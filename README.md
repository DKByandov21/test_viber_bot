# Viber Communication Hub

Flask приложение за двупосочна комуникация с клиенти през Viber (Business Messages + Viber Bot) с AI асистент, live agent handoff и уеб dashboard за операторите.

## Възможности

- **Viber Business Messages (VBM)** — изпращане на template известия (пратки, плащания, застраховки) и AI отговори на клиентските въпроси в контекста на изпратеното известие
- **Viber Bot** — AI асистент за Infobip услуги с RAG върху локална документация (`knowledge/`)
- **Live agent** — клиентът пише „искам агент" → разговорът влиза в опашка, операторът отговаря от dashboard-а
- **2FA вход** — OTP код по Viber, SMS, Voice или Email (Infobip 2FA API)
- **Voice** — TTS обаждания през Infobip `/tts/3/single`
- **Dashboard** — React SPA: разговори, agent queue, template изпращане, статистики, knowledge base

## Структура на проекта

```
├── app.py                      # Entry point (gunicorn app:app)
├── Procfile / runtime.txt      # Deploy конфигурация
├── requirements.txt
├── .env.example                # Шаблон за environment променливи
│
├── viberbot/                   # Flask backend пакет
│   ├── __init__.py             # App factory, регистрация на blueprints
│   ├── config.py               # Всички настройки, промптове, сендъри
│   ├── db.py                   # SQLAlchemy модели + миграции
│   ├── auth.py                 # Session/admin декоратори
│   ├── handlers/
│   │   └── webhook_handlers.py # Логика за входящи съобщения (AI/agent routing)
│   ├── routes/                 # HTTP endpoints (blueprints)
│   │   ├── webhook.py          # POST /webhook — входящи от Infobip
│   │   ├── agent.py            # POST /agent-reply — отговор от оператор
│   │   ├── notify.py           # /notify* — изпращане на template-и
│   │   ├── auth.py             # /api/auth/* — вход с 2FA
│   │   ├── dashboard_api.py    # /api/* — данни за dashboard-а
│   │   ├── dashboard_spa.py    # Сервира React build-а на /dashboard
│   │   ├── knowledge.py        # CRUD за knowledge base
│   │   ├── voice.py            # TTS обаждания
│   │   ├── users.py, projects.py, health.py
│   └── services/               # Бизнес логика
│       ├── state.py            # Разговори, история, сесии, agent_mode
│       ├── groq_client.py      # AI отговори (Groq) + RAG
│       ├── infobip_client.py   # Изходящи Viber/SMS/Voice съобщения
│       ├── infobip_2fa_client.py # Infobip 2FA API (SMS/Voice/Email OTP)
│       ├── auth_service.py     # Login flow, OTP verification
│       ├── knowledge_base.py   # RAG chunk търсене
│       └── projects.py
│
├── dashboard/                  # React SPA (Vite)
│   ├── src/pages/              # Страници (AgentQueue, Conversations, Notify...)
│   ├── src/components/         # Layout, навигация
│   ├── src/auth/               # Auth context, protected routes
│   └── dist/                   # Production build (committed, сервира се от Flask)
│
├── knowledge/                  # Markdown документация за RAG (Viber Bot)
├── docs/
│   └── clients/                # Клиентска документация и тестове
│       └── allianz-templates.md# Allianz Bank — 19 Viber template-а (тестов клиент)
├── scripts/
│   └── infobip_2fa_setup.py    # Еднократен setup на 2FA app + templates
└── tests/                      # pytest unit тестове (mock-нат HTTP/DB слой)
```

## Как работи комуникацията

```
Клиент (Viber) → Infobip → POST /webhook
                              │
                    agent_mode активен? ──да──→ записва се в историята,
                              │                 операторът вижда в Agent Queue
                             не
                              │
                    keyword „агент"? ──да──→ agent_mode=True, SMS до оператора
                              │
                    AI отговор (Groq)
                    ├─ VBM: контекст = последното изпратено известие
                    └─ Bot: контекст = knowledge base (RAG)
```

Операторът отговаря от Dashboard → Agent Queue → POST `/agent-reply` → Viber.

## Setup

1. `pip install -r requirements.txt`
2. Копирай `.env.example` → `.env` и попълни ключовете
3. За 2FA: изпълни еднократно `python scripts/infobip_2fa_setup.py` и добави ID-тата в `.env`
4. Стартиране: `gunicorn app:app` (или `flask run` за development)
5. Dashboard build: `cd dashboard && npm install && npm run build`

## Тестове

```
python3 -m pytest tests/
```

## Deploy бележки

- `dashboard/dist/` е committed (Flask го сервира директно) — след промяна по UI: `npm run build` + `git add -f dashboard/dist/assets/*`
- DB миграциите са идемпотентни `ALTER TABLE IF NOT EXISTS` в `db.py:init_db` — изпълняват се при всеки старт
- `.env` никога не се commit-ва
