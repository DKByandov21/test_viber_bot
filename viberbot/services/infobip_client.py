import requests

from viberbot import config


def send_viber_message(channel, sender, to, text, buttons=None):
    url = f"https://{config.INFOBIP_BASE_URL}/messages-api/1/messages"
    headers = {
        "Authorization": f"App {config.INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    content = {"body": {"text": text, "type": "TEXT"}}
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
    return send_viber_message("VIBER_BOT", config.VIBER_BOT_SENDER, to, text, buttons=buttons)


def reply_on_same_channel(channel, to, text):
    """Reply via the channel the inbound message came in on.
    VIBER_BM doesn't render ad-hoc buttons (only template-defined ones), so buttons are
    only attached for VIBER_BOT replies."""
    if channel == "VIBER_BM":
        return send_viber_message("VIBER_BM", config.VBM_SENDER, to, text)
    return send_viber_message("VIBER_BOT", config.VIBER_BOT_SENDER, to, text, buttons=config.REPLY_BUTTONS)


def send_sms_notification(to, text):
    url = f"https://{config.INFOBIP_BASE_URL}/sms/2/text/advanced"
    headers = {
        "Authorization": f"App {config.INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"messages": [{"destinations": [{"to": to}], "text": text}]}
    print(f"Sending SMS notification to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"SMS status: {response.status_code}")
    print(f"SMS response: {response.text}")
    return response.status_code


def send_voice_call(to, text, language="bg", speech_rate=0.9, gender=None, pause=None):
    url = f"https://{config.INFOBIP_BASE_URL}/tts/3/single"
    headers = {
        "Authorization": f"App {config.INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": config.VOICE_NUMBER_ID,
        "to": to,
        "text": text,
        "language": language,
        "speechRate": speech_rate,
    }
    if gender in ("male", "female"):
        payload["voice"] = {"gender": gender}
    if pause is not None:
        payload["pause"] = int(pause)
    print(f"Sending voice call to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Voice status: {response.status_code}")
    print(f"Voice response: {response.text}")
    return response.status_code, response.text


def send_raw_message(message):
    """Sends a single message object exactly as given to the Messages API,
    for channels/content schemas we don't have a dedicated helper for yet
    (e.g. RCS/WhatsApp/SMS templates with custom 'content' shapes)."""
    url = f"https://{config.INFOBIP_BASE_URL}/messages-api/1/messages"
    headers = {
        "Authorization": f"App {config.INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"messages": [message]}
    print(f"Sending raw message: {message}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Raw send status: {response.status_code}")
    print(f"Raw send response: {response.text}")
    return response.status_code, response.text


def get_rendered_template_text(template_name, language=None, placeholders=None):
    """Fetches the registered VBM template's body text from Infobip and fills in
    the placeholders - i.e. reconstructs the exact message the customer received.
    Returns None if the template can't be found (caller should fall back)."""
    url = f"https://{config.INFOBIP_BASE_URL}/viber/1/senders/{config.VBM_SENDER}/templates"
    headers = {
        "Authorization": f"App {config.INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if not response.ok:
            print(f"Template list fetch failed: {response.status_code}")
            return None
        templates = response.json().get("templates", [])
    except Exception as exc:
        print(f"Template list fetch error: {exc}")
        return None

    for template in templates:
        if template.get("templateId") != template_name:
            continue
        bodies = template.get("body") or []
        text = None
        for body in bodies:
            if language is None or body.get("language") == language:
                text = body.get("template")
                break
        if text is None and bodies:
            text = bodies[0].get("template")
        if not text:
            return None
        for key, value in (placeholders or {}).items():
            text = text.replace("{{%s}}" % key, str(value))
        return text
    return None


def send_template_notification(to, template_name, language, placeholders=None):
    url = f"https://{config.INFOBIP_BASE_URL}/messages-api/1/messages"
    headers = {
        "Authorization": f"App {config.INFOBIP_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {"type": "TEXT"}
    if placeholders:
        body.update(placeholders)

    payload = {
        "messages": [
            {
                "channel": "VIBER_BM",
                "sender": config.VBM_SENDER,
                "destinations": [{"to": to}],
                "template": {"templateName": template_name, "language": language},
                "content": {"body": body}
            }
        ]
    }
    print(f"Sending template '{template_name}' to: {to}")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Viber status: {response.status_code}")
    print(f"Viber response: {response.text}")
    return response.status_code, response.text
