import os

INFOBIP_API_KEY = os.environ.get("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.environ.get("INFOBIP_BASE_URL")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
APP_API_KEY = os.environ.get("APP_API_KEY")

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
VIBER_TEXT_LIMIT = 1000
MAX_HISTORY_MESSAGES = 10
AGENT_NOTIFY_PHONE = "359876888400"

VIBER_BOT_SENDER = "pa:6060271498432636599"
VBM_SENDER = "TCP"

SYSTEM_PROMPT = """Ти си помощник, специализиран в Infobip API и услуги (SMS, Viber, WhatsApp, Email, 2FA, Messages API).
Отговаряй кратко и ясно на български език, до 3-4 изречения. Не използвай markdown форматиране (без **, #, -, списъци) - само обикновен текст.
Ако ти е предоставен контекст от документация по-долу, базирай отговора си на него. Ако контекстът не съдържа отговора, кажи че не си сигурен."""

REPLY_BUTTONS = [
    {"type": "REPLY", "text": "Друг въпрос", "postbackData": "ANOTHER_QUESTION"},
    {"type": "REPLY", "text": "Свържи се с агент", "postbackData": "CONTACT_AGENT"},
    {"type": "OPEN_URL", "text": "Сайт на Infobip", "url": "https://www.infobip.com"},
    {"type": "REPLY", "text": "Край", "postbackData": "END_CHAT"}
]

# Registered Viber Business Message templates, keyed by a friendly name so
# /notify callers don't need to remember raw Infobip template IDs.
# "params" lists the placeholder keys the template body expects.
TEMPLATES = {
    "order_confirmation": {
        "id": "bb862b91-b6f0-4e1c-a31e-ebdcc822b240",
        "language": "bg",
        "params": ["1", "2", "3", "4", "5"],
        "description": "name, order_id, item, amount, delivery_address - confirmed working via API"
    },
    "otp": {
        "id": "5fafdcbe-8f81-4116-a14f-fabedb38b194",
        "language": "en",
        "params": ["pin"],
    },
    "euromaster": {
        "id": "97510a1e-11c6-4748-b4f4-b9c78e1a7b6b",
        "language": "bg",
        "params": ["First_name"],
        "description": "rich media (image + button) - operator rejects via API, use Broadcast instead"
    },
}

# In-memory only: cleared on every process restart/redeploy.
CONVERSATIONS = {}
AGENT_MODE_USERS = set()
