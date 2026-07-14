# Allianz Bank — Viber Template документация

Всички template-и са регистрирани чрез Infobip API и са тествани успешно.  
Канал: Viber Business Messages | Категория: `TRANSACTIONAL`

---

## Обща структура

**Регистрация:**
```
POST https://{baseUrl}/viber/1/senders/{sender}/templates
Authorization: App {api-key}
```

**Изпращане:**
```
POST https://{baseUrl}/viber/2/messages
Authorization: App {api-key}
```

**SMS Failover** се добавя само в **send заявката** — не се поддържа на ниво регистрация.  
Полето `smsFailover.text` е **статичен текст** (параметрите трябва да са заместени с реалните стойности преди изпращане).

---

## Съдържание

| # | Template | Език | templateId |
|---|----------|------|-----------|
| 1 | [1_verification](#1-1_verification--верификационен-код-bg) | BG | `f4efc9c6-6155-4b37-bcc6-4bc7627ce40f` |
| 2 | [2_low_balance](#2-2_low_balance--ниска-наличност-bg) | BG | `7016b853-bc63-4120-b2f2-c3676991ab0a` |
| 3 | [3_card_success](#3-3_card_success--успешна-транзакция-bg) | BG | `9b2514ff-1d9e-429d-9251-7726d29aabd6` |
| 4 | [4_card_failed](#4-4_card_failed--неуспешна-транзакция-bg) | BG | `9825fbb6-dbe7-48c8-a465-86f8185f94cb` |
| 5 | [5_card_refund](#5-5_card_refund--възстановена-сума-bg) | BG | `7c722b1c-5a66-4bb5-a62f-f17bbc55f8b8` |
| 6 | [6_payment_outgoing](#6-6_payment_outgoing--изходящ-превод-bg) | BG | `8ce86185-ef85-4163-8a43-83dc39e989e5` |
| 7 | [7_payment_incoming](#7-7_payment_incoming--входящ-превод-bg) | BG | `b895bdbb-7df2-4f84-a973-948ed6c34b2b` |
| 8 | [8_account_balance](#8-8_account_balance--баланс-по-сметка-bg) | BG | `8704863c-2fdb-464b-bbcd-cce5e7171223` |
| 9 | [1_verification_en](#9-1_verification_en--верификационен-код-en) | EN | `c2975a4d-8b44-45cc-b172-e96d80d51a53` |
| 10 | [2_low_balance_en](#10-2_low_balance_en--ниска-наличност-en) | EN | `a1babf75-8fa7-400c-8e67-bd1513bb69b9` |
| 11 | [3_card_success_en](#11-3_card_success_en--успешна-транзакция-en) | EN | `85e4cafb-544a-4f6d-8e6b-94264e0257df` |
| 12 | [4_card_failed_en](#12-4_card_failed_en--неуспешна-транзакция-en) | EN | `5910cccb-860a-4d24-a34d-05b7ce928ac6` |
| 13 | [5_card_refund_en](#13-5_card_refund_en--възстановена-сума-en) | EN | `ca6b5feb-1538-4e71-bfd4-89bc46b00e26` |
| 14 | [6_payment_outgoing_en](#14-6_payment_outgoing_en--изходящ-превод-en) | EN | `6fe2247c-5166-45f9-9caf-b39e3e0c6a6b` |
| 15 | [7_payment_incoming_en](#15-7_payment_incoming_en--входящ-превод-en) | EN | `5132e3ff-19ef-45a3-b1a7-219a0f781761` |
| 16 | [8_account_balance_en](#16-8_account_balance_en--баланс-по-сметка-en) | EN | `1f682393-da32-455d-9b21-271f97faf668` |
| 17 | [ins_policy_payment](#17-ins_policy_payment--напомняне-за-плащане-по-полица) | BG | `d4bbfb54-cda7-4dc6-bd8a-cc8a8a778d0b` |
| 18 | [ins_life_payment](#18-ins_life_payment--напомняне-по-полица-живот) | BG | `0c089bfc-9d8e-42fb-bd58-c4c4b1729450` |
| 19 | [ins_car_service](#19-ins_car_service--запис-за-автосервиз) | BG | `d9b4f2ea-091c-4cab-a2e6-d6b677469507` |

---

## 1. `1_verification` — Верификационен код (BG)

**Текст на съобщението:**
```
Вие заявихте {{service_type}} по канал Viber на {{phone}}. Моля, потвърдете с код {{code}}. Кодът е валиден 5 минути.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "Вие заявихте {{service_type}} по канал Viber на {{phone}}. Моля, потвърдете с код {{code}}. Кодът е валиден 5 минути."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "service_type", "example": "превод" },
      { "type": "TEXT", "name": "phone",        "example": "+359XXXXXXXXX" },
      { "type": "TEXT", "name": "code",         "example": "483291" }
    ]
  }'
```

**Отговор:** `templateId: f4efc9c6-6155-4b37-bcc6-4bc7627ce40f`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "f4efc9c6-6155-4b37-bcc6-4bc7627ce40f",
          "language": "bg",
          "parameters": {
            "service_type": "превод",
            "phone": "+359XXXXXXXXX",
            "code": "483291"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "Вие заявихте превод по канал Viber. Потвърдете с код 483291. Валиден 5 минути."
          }
        }
      }
    ]
  }'
```

---

## 2. `2_low_balance` — Ниска наличност (BG)


**Текст на съобщението:**
```
Разполагаемата сума за известия е под 1 EUR. Моля, допълнете депозита за известия в меню Управление на известия на Алианц Банк Онлайн.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "Разполагаемата сума за известия е под 1 EUR. Моля, допълнете депозита за известия в меню Управление на известия на Алианц Банк Онлайн."
      }
    ],
    "params": []
  }'
```

**Отговор:** `templateId: 7016b853-bc63-4120-b2f2-c3676991ab0a`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "7016b853-bc63-4120-b2f2-c3676991ab0a",
          "language": "bg",
          "parameters": {}
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "Разполагаемата сума за известия е под 1 EUR. Допълнете депозита в Алианц Банк Онлайн."
          }
        }
      }
    ]
  }'
```

---

## 3. `3_card_success` — Успешна транзакция (BG)

**Текст на съобщението:**
```
АлианцБанк ({{deposit_info}}) Успешна транзакция с карта {{card}} на сума {{amount}} {{currency}}, {{location}}. Наличност: {{balance}} {{balance_currency}} към {{datetime}}. Алианц Банк.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "АлианцБанк ({{deposit_info}}) Успешна транзакция с карта {{card}} на сума {{amount}} {{currency}}, {{location}}. Наличност: {{balance}} {{balance_currency}} към {{datetime}}. Алианц Банк."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info",     "example": "45.00 BGN" },
      { "type": "TEXT", "name": "card",             "example": "****1234" },
      { "type": "TEXT", "name": "amount",           "example": "150.00" },
      { "type": "TEXT", "name": "currency",         "example": "BGN" },
      { "type": "TEXT", "name": "location",         "example": "LIDL SOFIA" },
      { "type": "TEXT", "name": "balance",          "example": "1250.00" },
      { "type": "TEXT", "name": "balance_currency", "example": "BGN" },
      { "type": "TEXT", "name": "datetime",         "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: 9b2514ff-1d9e-429d-9251-7726d29aabd6`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "9b2514ff-1d9e-429d-9251-7726d29aabd6",
          "language": "bg",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "card": "****1234",
            "amount": "150.00",
            "currency": "BGN",
            "location": "LIDL SOFIA",
            "balance": "1250.00",
            "balance_currency": "BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "АлианцБанк (45.00 BGN) Успешна транзакция с карта ****1234 на сума 150.00 BGN, LIDL SOFIA. Наличност: 1250.00 BGN към 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 4. `4_card_failed` — Неуспешна транзакция (BG)

**Текст на съобщението:**
```
АлианцБанк ({{deposit_info}}) Неуспешна транзакция с карта {{card}} на сума {{amount}} {{currency}}, {{reason}}. Наличност: {{balance}} {{balance_currency}} към {{datetime}}. Алианц Банк.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "АлианцБанк ({{deposit_info}}) Неуспешна транзакция с карта {{card}} на сума {{amount}} {{currency}}, {{reason}}. Наличност: {{balance}} {{balance_currency}} към {{datetime}}. Алианц Банк."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info",     "example": "45.00 BGN" },
      { "type": "TEXT", "name": "card",             "example": "****1234" },
      { "type": "TEXT", "name": "amount",           "example": "150.00" },
      { "type": "TEXT", "name": "currency",         "example": "BGN" },
      { "type": "TEXT", "name": "reason",           "example": "Недостатъчни средства" },
      { "type": "TEXT", "name": "balance",          "example": "50.00" },
      { "type": "TEXT", "name": "balance_currency", "example": "BGN" },
      { "type": "TEXT", "name": "datetime",         "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: 9825fbb6-dbe7-48c8-a465-86f8185f94cb`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "9825fbb6-dbe7-48c8-a465-86f8185f94cb",
          "language": "bg",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "card": "****1234",
            "amount": "150.00",
            "currency": "BGN",
            "reason": "Недостатъчни средства",
            "balance": "50.00",
            "balance_currency": "BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "АлианцБанк (45.00 BGN) Неуспешна транзакция с карта ****1234 на сума 150.00 BGN, Недостатъчни средства. Наличност: 50.00 BGN към 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 5. `5_card_refund` — Възстановена сума (BG)

**Текст на съобщението:**
```
АлианцБанк ({{deposit_info}}) Възстановени {{amount}} {{currency}} по {{account}} за карта {{card}}, {{reason}}. Наличност: {{balance_info}} към {{datetime}}. Алианц Банк.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "АлианцБанк ({{deposit_info}}) Възстановени {{amount}} {{currency}} по {{account}} за карта {{card}}, {{reason}}. Наличност: {{balance_info}} към {{datetime}}. Алианц Банк."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "amount",       "example": "50.00" },
      { "type": "TEXT", "name": "currency",     "example": "BGN" },
      { "type": "TEXT", "name": "account",      "example": "BG80XXXXXXXXXXXXXXXXXXXX" },
      { "type": "TEXT", "name": "card",         "example": "****1234" },
      { "type": "TEXT", "name": "reason",       "example": "Отменена поръчка" },
      { "type": "TEXT", "name": "balance_info", "example": "1300.00 BGN" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: 7c722b1c-5a66-4bb5-a62f-f17bbc55f8b8`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "7c722b1c-5a66-4bb5-a62f-f17bbc55f8b8",
          "language": "bg",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "amount": "50.00",
            "currency": "BGN",
            "account": "BG80XXXXXXXXXXXXXXXXXXXX",
            "card": "****1234",
            "reason": "Отменена поръчка",
            "balance_info": "1300.00 BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "АлианцБанк (45.00 BGN) Възстановени 50.00 BGN по BG80XXXX за карта ****1234, Отменена поръчка. Наличност: 1300.00 BGN към 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 6. `6_payment_outgoing` — Изходящ превод (BG)

**Текст на съобщението:**
```
АлианцБанк ({{deposit_info}}) Платени {{amount}} {{currency}} от {{account}} на {{recipient}}, {{description}}. Наличност: {{balance_info}} към {{datetime}}. Алианц Банк.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "АлианцБанк ({{deposit_info}}) Платени {{amount}} {{currency}} от {{account}} на {{recipient}}, {{description}}. Наличност: {{balance_info}} към {{datetime}}. Алианц Банк."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "amount",       "example": "200.00" },
      { "type": "TEXT", "name": "currency",     "example": "BGN" },
      { "type": "TEXT", "name": "account",      "example": "BG80XXXXXXXXXXXXXXXXXXXX" },
      { "type": "TEXT", "name": "recipient",    "example": "ПОЛУЧАТЕЛ" },
      { "type": "TEXT", "name": "description",  "example": "ОПИСАНИЕ" },
      { "type": "TEXT", "name": "balance_info", "example": "1050.00 BGN" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: 8ce86185-ef85-4163-8a43-83dc39e989e5`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "8ce86185-ef85-4163-8a43-83dc39e989e5",
          "language": "bg",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "amount": "200.00",
            "currency": "BGN",
            "account": "BG80XXXXXXXXXXXXXXXXXXXX",
            "recipient": "ПОЛУЧАТЕЛ",
            "description": "ОПИСАНИЕ",
            "balance_info": "1050.00 BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "АлианцБанк (45.00 BGN) Платени 200.00 BGN от BG80XXXX на ПОЛУЧАТЕЛ, ОПИСАНИЕ. Наличност: 1050.00 BGN към 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 7. `7_payment_incoming` — Входящ превод (BG)

**Текст на съобщението:**
```
АлианцБанк ({{deposit_info}}) Постъпили {{amount}} {{currency}} по {{account}} от {{payer}}, {{description}}. Наличност: {{balance_info}} към {{datetime}}. Алианц Банк.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "АлианцБанк ({{deposit_info}}) Постъпили {{amount}} {{currency}} по {{account}} от {{payer}}, {{description}}. Наличност: {{balance_info}} към {{datetime}}. Алианц Банк."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "amount",       "example": "500.00" },
      { "type": "TEXT", "name": "currency",     "example": "BGN" },
      { "type": "TEXT", "name": "account",      "example": "BG80XXXXXXXXXXXXXXXXXXXX" },
      { "type": "TEXT", "name": "payer",        "example": "ИМЕ ФАМИЛИЯ" },
      { "type": "TEXT", "name": "description",  "example": "ОПИСАНИЕ" },
      { "type": "TEXT", "name": "balance_info", "example": "1550.00 BGN" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: b895bdbb-7df2-4f84-a973-948ed6c34b2b`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "b895bdbb-7df2-4f84-a973-948ed6c34b2b",
          "language": "bg",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "amount": "500.00",
            "currency": "BGN",
            "account": "BG80XXXXXXXXXXXXXXXXXXXX",
            "payer": "ИМЕ ФАМИЛИЯ",
            "description": "ОПИСАНИЕ",
            "balance_info": "1550.00 BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "АлианцБанк (45.00 BGN) Постъпили 500.00 BGN по BG80XXXX от ИМЕ ФАМИЛИЯ, ОПИСАНИЕ. Наличност: 1550.00 BGN към 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 8. `8_account_balance` — Баланс по сметка (BG)

**Текст на съобщението:**
```
АлианцБанк ({{deposit_info}}) Наличност по {{account}} към {{datetime}}: {{balance}} {{balance_currency}}. Алианц Банк.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "АлианцБанк ({{deposit_info}}) Наличност по {{account}} към {{datetime}}: {{balance}} {{balance_currency}}. Алианц Банк."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info",     "example": "45.00 BGN" },
      { "type": "TEXT", "name": "account",          "example": "BG80XXXXXXXXXXXXXXXXXXXX" },
      { "type": "TEXT", "name": "datetime",         "example": "06.07.2026 13:45" },
      { "type": "TEXT", "name": "balance",          "example": "1550.00" },
      { "type": "TEXT", "name": "balance_currency", "example": "BGN" }
    ]
  }'
```

**Отговор:** `templateId: 8704863c-2fdb-464b-bbcd-cce5e7171223`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "8704863c-2fdb-464b-bbcd-cce5e7171223",
          "language": "bg",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "account": "BG80XXXXXXXXXXXXXXXXXXXX",
            "datetime": "06.07.2026 13:45",
            "balance": "1550.00",
            "balance_currency": "BGN"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "АлианцБанк (45.00 BGN) Наличност по BG80XXXX към 06.07.2026 13:45: 1550.00 BGN."
          }
        }
      }
    ]
  }'
```

---

## 9. `1_verification_en` — Верификационен код (EN)


**Message text:**
```
You requested {{service_type}} by channel Viber to {{phone}}. Please confirm with code {{code}}. The code is valid for 5 minutes.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "en",
        "template": "You requested {{service_type}} by channel Viber to {{phone}}. Please confirm with code {{code}}. The code is valid for 5 minutes."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "service_type", "example": "transfer" },
      { "type": "TEXT", "name": "phone",        "example": "+359XXXXXXXXX" },
      { "type": "TEXT", "name": "code",         "example": "483291" }
    ]
  }'
```

**Отговор:** `templateId: c2975a4d-8b44-45cc-b172-e96d80d51a53`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "c2975a4d-8b44-45cc-b172-e96d80d51a53",
          "language": "en",
          "parameters": {
            "service_type": "transfer",
            "phone": "+359XXXXXXXXX",
            "code": "483291"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "You requested a transfer via Viber. Please confirm with code 483291. Valid for 5 minutes."
          }
        }
      }
    ]
  }'
```

---

## 10. `2_low_balance_en` — Ниска наличност (EN)

**Message text:**
```
The available amount for notifications is less than EUR 1. Please top up the deposit for notifications via Manage Notifications menu in Allianz Bank Online.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "en",
        "template": "The available amount for notifications is less than EUR 1. Please top up the deposit for notifications via Manage Notifications menu in Allianz Bank Online."
      }
    ],
    "params": []
  }'
```

**Отговор:** `templateId: a1babf75-8fa7-400c-8e67-bd1513bb69b9`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "a1babf75-8fa7-400c-8e67-bd1513bb69b9",
          "language": "en",
          "parameters": {}
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "The available amount for notifications is less than EUR 1. Please top up via Allianz Bank Online."
          }
        }
      }
    ]
  }'
```

---

## 11. `3_card_success_en` — Успешна транзакция (EN)

**Message text:**
```
AllianzBank ({{deposit_info}}) Successful card transaction {{card}} amount {{amount}} {{currency}} {{location}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "en",
        "template": "AllianzBank ({{deposit_info}}) Successful card transaction {{card}} amount {{amount}} {{currency}} {{location}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "card",         "example": "****1234" },
      { "type": "TEXT", "name": "amount",       "example": "150.00" },
      { "type": "TEXT", "name": "currency",     "example": "BGN" },
      { "type": "TEXT", "name": "location",     "example": "LIDL SOFIA" },
      { "type": "TEXT", "name": "balance_info", "example": "1250.00 BGN" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: 85e4cafb-544a-4f6d-8e6b-94264e0257df`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "85e4cafb-544a-4f6d-8e6b-94264e0257df",
          "language": "en",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "card": "****1234",
            "amount": "150.00",
            "currency": "BGN",
            "location": "LIDL SOFIA",
            "balance_info": "1250.00 BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "AllianzBank (45.00 BGN) Successful card transaction ****1234 amount 150.00 BGN LIDL SOFIA. Available: 1250.00 BGN on 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 12. `4_card_failed_en` — Неуспешна транзакция (EN)

**Message text:**
```
AllianzBank ({{deposit_info}}) Failed card transaction {{card}} amount {{amount}} {{currency}} {{reason}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "en",
        "template": "AllianzBank ({{deposit_info}}) Failed card transaction {{card}} amount {{amount}} {{currency}} {{reason}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "card",         "example": "****1234" },
      { "type": "TEXT", "name": "amount",       "example": "150.00" },
      { "type": "TEXT", "name": "currency",     "example": "BGN" },
      { "type": "TEXT", "name": "reason",       "example": "Insufficient funds" },
      { "type": "TEXT", "name": "balance_info", "example": "50.00 BGN" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: 5910cccb-860a-4d24-a34d-05b7ce928ac6`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "5910cccb-860a-4d24-a34d-05b7ce928ac6",
          "language": "en",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "card": "****1234",
            "amount": "150.00",
            "currency": "BGN",
            "reason": "Insufficient funds",
            "balance_info": "50.00 BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "AllianzBank (45.00 BGN) Failed card transaction ****1234 amount 150.00 BGN Insufficient funds. Available: 50.00 BGN on 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 13. `5_card_refund_en` — Възстановена сума (EN)

**Message text:**
```
AllianzBank ({{deposit_info}}) Refunded {{amount}} {{currency}} on {{account}} for card {{card}} {{reason}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "en",
        "template": "AllianzBank ({{deposit_info}}) Refunded {{amount}} {{currency}} on {{account}} for card {{card}} {{reason}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "amount",       "example": "50.00" },
      { "type": "TEXT", "name": "currency",     "example": "BGN" },
      { "type": "TEXT", "name": "account",      "example": "BG80XXXXXXXXXXXXXXXXXXXX" },
      { "type": "TEXT", "name": "card",         "example": "****1234" },
      { "type": "TEXT", "name": "reason",       "example": "Cancelled order" },
      { "type": "TEXT", "name": "balance_info", "example": "1300.00 BGN" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: ca6b5feb-1538-4e71-bfd4-89bc46b00e26`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "ca6b5feb-1538-4e71-bfd4-89bc46b00e26",
          "language": "en",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "amount": "50.00",
            "currency": "BGN",
            "account": "BG80XXXXXXXXXXXXXXXXXXXX",
            "card": "****1234",
            "reason": "Cancelled order",
            "balance_info": "1300.00 BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "AllianzBank (45.00 BGN) Refunded 50.00 BGN on BG80XXXX for card ****1234 Cancelled order. Available: 1300.00 BGN on 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 14. `6_payment_outgoing_en` — Изходящ превод (EN)

**Message text:**
```
AllianzBank ({{deposit_info}}) Paid {{amount}} {{currency}} from {{account}} to {{recipient}} {{description}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "en",
        "template": "AllianzBank ({{deposit_info}}) Paid {{amount}} {{currency}} from {{account}} to {{recipient}} {{description}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "amount",       "example": "200.00" },
      { "type": "TEXT", "name": "currency",     "example": "BGN" },
      { "type": "TEXT", "name": "account",      "example": "BG80XXXXXXXXXXXXXXXXXXXX" },
      { "type": "TEXT", "name": "recipient",    "example": "RECIPIENT NAME" },
      { "type": "TEXT", "name": "description",  "example": "DESCRIPTION" },
      { "type": "TEXT", "name": "balance_info", "example": "1050.00 BGN" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: 6fe2247c-5166-45f9-9caf-b39e3e0c6a6b`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "6fe2247c-5166-45f9-9caf-b39e3e0c6a6b",
          "language": "en",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "amount": "200.00",
            "currency": "BGN",
            "account": "BG80XXXXXXXXXXXXXXXXXXXX",
            "recipient": "RECIPIENT NAME",
            "description": "DESCRIPTION",
            "balance_info": "1050.00 BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "AllianzBank (45.00 BGN) Paid 200.00 BGN from BG80XXXX to RECIPIENT NAME DESCRIPTION. Available: 1050.00 BGN on 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 15. `7_payment_incoming_en` — Входящ превод (EN)

**Message text:**
```
AllianzBank ({{deposit_info}}) Incoming {{amount}} {{currency}} to {{account}} from {{payer}} {{description}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "en",
        "template": "AllianzBank ({{deposit_info}}) Incoming {{amount}} {{currency}} to {{account}} from {{payer}} {{description}}. Available: {{balance_info}} on {{datetime}}. Allianz Bank."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "amount",       "example": "500.00" },
      { "type": "TEXT", "name": "currency",     "example": "BGN" },
      { "type": "TEXT", "name": "account",      "example": "BG80XXXXXXXXXXXXXXXXXXXX" },
      { "type": "TEXT", "name": "payer",        "example": "FIRST LAST" },
      { "type": "TEXT", "name": "description",  "example": "DESCRIPTION" },
      { "type": "TEXT", "name": "balance_info", "example": "1550.00 BGN" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" }
    ]
  }'
```

**Отговор:** `templateId: 5132e3ff-19ef-45a3-b1a7-219a0f781761`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "5132e3ff-19ef-45a3-b1a7-219a0f781761",
          "language": "en",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "amount": "500.00",
            "currency": "BGN",
            "account": "BG80XXXXXXXXXXXXXXXXXXXX",
            "payer": "FIRST LAST",
            "description": "DESCRIPTION",
            "balance_info": "1550.00 BGN",
            "datetime": "06.07.2026 13:45"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "AllianzBank (45.00 BGN) Incoming 500.00 BGN to BG80XXXX from FIRST LAST DESCRIPTION. Available: 1550.00 BGN on 06.07.2026 13:45."
          }
        }
      }
    ]
  }'
```

---

## 16. `8_account_balance_en` — Баланс по сметка (EN)

**Message text:**
```
AllianzBank ({{deposit_info}}) Account balance {{account}} on {{datetime}}: {{balance_info}}. Allianz Bank.
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "en",
        "template": "AllianzBank ({{deposit_info}}) Account balance {{account}} on {{datetime}}: {{balance_info}}. Allianz Bank."
      }
    ],
    "params": [
      { "type": "TEXT", "name": "deposit_info", "example": "45.00 BGN" },
      { "type": "TEXT", "name": "account",      "example": "BG80XXXXXXXXXXXXXXXXXXXX" },
      { "type": "TEXT", "name": "datetime",     "example": "06.07.2026 13:45" },
      { "type": "TEXT", "name": "balance_info", "example": "1550.00 BGN" }
    ]
  }'
```

**Отговор:** `templateId: 1f682393-da32-455d-9b21-271f97faf668`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "1f682393-da32-455d-9b21-271f97faf668",
          "language": "en",
          "parameters": {
            "deposit_info": "45.00 BGN",
            "account": "BG80XXXXXXXXXXXXXXXXXXXX",
            "datetime": "06.07.2026 13:45",
            "balance_info": "1550.00 BGN"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "AllianzBank (45.00 BGN) Account balance BG80XXXX on 06.07.2026 13:45: 1550.00 BGN."
          }
        }
      }
    ]
  }'
```

---

## 17. `ins_policy_payment` — Напомняне за плащане по полица

**Текст на съобщението:**
```
Здравейте,
 
Към {{period}} по полица {{policy_number}} {{policy_type}} дължите {{amount}} {{currency}}, които може да платите до {{due_date}}. При липса на плащане до посочената дата, полицата ще бъде прекратена от {{termination_date}}. Моля да ни извините, ако вече сте направили плащане.
 
Поздрави,
Екипът на Алианц България
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "Здравейте,\n \nКъм {{period}} по полица {{policy_number}} {{policy_type}} дължите {{amount}} {{currency}}, които може да платите до {{due_date}}. При липса на плащане до посочената дата, полицата ще бъде прекратена от {{termination_date}}. Моля да ни извините, ако вече сте направили плащане.\n \nПоздрави,\nЕкипът на Алианц България"
      }
    ],
    "params": [
      { "type": "TEXT", "name": "period",           "example": "01.01.2026" },
      { "type": "TEXT", "name": "policy_number",    "example": "123456789" },
      { "type": "TEXT", "name": "policy_type",      "example": "Автокаско" },
      { "type": "TEXT", "name": "amount",           "example": "250.00" },
      { "type": "TEXT", "name": "currency",         "example": "BGN" },
      { "type": "TEXT", "name": "due_date",         "example": "31.07.2026" },
      { "type": "TEXT", "name": "termination_date", "example": "01.08.2026" }
    ]
  }'
```

**Отговор:** `templateId: d4bbfb54-cda7-4dc6-bd8a-cc8a8a778d0b`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "d4bbfb54-cda7-4dc6-bd8a-cc8a8a778d0b",
          "language": "bg",
          "parameters": {
            "period": "01.01.2026",
            "policy_number": "123456789",
            "policy_type": "Автокаско",
            "amount": "250.00",
            "currency": "BGN",
            "due_date": "31.07.2026",
            "termination_date": "01.08.2026"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "Към 01.01.2026 по полица 123456789 Автокаско дължите 250.00 BGN, платими до 31.07.2026. При неплащане полицата се прекратява от 01.08.2026. Алианц България."
          }
        }
      }
    ]
  }'
```

---

## 18. `ins_life_payment` — Напомняне по полица Живот

**Текст на съобщението:**
```
Здравейте,
По полица Живот {{policy_number}} дължите сума {{amount}} {{currency}}. Покритието по застраховката Ви е изтекло на {{expiry_date}}. Повече информация можете да получите на {{contact}}. Моля да ни извините, ако вече сте превели сумата.
 
Всяка обратна връзка ни помага да станем по-добри - моля, споделете Вашата оценка за Алианц: https://imo.cx/AZBGLifeBG
 
Поздрави,
Екипът на Алианц България
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "Здравейте,\nПо полица Живот {{policy_number}} дължите сума {{amount}} {{currency}}. Покритието по застраховката Ви е изтекло на {{expiry_date}}. Повече информация можете да получите на {{contact}}. Моля да ни извините, ако вече сте превели сумата.\n \nВсяка обратна връзка ни помага да станем по-добри - моля, споделете Вашата оценка за Алианц: https://imo.cx/AZBGLifeBG\n \nПоздрави,\nЕкипът на Алианц България"
      }
    ],
    "params": [
      { "type": "TEXT", "name": "policy_number", "example": "987654321" },
      { "type": "TEXT", "name": "amount",        "example": "180.00" },
      { "type": "TEXT", "name": "currency",      "example": "BGN" },
      { "type": "TEXT", "name": "expiry_date",   "example": "30.06.2026" },
      { "type": "TEXT", "name": "contact",       "example": "0700 10 010" }
    ]
  }'
```

**Отговор:** `templateId: 0c089bfc-9d8e-42fb-bd58-c4c4b1729450`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "0c089bfc-9d8e-42fb-bd58-c4c4b1729450",
          "language": "bg",
          "parameters": {
            "policy_number": "987654321",
            "amount": "180.00",
            "currency": "BGN",
            "expiry_date": "30.06.2026",
            "contact": "0700 10 010"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "По полица Живот 987654321 дължите 180.00 BGN. Покритието е изтекло на 30.06.2026. За информация: 0700 10 010. Алианц България."
          }
        }
      }
    ]
  }'
```

---

## 19. `ins_car_service` — Запис за автосервиз

**Текст на съобщението:**
```
Здравейте,
 
За автомобил {{car}} има регистрирана поръчка {{order_number}} за сервиз {{service_center}}. Можете да запишете час за прием на автомобила на тел.: {{phone1}} {{phone2}}
 
Поздрави,
Екипът на Алианц България
```

### Регистрация

```bash
curl -X POST "https://{baseUrl}/viber/1/senders/{sender}/templates" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "TRANSACTIONAL",
    "body": [
      {
        "language": "bg",
        "template": "Здравейте,\n \nЗа автомобил {{car}} има регистрирана поръчка {{order_number}} за сервиз {{service_center}}. Можете да запишете час за прием на автомобила на тел.: {{phone1}} {{phone2}}\n \nПоздрави,\nЕкипът на Алианц България"
      }
    ],
    "params": [
      { "type": "TEXT", "name": "car",            "example": "CA1234AB Toyota Corolla" },
      { "type": "TEXT", "name": "order_number",   "example": "WO-2026-00123" },
      { "type": "TEXT", "name": "service_center", "example": "АвтоСервиз София" },
      { "type": "TEXT", "name": "phone1",         "example": "02 800 0000" },
      { "type": "TEXT", "name": "phone2",         "example": "0888 123 456" }
    ]
  }'
```

**Отговор:** `templateId: d9b4f2ea-091c-4cab-a2e6-d6b677469507`

### Изпращане

```bash
curl -X POST "https://{baseUrl}/viber/2/messages" \
  -H "Authorization: App {api-key}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "sender": "{sender}",
        "destinations": [{ "to": "{recipient}" }],
        "content": {
          "type": "TEMPLATE",
          "templateId": "d9b4f2ea-091c-4cab-a2e6-d6b677469507",
          "language": "bg",
          "parameters": {
            "car": "CA1234AB Toyota Corolla",
            "order_number": "WO-2026-00123",
            "service_center": "АвтоСервиз София",
            "phone1": "02 800 0000",
            "phone2": "0888 123 456"
          }
        },
        "options": {
          "smsFailover": {
            "from": "{sms-sender}",
            "text": "За CA1234AB Toyota Corolla има поръчка WO-2026-00123 за АвтоСервиз София. Запишете час на тел.: 02 800 0000 / 0888 123 456. Алианц България."
          }
        }
      }
    ]
  }'
```

---
