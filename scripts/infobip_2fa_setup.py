#!/usr/bin/env python3
"""
Еднократен setup скрипт — създава 2FA application и message templates в Infobip.
Изпълни веднъж на среда и добави резултатите в .env.

Изисквани env vars: INFOBIP_BASE_URL, INFOBIP_API_KEY
Опционални: INFOBIP_2FA_APP_NAME, INFOBIP_2FA_FROM
"""
import os
import sys

import requests

BASE_URL = os.environ.get("INFOBIP_BASE_URL", "").strip()
API_KEY = os.environ.get("INFOBIP_API_KEY", "").strip()

if not BASE_URL or not API_KEY:
    print("ГРЕШКА: INFOBIP_BASE_URL и INFOBIP_API_KEY трябва да са зададени.")
    sys.exit(1)

APP_NAME = os.environ.get("INFOBIP_2FA_APP_NAME", "ViberBot Auth")
FROM = os.environ.get("INFOBIP_2FA_FROM", "InfoSMS")

HEADERS = {
    "Authorization": f"App {API_KEY}",
    "Content-Type": "application/json",
}


def post(path, body):
    url = f"https://{BASE_URL}{path}"
    resp = requests.post(url, headers=HEADERS, json=body)
    if not resp.ok:
        print(f"ГРЕШКА {resp.status_code} при {path}:\n{resp.text}")
        sys.exit(1)
    return resp.json()


print("=== Infobip 2FA Setup ===\n")

# 1. Създай application
print("1. Създаване на 2FA application...")
app_data = post("/2fa/2/applications", {
    "name": APP_NAME,
    "enabled": True,
    "configuration": {
        "pinAttempts": 5,
        "allowMultiplePinVerifications": False,
        "pinTimeToLive": "5m",
        "verifyPinLimit": "1/3s",
        "sendPinPerApplicationLimit": "10000/1d",
        "sendPinPerPhoneNumberLimit": "5/1d",
    },
})
app_id = app_data["applicationId"]
print(f"   OK → applicationId: {app_id}\n")

# 2. SMS template
print("2. Създаване на SMS message template...")
sms_data = post(f"/2fa/2/applications/{app_id}/messages", {
    "pinType": "NUMERIC",
    "messageText": "Вашият код за вход е {{pin}}. Валиден 5 минути.",
    "pinLength": 6,
    "senderId": FROM,
})
sms_msg_id = sms_data["messageId"]
print(f"   OK → SMS messageId: {sms_msg_id}\n")

# 3. Voice template
print("3. Създаване на Voice message template...")
voice_data = post(f"/2fa/2/applications/{app_id}/messages", {
    "pinType": "NUMERIC",
    "messageText": "Вашият код за вход е {{pin}}. Повтарям: {{pin}}.",
    "pinLength": 6,
    "senderId": FROM,
    "language": {"languageCode": "BG"},
    "repeatDTMF": "1#",
    "speechRate": 1.0,
})
voice_msg_id = voice_data["messageId"]
print(f"   OK → Voice messageId: {voice_msg_id}\n")

print("=" * 40)
print("Добави следното в .env:\n")
print(f"INFOBIP_2FA_APP_ID={app_id}")
print(f"INFOBIP_2FA_SMS_MSG_ID={sms_msg_id}")
print(f"INFOBIP_2FA_VOICE_MSG_ID={voice_msg_id}")
print(f"INFOBIP_2FA_FROM={FROM}")
print("\nЗа Email: добави INFOBIP_2FA_EMAIL_MSG_ID след ръчно създаване в Infobip портала.")
