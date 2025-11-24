from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
import os

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Configure basic logging to stdout for better diagnostics in container
    import logging
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Token revocation (blocklist) check
    from app.services.auth_service import AuthService

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get('jti')
        if not jti:
            return True
        auth_service = AuthService()
        return auth_service.is_token_revoked(jti)

    # Configure CORS
    # In development allow all localhost origins to simplify running frontend on different ports.
    # In production use explicit origins from env `CORS_ORIGINS`.
    if app.config.get('TESTING') or os.getenv('FLASK_ENV', '').lower() == 'development' or app.config.get('ENV') == 'development':
        # Allow localhost origins and support credentials for dev convenience
        CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    else:
        CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(','))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    # face routes depend on native dlib/face-recognition libs which may not be
    # available in all dev environments. Import defensively so the app can
    # start without those native deps when needed.
    try:
        from app.routes.face import face_bp
    except Exception as e:
        app.logger.warning('Face routes disabled: %s', str(e))
        face_bp = None
    from app.routes.attendance import attendance_bp
    from app.routes.statistics import statistics_bp
    from app.routes.admin import admin_bp
    from app.routes.health import health_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    if face_bp:
        app.register_blueprint(face_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(health_bp)

    # Register error handlers
    from app.middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    return app
