import config
from groq_client import ask_groq
from infobip_client import reply_on_same_channel, send_sms_notification


def parse_inbound_message(msg):
    """Normalizes the two inbound shapes Infobip sends us:
    legacy VBM ({"from", "message": {"text"}}) and the VIBER_BOT MO event
    ({"sender", "channel", "content": [{"type", "text"}]})."""
    sender = msg.get("sender") or msg.get("from")
    channel = msg.get("channel")
    content = msg.get("content")
    has_content_list = isinstance(content, list) and content
    item = content[0] if has_content_list else {}
    content_type = item.get("type", "TEXT") if has_content_list else None

    if channel is None:
        channel = "VIBER_BOT" if has_content_list else "VIBER_BM"

    text = item.get("text", "") if has_content_list else msg.get("message", {}).get("text", "")
    button_payload = item.get("payload") if content_type == "BUTTON_REPLY" else None

    return sender, channel, content_type, text, button_payload


def handle_button_reply(sender, channel, payload):
    if payload == "CONTACT_AGENT":
        config.AGENT_MODE_USERS.add(sender)
        send_sms_notification(config.AGENT_NOTIFY_PHONE, f"Клиент {sender} иска да говори с агент във Viber бота.")
        reply_on_same_channel(channel, sender, "Свързваме те с агент. Очаквай отговор скоро!")
    elif payload == "END_CHAT":
        config.CONVERSATIONS.pop(sender, None)
        config.AGENT_MODE_USERS.discard(sender)
        reply_on_same_channel(channel, sender, "Разговорът приключи. Пиши ми пак, когато имаш въпрос!")
    elif payload == "ANOTHER_QUESTION":
        reply_on_same_channel(channel, sender, "Питай ме нещо за Infobip!")


def handle_text_message(sender, channel, text):
    if sender in config.AGENT_MODE_USERS:
        reply_on_same_channel(channel, sender, "Агентът е известен и ще ти отговори скоро.")
        return
    ai_reply = ask_groq(sender, text)
    reply_on_same_channel(channel, sender, ai_reply)
