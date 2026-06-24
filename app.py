from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

INFOBIP_API_KEY = os.environ.get("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.environ.get("INFOBIP_BASE_URL")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """Ти си полезен асистент. Отговаряй кратко и ясно на български език, до 3-4 изречения. Не използвай markdown форматиране (без **, #, -, списъци) - само обикновен текст."""

VIBER_TEXT_LIMIT = 1000


def ask_groq(user_message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 250
    }
    print(f"Calling Groq with model: {GROQ_MODEL}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Groq status: {response.status_code}")
    print(f"Groq response: {response.text}")
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    return reply[:VIBER_TEXT_LIMIT]


REPLY_BUTTONS = [
    {"type": "REPLY", "text": "Друг въпрос", "postbackData": "ANOTHER_QUESTION"},
    {"type": "REPLY", "text": "Край", "postbackData": "END_CHAT"}
]


VIBER_BOT_SENDER = "pa:6060271498432636599"


def send_viber_bot_message(to, text, buttons=None):
    url = f"https://{INFOBIP_BASE_URL}/messages-api/1/messages"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    content = {
        "body": {
            "text": text,
            "type": "TEXT"
        }
    }
    if buttons:
        content["buttons"] = buttons

    payload = {
        "messages": [
            {
                "channel": "VIBER_BOT",
                "sender": VIBER_BOT_SENDER,
                "destinations": [{"to": to}],
                "content": content
            }
        ]
    }
    print(f"Sending to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Viber status: {response.status_code}")
    print(f"Viber response: {response.text}")
    return response.status_code


def send_template_notification(to, template_name, language, placeholders=None):
    url = f"https://{INFOBIP_BASE_URL}/messages-api/1/messages"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {"type": "TEXT"}
    if placeholders:
        body.update(placeholders)

    payload = {
        "messages": [
            {
                "channel": "VIBER_BM",
                "sender": "TCP",
                "destinations": [{"to": to}],
                "template": {
                    "templateName": template_name,
                    "language": language
                },
                "content": {
                    "body": body
                }
            }
        ]
    }
    print(f"Sending template '{template_name}' to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Viber status: {response.status_code}")
    print(f"Viber response: {response.text}")
    return response.status_code, response.text


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    try:
        results = data.get("results", [])
        for msg in results:
            sender = msg.get("sender") or msg.get("from")
            content = msg.get("content")
            if isinstance(content, list) and content:
                text = content[0].get("text", "")
            else:
                text = msg.get("message", {}).get("text", "")
            print(f"From: {sender}, Text: {text}")
            if sender and text:
                ai_reply = ask_groq(text)
                send_viber_bot_message(sender, ai_reply, buttons=REPLY_BUTTONS)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    return jsonify({"status": "ok"}), 200


@app.route("/notify", methods=["POST"])
def notify():
    data = request.json or {}
    to = data.get("to")
    placeholders = data.get("placeholders")

    if not to:
        return jsonify({"status": "error", "message": "'to' is required"}), 400

    status, response_text = send_template_notification(
        to=to,
        template_name="euromaster",
        language="bg",
        placeholders=placeholders
    )

    return jsonify({"status": "sent", "infobip_status": status, "infobip_response": response_text}), 200


@app.route("/", methods=["GET"])
def health():
    return "Bot is running!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
