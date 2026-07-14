from flask import Blueprint, g, jsonify, request

from viberbot.auth import require_session
from viberbot.services.auth_service import AuthError, register, start_login, update_profile, verify_otp

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.route("/register", methods=["POST"])
def register_route():
    data = request.json or {}
    email, password, phone = data.get("email"), data.get("password"), data.get("phone")
    if not email or not password or not phone:
        return jsonify({"status": "error", "message": "'email', 'password' and 'phone' are required"}), 400

    try:
        user = register(email, password, phone)
    except AuthError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    return jsonify({"status": "registered", "user": user.to_dict()}), 201


@bp.route("/login", methods=["POST"])
def login_route():
    data = request.json or {}
    email, password = data.get("email"), data.get("password")
    if not email or not password:
        return jsonify({"status": "error", "message": "'email' and 'password' are required"}), 400

    channel = data.get("channel", "viber")
    if channel not in ("viber", "sms", "voice", "email"):
        return jsonify({"status": "error", "message": "Невалиден канал. Позволени: viber, sms, voice, email"}), 400

    try:
        otp_id = start_login(email, password, channel=channel)
    except AuthError as e:
        return jsonify({"status": "error", "message": str(e)}), 401

    return jsonify({"status": "otp_sent", "otp_id": otp_id}), 200


@bp.route("/verify", methods=["POST"])
def verify_route():
    data = request.json or {}
    otp_id, code = data.get("otp_id"), data.get("code")
    if not otp_id or not code:
        return jsonify({"status": "error", "message": "'otp_id' and 'code' are required"}), 400

    try:
        token, user = verify_otp(otp_id, code)
    except AuthError as e:
        return jsonify({"status": "error", "message": str(e)}), 401

    return jsonify({"status": "ok", "token": token, "user": user.to_dict()}), 200


@bp.route("/me", methods=["GET"])
@require_session
def me_route():
    return jsonify(g.user.to_dict()), 200


@bp.route("/me", methods=["PUT"])
@require_session
def update_me_route():
    data = request.json or {}
    try:
        user = update_profile(
            g.user,
            phone=data.get("phone"),
            current_password=data.get("current_password"),
            new_password=data.get("new_password"),
        )
    except AuthError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    return jsonify(user.to_dict()), 200
