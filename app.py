import os
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# importa desde el paquete agendaback
from models import db
from routes.auth import auth_bp
from routes.prospect import prospect_bp
from routes.appointment import appointment_bp
from routes.call import call_bp
from routes.history import history_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    CORS(app, resources={r"/*": {"origins": "*"}})
    JWTManager(app)

    db.init_app(app)
    Migrate(app, db)

    if app.config.get("ENV") == "development":
        with app.app_context():
            if not os.path.exists("migrations"):
                init()
            migrate(message="auto migration", autogenerate=True)
            upgrade()

    # registra blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(prospect_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(call_bp)
    app.register_blueprint(history_bp)

    @app.route("/ping")
    def ping():
        return {"msg": "pong"}

    return app

if __name__ == "__main__":
    create_app().run(debug=True)
