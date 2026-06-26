from viberbot import config
from viberbot.services import state
from viberbot.services.groq_client import ask_groq
from viberbot.services.infobip_client import reply_on_same_channel, send_sms_notification


KNOWN_BUTTON_PAYLOADS = {"CONTACT_AGENT", "END_CHAT", "ANOTHER_QUESTION"}


def parse_inbound_message(msg):
    """Normalizes the two inbound shapes Infobip sends us:
    legacy VBM ({"from", "message": {"text"}}) and the VIBER_BOT MO event
    ({"sender", "channel", "content": [{"type", "text"}]}).

    Button clicks are sometimes delivered as a structured BUTTON_REPLY content
    item, but Viber Bot quick replies often just arrive as plain TEXT whose
    content is the button's postbackData verbatim - so we also recognize that."""
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

    if not button_payload and text in KNOWN_BUTTON_PAYLOADS:
        content_type = "BUTTON_REPLY"
        button_payload = text

    return sender, channel, content_type, text, button_payload


def handle_button_reply(sender, channel, payload):
    state.set_channel(sender, channel)
    state.ensure_fresh_session(sender)

    if payload == "CONTACT_AGENT":
        state.set_agent_mode(sender, True)
        send_sms_notification(config.AGENT_NOTIFY_PHONE, f"Клиент {sender} иска да говори с агент във Viber бота.")
        reply_on_same_channel(channel, sender, "Свързваме те с агент. Очаквай отговор скоро!")
    elif payload == "END_CHAT":
        state.clear_conversation(sender)
        reply_on_same_channel(channel, sender, "Разговорът приключи. Пиши ми пак, когато имаш въпрос!")
    elif payload == "ANOTHER_QUESTION":
        reply_on_same_channel(channel, sender, "Питай ме нещо за Infobip!")


def handle_text_message(sender, channel, text):
    state.set_channel(sender, channel)
    state.ensure_fresh_session(sender)

    if state.is_agent_mode(sender):
        # Customer already got the "we're connecting you" notice when they
        # hit Contact Agent - just log what they say so the agent sees it,
        # no need to repeat the notice on every message.
        state.append_user_message(sender, text)
        return

    ai_reply = ask_groq(sender, text)
    reply_on_same_channel(channel, sender, ai_reply)
