from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from typing import Type
from .config import Config


db = SQLAlchemy()


def create_app(config_class: Type[Config] = Config) -> Flask:
    """
    Creates and configures the Flask application.

    This function initializes the Flask app, sets up the database configuration, 
    and registers the routes. It also initializes database migrations using Flask-Migrate.

    Args:
        config_class (Type[Config], optional): The configuration class to use for the app. 
        Defaults to the Config class from the config module.

    Returns:
        Flask: The initialized Flask application instance.
    """
    app = Flask(__name__)

    app.config.from_object(config_class)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/movies_db'

    db.init_app(app)

    from .routes import register_routes
    register_routes(app, db)

    migrate = Migrate(app, db)

    return app
