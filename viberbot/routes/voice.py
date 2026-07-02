from flask import Blueprint, jsonify, request

from viberbot.auth import require_admin, require_session
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

    status, response_text = send_voice_call(to, text, language, speech_rate)
    return jsonify({"status": "sent", "infobip_status": status, "infobip_response": response_text}), 200
