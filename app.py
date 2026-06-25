from flask import Flask, request, jsonify
import requests
import os
import re
import glob

app = Flask(__name__)

INFOBIP_API_KEY = os.environ.get("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.environ.get("INFOBIP_BASE_URL")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """Ти си помощник, специализиран в Infobip API и услуги (SMS, Viber, WhatsApp, Email, 2FA, Messages API).
Отговаряй кратко и ясно на български език, до 3-4 изречения. Не използвай markdown форматиране (без **, #, -, списъци) - само обикновен текст.
Ако ти е предоставен контекст от документация по-долу, базирай отговора си на него. Ако контекстът не съдържа отговора, кажи че не си сигурен."""

VIBER_TEXT_LIMIT = 1000
KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")

CONVERSATIONS = {}
MAX_HISTORY_MESSAGES = 10
AGENT_NOTIFY_PHONE = "359876888400"
AGENT_MODE_USERS = set()


def load_knowledge_chunks():
    chunks = []
    for path in glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md")):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        sections = re.split(r"\n(?=#{1,3} )", content)
        for section in sections:
            section = section.strip()
            if section:
                chunks.append(section)
    return chunks


KNOWLEDGE_CHUNKS = load_knowledge_chunks()
print(f"Loaded {len(KNOWLEDGE_CHUNKS)} knowledge chunks")


def find_relevant_chunks(query, top_n=3):
    query_words = set(re.findall(r"\w+", query.lower()))
    if not query_words:
        return []

    scored = []
    for chunk in KNOWLEDGE_CHUNKS:
        chunk_words = set(re.findall(r"\w+", chunk.lower()))
        overlap = len(query_words & chunk_words)
        if overlap > 0:
            scored.append((overlap, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:top_n]]


def ask_groq(sender, user_message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    relevant_chunks = find_relevant_chunks(user_message)
    if relevant_chunks:
        context = "\n\n---\n\n".join(relevant_chunks)
        user_content = f"Контекст от Infobip документация:\n{context}\n\nВъпрос: {user_message}"
    else:
        user_content = user_message

    history = CONVERSATIONS.get(sender, [])
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_content}]

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 250
    }
    print(f"Calling Groq with model: {GROQ_MODEL}, with {len(relevant_chunks)} knowledge chunks, {len(history)} history messages")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Groq status: {response.status_code}")
    print(f"Groq response: {response.text}")
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    reply = reply[:VIBER_TEXT_LIMIT]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    CONVERSATIONS[sender] = history[-MAX_HISTORY_MESSAGES:]

    return reply


REPLY_BUTTONS = [
    {"type": "REPLY", "text": "Друг въпрос", "postbackData": "ANOTHER_QUESTION"},
    {"type": "REPLY", "text": "Свържи се с агент", "postbackData": "CONTACT_AGENT"},
    {"type": "OPEN_URL", "text": "Сайт на Infobip", "url": "https://www.infobip.com"},
    {"type": "REPLY", "text": "Край", "postbackData": "END_CHAT"}
]


VIBER_BOT_SENDER = "pa:6060271498432636599"
VBM_SENDER = "TCP"


def send_viber_message(channel, sender, to, text, buttons=None):
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
                "channel": channel,
                "sender": sender,
                "destinations": [{"to": to}],
                "content": content
            }
        ]
    }
    print(f"Sending {channel} message to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Viber status: {response.status_code}")
    print(f"Viber response: {response.text}")
    return response.status_code


def send_viber_bot_message(to, text, buttons=None):
    return send_viber_message("VIBER_BOT", VIBER_BOT_SENDER, to, text, buttons=buttons)


def reply_on_same_channel(channel, to, text):
    """Reply via the channel the inbound message came in on.
    VIBER_BM doesn't render ad-hoc buttons (only template-defined ones), so buttons are
    only attached for VIBER_BOT replies."""
    if channel == "VIBER_BM":
        return send_viber_message("VIBER_BM", VBM_SENDER, to, text)
    return send_viber_message("VIBER_BOT", VIBER_BOT_SENDER, to, text, buttons=REPLY_BUTTONS)


def send_sms_notification(to, text):
    url = f"https://{INFOBIP_BASE_URL}/sms/2/text/advanced"
    headers = {
        "Authorization": f"App {INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {
                "destinations": [{"to": to}],
                "text": text
            }
        ]
    }
    print(f"Sending SMS notification to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"SMS status: {response.status_code}")
    print(f"SMS response: {response.text}")
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
            channel = msg.get("channel")
            content = msg.get("content")
            has_content_list = isinstance(content, list) and content
            item = content[0] if has_content_list else {}
            content_type = item.get("type", "TEXT") if has_content_list else None

            if channel is None:
                channel = "VIBER_BOT" if has_content_list else "VIBER_BM"

            if content_type == "BUTTON_REPLY":
                payload = item.get("payload")
                print(f"From: {sender}, Channel: {channel}, Button: {payload}")
                if payload == "CONTACT_AGENT":
                    AGENT_MODE_USERS.add(sender)
                    send_sms_notification(
                        AGENT_NOTIFY_PHONE,
                        f"Клиент {sender} иска да говори с агент във Viber бота."
                    )
                    reply_on_same_channel(channel, sender, "Свързваме те с агент. Очаквай отговор скоро!")
                elif payload == "END_CHAT":
                    CONVERSATIONS.pop(sender, None)
                    AGENT_MODE_USERS.discard(sender)
                    reply_on_same_channel(channel, sender, "Разговорът приключи. Пиши ми пак, когато имаш въпрос!")
                elif payload == "ANOTHER_QUESTION":
                    reply_on_same_channel(channel, sender, "Питай ме нещо за Infobip!")
                continue

            text = item.get("text", "") if has_content_list else msg.get("message", {}).get("text", "")
            print(f"From: {sender}, Channel: {channel}, Text: {text}")
            if not (sender and text):
                continue

            if sender in AGENT_MODE_USERS:
                reply_on_same_channel(channel, sender, "Агентът е известен и ще ти отговори скоро.")
                continue

            ai_reply = ask_groq(sender, text)
            reply_on_same_channel(channel, sender, ai_reply)

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


@app.route("/agent-reply", methods=["POST"])
def agent_reply():
    data = request.json or {}
    to = data.get("to")
    text = data.get("text")
    release_agent_mode = data.get("release_agent_mode", False)

    if not to or not text:
        return jsonify({"status": "error", "message": "'to' and 'text' are required"}), 400

    if release_agent_mode:
        AGENT_MODE_USERS.discard(to)
    else:
        AGENT_MODE_USERS.add(to)

    status = send_viber_bot_message(to, text)
    return jsonify({"status": "sent", "infobip_status": status}), 200


@app.route("/", methods=["GET"])
def health():
    return "Bot is running!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
