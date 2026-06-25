from flask import Blueprint, jsonify, request

from viberbot import config
from viberbot.auth import require_api_key
from viberbot.services.groq_client import remember_notification
from viberbot.services.infobip_client import send_template_notification

bp = Blueprint("notify", __name__)


@bp.route("/notify", methods=["POST"])
@require_api_key
def notify():
    data = request.json or {}
    to = data.get("to")
    placeholders = data.get("placeholders")
    context_summary = data.get("context_summary")

    if not to:
        return jsonify({"status": "error", "message": "'to' is required"}), 400

    template_key = data.get("template")
    if template_key:
        template = config.TEMPLATES.get(template_key)
        if not template:
            return jsonify({
                "status": "error",
                "message": f"Unknown template '{template_key}'. Known: {list(config.TEMPLATES.keys())}"
            }), 400
        template_name, language = template["id"], template["language"]
    else:
        template_name = data.get("template_name", "euromaster")
        language = data.get("language", "bg")

    status, response_text = send_template_notification(
        to=to, template_name=template_name, language=language, placeholders=placeholders
    )
    remember_notification(to, context_summary)

    return jsonify({"status": "sent", "infobip_status": status, "infobip_response": response_text}), 200
