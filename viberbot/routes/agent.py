from flask import Blueprint, jsonify, request

from viberbot.auth import require_session
from viberbot.services import state
from viberbot.services.infobip_client import send_viber_bot_message

bp = Blueprint("agent", __name__)


@bp.route("/agent-reply", methods=["POST"])
@require_session
def agent_reply():
    data = request.json or {}
    to = data.get("to")
    text = data.get("text")
    release_agent_mode = data.get("release_agent_mode", False)

    if not to or not text:
        return jsonify({"status": "error", "message": "'to' and 'text' are required"}), 400

    state.set_agent_mode(to, not release_agent_mode)

    status = send_viber_bot_message(to, text)
    return jsonify({"status": "sent", "infobip_status": status}), 200
