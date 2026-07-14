from typing import Literal

import requests

from viberbot import config


class InfobipOtpError(Exception):
    def __init__(self, message, raw=None):
        super().__init__(message)
        self.raw = raw


class InfobipPinExpired(InfobipOtpError):
    pass


class InfobipAttemptsExceeded(InfobipOtpError):
    pass


_SEND_PATH = {
    "sms": "/2fa/2/pin",
    "voice": "/2fa/2/pin/voice",
    "email": "/2fa/2/pin/email",
}

_MSG_ID_ENV = {
    "sms": lambda: config.INFOBIP_2FA_SMS_MSG_ID,
    "voice": lambda: config.INFOBIP_2FA_VOICE_MSG_ID,
    "email": lambda: config.INFOBIP_2FA_EMAIL_MSG_ID,
}


def _headers():
    return {
        "Authorization": f"App {config.INFOBIP_API_KEY}",
        "Content-Type": "application/json",
    }


def _base():
    return f"https://{config.INFOBIP_BASE_URL}"


def _parse_service_error(resp):
    try:
        svc = resp.json().get("requestError", {}).get("serviceException", {})
        return svc.get("text", resp.text), svc.get("messageId", "")
    except Exception:
        return resp.text, ""


def send_otp(channel: Literal["sms", "voice", "email"], destination: str) -> str:
    msg_id = _MSG_ID_ENV[channel]()
    if not config.INFOBIP_2FA_APP_ID or not msg_id:
        raise InfobipOtpError(
            f"Infobip 2FA не е конфигуриран (INFOBIP_2FA_APP_ID / INFOBIP_2FA_{channel.upper()}_MSG_ID липсват)"
        )

    body = {
        "applicationId": config.INFOBIP_2FA_APP_ID,
        "messageId": msg_id,
        "from": config.INFOBIP_2FA_FROM,
        "to": destination,
    }

    resp = requests.post(f"{_base()}{_SEND_PATH[channel]}", headers=_headers(), json=body)

    if not resp.ok:
        text, _ = _parse_service_error(resp)
        raise InfobipOtpError(
            f"[{channel}] send_otp върна {resp.status_code}: {text}", raw=resp.text
        )

    pin_id = resp.json().get("pinId")
    if not pin_id:
        raise InfobipOtpError(f"Липсва pinId в отговора: {resp.text}")
    return pin_id


def verify_otp(pin_id: str, pin: str) -> bool:
    resp = requests.post(
        f"{_base()}/2fa/2/pin/{pin_id}/verify",
        headers=_headers(),
        json={"pin": pin},
    )

    if resp.status_code == 404:
        raise InfobipPinExpired("PIN не е намерен или е изтекъл")

    if not resp.ok:
        text, msg_id = _parse_service_error(resp)
        text_lo = text.lower()
        if "expired" in text_lo or "EXPIRED" in msg_id:
            raise InfobipPinExpired(text)
        if "attempt" in text_lo or "ATTEMPTS" in msg_id:
            raise InfobipAttemptsExceeded(text)
        raise InfobipOtpError(f"verify_otp върна {resp.status_code}: {text}", raw=resp.text)

    return bool(resp.json().get("verified"))
