from flask import Blueprint

bp = Blueprint("health", __name__)


@bp.route("/", methods=["GET"])
def health():
    return "Bot is running!", 200
