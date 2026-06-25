from functools import wraps

from flask import jsonify, request

import config


def require_api_key(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not config.APP_API_KEY:
            return jsonify({"status": "error", "message": "APP_API_KEY not configured on server"}), 500
        if request.headers.get("X-API-Key") != config.APP_API_KEY:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
        return view(*args, **kwargs)
    return wrapped
