from flask import Blueprint, jsonify, request

from viberbot.auth import require_session
from viberbot.services import state
from viberbot.services.infobip_client import reply_on_same_channel

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

    channel = state.get_channel(to)

    status = reply_on_same_channel(channel, to, text)
    state.append_agent_message(to, text)

    if release_agent_mode:
        state.set_agent_mode(to, False)
        notice = "Вече си обратно при AI асистента - можеш да продължиш да задаваш въпроси."
        reply_on_same_channel(channel, to, notice)
        state.append_assistant_note(to, notice)
    else:
        state.set_agent_mode(to, True)

    return jsonify({"status": "sent", "infobip_status": status}), 200
