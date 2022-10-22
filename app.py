from flask import Flask, render_template, request, abort
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from marshmallow import ValidationError
from flask_cors import CORS
from db import setup_db
from config import ProductionConfig
import db.schemas as schemas
import db.models as models


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

    @app.post("/api/login")
    def login():
        data = schemas.login_schema.load(request.json)
        admin = models.Admin.query.filter_by(email=data['email']).one_or_none()
        if not admin or not admin.checkpw(data['password']):
            return abort(422, "Email or password is not correct.")

        return {"data": schemas.admin_schema.dump(admin), "token": create_access_token(admin.id)}

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
