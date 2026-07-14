import os

from flask import Blueprint, send_file, send_from_directory

from viberbot import config

bp = Blueprint("dashboard_spa", __name__)

# Resolve once at import time so path-traversal checks are reliable.
DIST_DIR = os.path.realpath(os.path.join(config.BASE_DIR, "dashboard", "dist"))
_DIST_PREFIX = DIST_DIR + os.sep


@bp.route("/dashboard")
@bp.route("/dashboard/")
@bp.route("/dashboard/<path:path>")
def serve_dashboard(path=""):
    if path:
        candidate = os.path.realpath(os.path.join(DIST_DIR, path))
        # Only serve files that are actually inside DIST_DIR (blocks traversal).
        if candidate.startswith(_DIST_PREFIX) and os.path.isfile(candidate):
            return send_file(candidate)
    return send_from_directory(DIST_DIR, "index.html")
