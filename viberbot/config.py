import os

INFOBIP_API_KEY = os.environ.get("INFOBIP_API_KEY")
INFOBIP_BASE_URL = os.environ.get("INFOBIP_BASE_URL")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
APP_API_KEY = os.environ.get("APP_API_KEY")
DATABASE_URL = (
    os.environ.get("DATABASE_URL", "")
    .replace("postgres://", "postgresql://", 1)
    .replace("postgresql://", "postgresql+psycopg://", 1)
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

VIBER_TEXT_LIMIT = 1000
MAX_HISTORY_MESSAGES = 50
AGENT_NOTIFY_PHONE = "359876888400"
CONVERSATION_TIMEOUT_MINUTES = 3

VIBER_BOT_SENDER = "pa:6060271498432636599"
VBM_SENDER = "TCP"
VOICE_NUMBER_ID = os.environ.get("VOICE_NUMBER_ID", "5F5865622A8A2F6CEE951860D0432E98")

SYSTEM_PROMPT = """Ти си помощник, специализиран в Infobip API и услуги (SMS, Viber, WhatsApp, Email, 2FA, Messages API).
Отговаряй кратко и ясно на български език, до 3-4 изречения. Не използвай markdown форматиране (без **, #, -, списъци) - само обикновен текст.
Ако ти е предоставен контекст от документация по-долу, базирай отговора си на него. Ако контекстът не съдържа отговора, кажи че не си сигурен."""

REPLY_BUTTONS = [
    {"type": "REPLY", "text": "Друг въпрос", "postbackData": "ANOTHER_QUESTION"},
    {"type": "REPLY", "text": "Свържи се с агент", "postbackData": "CONTACT_AGENT"},
    {"type": "OPEN_URL", "text": "Сайт на Infobip", "url": "https://www.infobip.com"},
    {"type": "REPLY", "text": "Край", "postbackData": "END_CHAT"}
]

