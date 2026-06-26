from functools import wraps

from flask import g, jsonify, request


def require_session(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        from viberbot.services.auth_service import get_user_from_token

        token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        user = get_user_from_token(token)
        if not user:
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
        g.user = user
        return view(*args, **kwargs)
    return wrapped


def require_admin(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not getattr(g, "user", None) or g.user.role != "admin":
            return jsonify({"status": "error", "message": "Admin access required"}), 403
        return view(*args, **kwargs)
    return wrapped
