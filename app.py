from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

INFOBIP_API_KEY = os.environ.get("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.environ.get("INFOBIP_BASE_URL")

def send_viber_bm_message(to, text):
    url = f"https://{INFOBIP_BASE_URL}/messages-api/1/messages"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "channel": "VIBER_BM",
                "sender": "TCP",
                "destinations": [{"to": to}],
                "content": {
                    "body": {
                        "text": text,
                        "type": "TEXT"
                    }
                }
            }
        ]
    }
    print(f"Sending to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Viber status: {response.status_code}")
    print(f"Viber response: {response.text}")
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
            print(f"From: {sender}, Text: {text}")
            if sender and text:
                send_viber_bm_message(sender, "Здравей! Ботът работи! 🤖")

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
