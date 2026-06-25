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
