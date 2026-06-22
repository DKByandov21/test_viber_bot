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


def send_viber_message(to, text):
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
    print(f"Sending to Viber: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Viber send status: {response.status_code}")
    print(f"Viber send response: {response.text}")
    return response.status_code


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    try:
        results = data.get("results", [])
        for msg in results:
            sender = msg.get("from")
            text = msg.get("message", {}).get("text", "")

            if sender and text:
                print(f"Processing message from {sender}: {text}")
                ai_reply = ask_groq(text)
                print(f"AI reply: {ai_reply}")
                send_viber_message(sender, ai_reply)

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
