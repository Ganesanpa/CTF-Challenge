from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # or use app.config['SQLALCHEMY_DATABASE_URI'] = ...

    db.init_app(app)

    with app.app_context():
        from models import User, Challenge, Submission  # ensure models are loaded
        db.create_all()

    return app
