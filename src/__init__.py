"""Flask app config and initialization"""
import logging.config

from flask import Flask


def create_app(config_obj=None):
    """Sets config from passed in config object,
    initializes Flask modules, registers blueprints (routes)

    Args:
        config_obj (class): config class to apply to app

    Returns:
        app: configured and initialized Flask app object

    """
    app = Flask(__name__, static_folder=None)

    if not config_obj:
        logging.warning(
            "No config specified; defaulting to development"
        )
        import config
        config_obj = config.DevelopmentConfig

    app.config.from_object(config_obj)

    from src.models.base import db, migrate
    db.init_app(app)
    db.app = app

    with app.app_context():
        if app.config["FLASK_ENV"] == 'development':
            migrate.init_app(app, db, render_as_batch=True)
        else:
    migrate.init_app(app, db)

    from src.routes import register_routes
    register_routes(app)

    return app
