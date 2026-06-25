from flask import Flask


def create_app():
    app = Flask(__name__)

    from viberbot.routes.agent import bp as agent_bp
    from viberbot.routes.health import bp as health_bp
    from viberbot.routes.notify import bp as notify_bp
    from viberbot.routes.webhook import bp as webhook_bp

    app.register_blueprint(webhook_bp)
    app.register_blueprint(notify_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(health_bp)

    return app
