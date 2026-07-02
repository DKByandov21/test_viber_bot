from flask import Blueprint, jsonify, request

from viberbot.auth import require_admin, require_session
from viberbot.db import VoiceTemplate, db
from viberbot.services.infobip_client import send_voice_call

bp = Blueprint("voice", __name__, url_prefix="/api/voice")


@bp.route("/call", methods=["POST"])
@require_session
@require_admin
def voice_call():
    data = request.json or {}
    to = data.get("to")
    text = data.get("text")

    if not to or not text:
        return jsonify({"status": "error", "message": "'to' and 'text' are required"}), 400

    language = data.get("language", "bg")
    speech_rate = float(data.get("speech_rate", 0.9))
    speech_rate = max(0.5, min(2.0, speech_rate))
    gender = data.get("gender")
    pause = data.get("pause")
    if pause is not None:
        pause = max(0, min(10, int(pause)))

    status, response_text = send_voice_call(to, text, language, speech_rate, gender=gender, pause=pause)
    return jsonify({"status": "sent", "infobip_status": status, "infobip_response": response_text}), 200


@bp.route("/templates", methods=["GET"])
@require_session
@require_admin
def list_voice_templates():
    templates = VoiceTemplate.query.order_by(VoiceTemplate.created_at.desc()).all()
    return jsonify([t.to_dict() for t in templates])


@bp.route("/templates", methods=["POST"])
@require_session
@require_admin
def create_voice_template():
    data = request.json or {}
    name = data.get("name", "").strip()
    text = data.get("text", "").strip()
    if not name or not text:
        return jsonify({"status": "error", "message": "'name' and 'text' are required"}), 400

    t = VoiceTemplate(
        name=name,
        text=text,
        language=data.get("language", "bg"),
        gender=data.get("gender") or None,
        speech_rate=float(data.get("speech_rate", 0.9)),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201


@bp.route("/templates/<int:template_id>", methods=["DELETE"])
@require_session
@require_admin
def delete_voice_template(template_id):
    t = VoiceTemplate.query.get_or_404(template_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"status": "deleted"})
