from flask import Blueprint, jsonify, request

from viberbot.auth import require_admin, require_session
from viberbot.services import state
from viberbot.services.groq_client import remember_notification
from viberbot.services.infobip_client import send_raw_message, send_template_notification

bp = Blueprint("notify", __name__)


@bp.route("/notify", methods=["POST"])
@require_session
@require_admin
def notify():
    data = request.json or {}
    to = data.get("to")
    placeholders = data.get("placeholders")
    context_summary = data.get("context_summary")

    if not to:
        return jsonify({"status": "error", "message": "'to' is required"}), 400

    template_key = data.get("template")
    if template_key:
        template = state.get_template(template_key)
        if not template:
            known = [t["key"] for t in state.list_templates()]
            return jsonify({
                "status": "error",
                "message": f"Unknown template '{template_key}'. Known: {known}"
            }), 400
        template_name, language = template["id"], template["language"]
    else:
        template_name = data.get("template_name", "euromaster")
        language = data.get("language", "bg")

    status, response_text = send_template_notification(
        to=to, template_name=template_name, language=language, placeholders=placeholders
    )
    # Without a stored summary the VBM AI has no idea what notification the
    # customer is replying to - fall back to template name + placeholder values.
    if not context_summary:
        details = ", ".join(f"{k}: {v}" for k, v in (placeholders or {}).items() if k != "type")
        context_summary = f"Изпратено известие по template '{template_name}'"
        if details:
            context_summary += f" с данни: {details}"
        context_summary += "."
    remember_notification(to, context_summary)

    return jsonify({"status": "sent", "infobip_status": status, "infobip_response": response_text}), 200


@bp.route("/notify/bulk", methods=["POST"])
@require_session
@require_admin
def notify_bulk():
    data = request.json or {}
    template_key = data.get("template")
    to_list = data.get("to_list", [])
    placeholders = data.get("placeholders", {})

    if not template_key:
        return jsonify({"status": "error", "message": "'template' is required"}), 400
    if not to_list or not isinstance(to_list, list):
        return jsonify({"status": "error", "message": "'to_list' must be a non-empty list"}), 400
    if len(to_list) > 200:
        return jsonify({"status": "error", "message": "Maximum 200 recipients per bulk send"}), 400

    template = state.get_template(template_key)
    if not template:
        known = [t["key"] for t in state.list_templates()]
        return jsonify({"status": "error", "message": f"Unknown template '{template_key}'. Known: {known}"}), 400

    results = []
    for to in to_list:
        to = str(to).strip()
        if not to:
            continue
        try:
            status, _ = send_template_notification(
                to=to,
                template_name=template["id"],
                language=template["language"],
                placeholders=placeholders or None,
            )
            results.append({"to": to, "status": status, "ok": status == 200})
        except Exception as exc:
            results.append({"to": to, "status": 0, "ok": False, "error": str(exc)})

    sent = sum(1 for r in results if r["ok"])
    return jsonify({"results": results, "sent": sent, "failed": len(results) - sent}), 200


@bp.route("/notify/raw", methods=["POST"])
@require_session
@require_admin
def notify_raw():
    message = request.json
    if not isinstance(message, dict) or not message:
        return jsonify({"status": "error", "message": "Request body must be a JSON message object"}), 400

    status, response_text = send_raw_message(message)

    # Raw sends are how the dashboard Notify page delivers templates - store a
    # context summary per recipient so the VBM AI can answer about the message.
    if status == 200:
        summary = _summarize_raw_message(message)
        if summary:
            for dest in message.get("destinations", []):
                to = dest.get("to")
                if to:
                    remember_notification(str(to), summary)

    return jsonify({"status": "sent", "infobip_status": status, "infobip_response": response_text}), 200


def _summarize_raw_message(message):
    template = message.get("template") or {}
    template_name = template.get("templateName")
    if not template_name:
        return None
    body = (message.get("content") or {}).get("body") or {}
    details = ", ".join(f"{k}: {v}" for k, v in body.items() if k != "type")
    summary = f"Изпратено известие по template '{template_name}'"
    if details:
        summary += f" с данни: {details}"
    return summary + "."
