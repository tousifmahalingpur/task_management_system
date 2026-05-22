from flask import Flask
from config import Config

from extensions import (
    db,
    bcrypt,
    login_manager
)

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    bcrypt.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from routes.auth_routes import auth
    from routes.task_routes import task

    app.register_blueprint(auth)

    app.register_blueprint(task)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)