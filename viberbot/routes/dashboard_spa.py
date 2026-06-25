import os

from flask import Blueprint, send_from_directory

from viberbot import config

bp = Blueprint("dashboard_spa", __name__)

DIST_DIR = os.path.join(config.BASE_DIR, "dashboard", "dist")


@bp.route("/dashboard")
@bp.route("/dashboard/")
@bp.route("/dashboard/<path:path>")
def serve_dashboard(path=""):
    full_path = os.path.join(DIST_DIR, path) if path else None
    if full_path and os.path.isfile(full_path):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, "index.html")
