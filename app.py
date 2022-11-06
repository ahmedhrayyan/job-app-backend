from os import path
from flask import Flask, render_template, request, abort
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, current_user
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from db import setup_db
from config import ProductionConfig
from utils.uploadcare import uploadcare
import db.schemas as schemas
import db.models as models
import utils.helpers as helpers


def paginate(query, page: int = 1, per_page: int = 15):
    """ Return a list of paginated items and a dict contains metadata """
    meta = {
        'total': query.count(),
        'current_page': page,
        'per_page': per_page,
    }
    return query.paginate(page=page, per_page=per_page), meta


def create_app(config=ProductionConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    setup_db(app)
    CORS(app)
    jwt = JWTManager(app)

    @jwt.token_verification_failed_loader
    def verification_failure(jwt_header, jwt_data):
        print(jwt_header, jwt_data)
        return {"message": "Account suspended"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        """ custom invalid token response """
        return {'message': error_string}, 401

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """ get current user from database """
        identity = jwt_data["sub"]
        return models.Admin.query.get(identity)

    @app.get('/')
    def index():
        return render_template("index.html")

    @app.post("/api/upload")
    @jwt_required(optional=True)
    def upload():
        if 'file' not in request.files:
            abort(400, "No file founded")
        file = request.files['file']

        if file.filename == '':
            abort(400, 'No selected file')
        file_ext = path.splitext(file.filename)[1][1:]
        if file_ext not in app.config['ALLOWED_EXTENSIONS']:
            abort(422, 'You cannot upload %s files' % file_ext)
        # set name on uploadcare cdn
        file.name = file.filename

        ucare_file = uploadcare.upload(file)

        return {'path': ucare_file.cdn_path()}

    @app.post("/api/register")
    def register():
        admin = schemas.admin_schema.load(request.json)
        try:
            admin.insert()
        except IntegrityError as e:
            abort(422, helpers.parse_integrity_error(e))

        return {"data": schemas.admin_schema.dump(admin), "token": create_access_token(admin.id)}

    @app.post("/api/login")
    def login():
        data = schemas.login_schema.load(request.json)
        admin = models.Admin.query.filter_by(email=data['email']).one_or_none()
        if not admin or not admin.checkpw(data['password']):
            return abort(422, "Email or password is not correct.")

        return {"data": schemas.admin_schema.dump(admin), "token": create_access_token(admin.id)}

    @app.get("/api/profile/jobs")
    @jwt_required()
    def get_profile_jobs():
        page = request.args.get("page", 1, int)
        jobs, meta = paginate(models.Job.query.filter_by(admin_id=current_user.id), page)
        return {"data": schemas.job_schema.dump(jobs, many=True), "meta": meta}

    @app.get("/api/jobs")
    def get_jobs():
        page = request.args.get("page", 1, int)
        jobs, meta = paginate(models.Job.query, page)
        return {"data": schemas.job_schema.dump(jobs, many=True), "meta": meta}

    @app.get("/api/jobs/<int:job_id>")
    def show_job(job_id):
        job = models.Job.query.get_or_404(job_id)
        return {"data": schemas.job_schema.dump(job)}

    @app.post("/api/jobs")
    @jwt_required(optional=True)
    def create_job():
        job = schemas.job_schema.load(request.json)
        job.insert()
        return {"data": schemas.job_schema.dump(job)}

    @app.delete("/api/jobs/<int:job_id>")
    @jwt_required()
    def delete_job(job_id):
        target = models.Job.query.get(job_id)
        if not target:
            abort(404)
        if target.admin_id != current_user.id:
            abort(403)

        target.delete()
        return {"message": "success"}

    # ---------- ERROR HANDLING ---------- #

    @app.errorhandler(ValidationError)
    def marshmallow_error_handler(error):
        return {'message': 'The given data was invalid.', 'errors': error.messages}, 400

    @app.errorhandler(Exception)
    def default_error_handler(error):
        # log error outside testing environment, useful for debugging
        if app.config['TESTING'] is not True:
            app.logger.exception(error)

        code = getattr(error, 'code', 500)
        message = getattr(error, 'description', "Something went wrong")

        return {'message': message}, code if isinstance(code, int) else 500

        # -------------- COMMANDS ------------------- #

    @app.cli.command('db_seed')
    def db_seed():
        admin = models.Admin(name="Admin", email="admin@admin.com", password="123456")
        admin.insert()
        print("Seed success.")

    return app
