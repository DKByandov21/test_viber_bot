from flask import Blueprint, g, jsonify, request

from viberbot.auth import require_admin, require_session
from viberbot.db import OtpCode, Session, User, db

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.route("", methods=["GET"])
@require_session
@require_admin
def list_users():
    users = User.query.order_by(User.created_at.asc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@bp.route("/<int:user_id>", methods=["PUT"])
@require_session
@require_admin
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    data = request.json or {}
    role = data.get("role")
    if role not in ("admin", "agent"):
        return jsonify({"status": "error", "message": "'role' must be 'admin' or 'agent'"}), 400

    user.role = role
    db.session.commit()
    return jsonify(user.to_dict()), 200


@bp.route("/<int:user_id>", methods=["DELETE"])
@require_session
@require_admin
def delete_user(user_id):
    if user_id == g.user.id:
        return jsonify({"status": "error", "message": "Не можеш да изтриеш собствения си акаунт"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    Session.query.filter_by(user_id=user_id).delete()
    OtpCode.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"status": "deleted", "id": user_id}), 200
