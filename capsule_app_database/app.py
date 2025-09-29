from flask import Flask
from config import Config
from extensions import db, migrate, jwt, make_celery




def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)


# extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


# register blueprints
    from routes.messages import bp as messages_bp
    from routes.documents import bp as documents_bp
    from routes.consent import bp as consent_bp


    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(consent_bp, url_prefix='/api/consent')


# create celery
    make_celery(app)


    return app
app = create_app()