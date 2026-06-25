import os

from flask import Flask, jsonify, request

import config
from auth import require_api_key
from groq_client import remember_notification
from infobip_client import send_template_notification, send_viber_bot_message
from webhook_handlers import handle_button_reply, handle_text_message, parse_inbound_message

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    try:
        for msg in data.get("results", []):
            sender, channel, content_type, text, button_payload = parse_inbound_message(msg)

            if content_type == "BUTTON_REPLY":
                print(f"From: {sender}, Channel: {channel}, Button: {button_payload}")
                handle_button_reply(sender, channel, button_payload)
                continue

            print(f"From: {sender}, Channel: {channel}, Text: {text}")
            if sender and text:
                handle_text_message(sender, channel, text)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    return jsonify({"status": "ok"}), 200


@app.route("/notify", methods=["POST"])
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


@app.route("/agent-reply", methods=["POST"])
@require_api_key
def agent_reply():
    data = request.json or {}
    to = data.get("to")
    text = data.get("text")
    release_agent_mode = data.get("release_agent_mode", False)

    if not to or not text:
        return jsonify({"status": "error", "message": "'to' and 'text' are required"}), 400

    if release_agent_mode:
        config.AGENT_MODE_USERS.discard(to)
    else:
        config.AGENT_MODE_USERS.add(to)

    status = send_viber_bot_message(to, text)
    return jsonify({"status": "sent", "infobip_status": status}), 200


@app.route("/", methods=["GET"])
def health():
    return "Bot is running!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
