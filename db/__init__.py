from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def setup_db(app):
    """
    binds a flask application and a SQLAlchemy service
    :param app: Flask app instance
    """

    db.init_app(app)

    # do not use migrations in test environment
    if app.config['TESTING'] is True:
        db.create_all()
    else:
        Migrate(app, db, compare_type=True)
