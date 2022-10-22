from flask import Flask, render_template
from db import setup_db
from config import ProductionConfig


def create_app(config=ProductionConfig):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config)
    setup_db(app)

    @app.get('/')
    def index():
        return render_template("index.html")

    return app
