from flask import Blueprint, jsonify, request

from viberbot.handlers.webhook_handlers import handle_button_reply, handle_text_message, parse_inbound_message

bp = Blueprint("webhook", __name__)


@bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    for msg in data.get("results", []):
        try:
            sender, channel, content_type, text, button_payload = parse_inbound_message(msg)

            if content_type == "BUTTON_REPLY":
                print(f"From: {sender}, Channel: {channel}, Button: {button_payload}")
                handle_button_reply(sender, channel, button_payload)
                continue

            print(f"From: {sender}, Channel: {channel}, Text: {text}")
            if sender and text:
                handle_text_message(sender, channel, text)

        except Exception as e:
            print(f"Error processing message {msg}: {e}")
            import traceback
            traceback.print_exc()

    return jsonify({"status": "ok"}), 200
