from viberbot import config
from viberbot.services import state
from viberbot.services.groq_client import ask_groq
from viberbot.services.infobip_client import reply_on_same_channel, send_sms_notification


KNOWN_BUTTON_PAYLOADS = {"CONTACT_AGENT", "END_CHAT", "ANOTHER_QUESTION"}

# Keyword triggers for channels that don't support interactive buttons (e.g. VBM).
# Matched against the full lowercased, stripped message text.
_AGENT_KEYWORDS = {"агент", "оператор", "служител", "жив човек", "iskam agent", "agent"}
_END_CHAT_KEYWORDS = {"край", "стоп", "довиждане", "end", "stop"}


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
        channel_label = "VBM" if channel == "VIBER_BM" else "Viber Bot"
        send_sms_notification(
            config.AGENT_NOTIFY_PHONE,
            f"Клиент {sender} иска да говори с агент ({channel_label}). Отговори от dashboard-а.",
        )
        notice = "Свързваме те с агент. Очаквай отговор скоро!"
        reply_on_same_channel(channel, sender, notice)
        state.append_assistant_note(sender, notice)
    elif payload == "END_CHAT":
        state.clear_conversation(sender)
        reply_on_same_channel(channel, sender, "Разговорът приключи. Пиши ми пак, когато имаш въпрос!")
    elif payload == "ANOTHER_QUESTION":
        reply_on_same_channel(channel, sender, "Питай ме нещо за Infobip!")


def _keyword_match(text, keywords):
    normalized = text.lower().strip()
    return any(kw in normalized for kw in keywords)


def handle_text_message(sender, channel, text):
    state.set_channel(sender, channel)
    state.ensure_fresh_session(sender)

    if state.is_agent_mode(sender):
        # Customer already got the "we're connecting you" notice when they
        # hit Contact Agent - just log what they say so the agent sees it.
        state.append_user_message(sender, text)
        return

    # Keyword-based agent handoff — primary path for VBM (no interactive buttons),
    # but works as a fallback on any channel. The trigger message itself must land
    # in history too, so the agent sees what the customer actually wrote.
    if _keyword_match(text, _AGENT_KEYWORDS):
        state.append_user_message(sender, text)
        handle_button_reply(sender, channel, "CONTACT_AGENT")
        return

    if _keyword_match(text, _END_CHAT_KEYWORDS):
        state.append_user_message(sender, text)
        handle_button_reply(sender, channel, "END_CHAT")
        return

    ai_reply = ask_groq(sender, text, channel)
    if channel == "VIBER_BM":
        # VBM has no quick-reply buttons, so every reply carries the agent hint.
        # Trim the AI part if needed so the combined text stays within the limit.
        max_reply = config.VIBER_TEXT_LIMIT - len(config.VBM_AGENT_HINT) - 2
        ai_reply = f"{ai_reply[:max_reply]}\n\n{config.VBM_AGENT_HINT}"
    reply_on_same_channel(channel, sender, ai_reply)
