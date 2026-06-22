from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

INFOBIP_API_KEY = os.environ.get("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.environ.get("INFOBIP_BASE_URL")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """Ти си полезен асистент. Отговаряй кратко и ясно на български език."""


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
        "max_tokens": 500
    }
    print(f"Calling Groq with model: {GROQ_MODEL}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Groq status: {response.status_code}")
    print(f"Groq response: {response.text}")
    data = response.json()
    return data["choices"][0]["message"]["content"]


def send_viber_bm_message(to, text):
    """Send message via Viber BM (TCP sender)"""
    url = f"https://{INFOBIP_BASE_URL}/viber/2/messages"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "channel": "VIBER",
                "sender": {"type": "VIBER_BM", "sender": "TCP"},
                "destinations": [{"to": to}],
                "content": {"body": {"type": "TEXT", "text": text}}
            }
        ]
    }
    print(f"Sending VBM to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Viber BM send status: {response.status_code}")
    print(f"Viber BM send response: {response.text}")
    return response.status_code


def send_viber_bot_message(to, text):
    """Send message via Viber Bot"""
    url = f"https://{INFOBIP_BASE_URL}/viber/2/messages"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "channel": "VIBER",
                "sender": {"type": "VIBER_BOT"},
                "destinations": [{"to": to}],
                "content": {"body": {"type": "TEXT", "text": text}}
            }
        ]
    }
    print(f"Sending Bot message to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Viber Bot send status: {response.status_code}")
    print(f"Viber Bot send response: {response.text}")
    return response.status_code


def parse_message(data):
    """Parse both VBM and Viber Bot message formats"""
    results = data.get("results", [])
    messages = []

    for msg in results:
        sender = None
        text = None
        msg_type = None

        # Viber Bot format (MO_MESSAGES_API_JSON)
        if "from" in msg and "message" in msg:
            sender = msg.get("from")
            text = msg.get("message", {}).get("text", "")
            msg_type = "bot"

        # VBM format (MO_OTT_MSISDN)
        elif "from" in msg:
            sender = msg.get("from")
            text = msg.get("text", "") or msg.get("message", {}).get("text", "")
            msg_type = "vbm"

        if sender and text:
            messages.append({"sender": sender, "text": text, "type": msg_type})

    return messages


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    try:
        messages = parse_message(data)

        for msg in messages:
            sender = msg["sender"]
            text = msg["text"]
            msg_type = msg["type"]

            print(f"Processing [{msg_type}] from {sender}: {text}")
            ai_reply = ask_groq(text)
            print(f"AI reply: {ai_reply}")

            if msg_type == "vbm":
                send_viber_bm_message(sender, ai_reply)
            else:
                send_viber_bot_message(sender, ai_reply)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    return jsonify({"status": "ok"}), 200


@app.route("/", methods=["GET"])
def health():
    return "Bot is running!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
