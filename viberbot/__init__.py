from flask import Flask
from flask_cors import CORS

from viberbot import config
from viberbot.db import init_db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    init_db(app)

    from viberbot.routes.agent import bp as agent_bp
    from viberbot.routes.auth import bp as auth_bp
    from viberbot.routes.dashboard_api import bp as dashboard_api_bp
    from viberbot.routes.dashboard_spa import bp as dashboard_spa_bp
    from viberbot.routes.health import bp as health_bp
    from viberbot.routes.knowledge import bp as knowledge_bp
    from viberbot.routes.notify import bp as notify_bp
    from viberbot.routes.projects import bp as projects_bp
    from viberbot.routes.users import bp as users_bp
    from viberbot.routes.voice import bp as voice_bp
    from viberbot.routes.webhook import bp as webhook_bp

    app.register_blueprint(webhook_bp)
    app.register_blueprint(notify_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_api_bp)
    app.register_blueprint(dashboard_spa_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(voice_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(health_bp)

    return app


