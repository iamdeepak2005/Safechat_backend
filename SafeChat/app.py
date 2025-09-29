from flask import Flask
from extensions import db
import config
from models.user import User
from models.file import File
from models.activity_log import FileActivityLog
from models.permission import FilePermission
from models.notifications import Notification
from models.capsule import Capsule
# ✅ Import blueprints
from routes.files import files_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    # Register routes
    app.register_blueprint(files_bp, url_prefix="/api")

    # ✅ Create all tables AFTER all models are imported
    with app.app_context():
        db.create_all()
        print("✅ All tables created successfully.")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
