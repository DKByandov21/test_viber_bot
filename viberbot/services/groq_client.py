import requests

from viberbot import config
from viberbot.services.knowledge_base import find_relevant_chunks


def ask_groq(sender, user_message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    relevant_chunks = find_relevant_chunks(user_message)
    if relevant_chunks:
        context = "\n\n---\n\n".join(relevant_chunks)
        user_content = f"Контекст от Infobip документация:\n{context}\n\nВъпрос: {user_message}"
    else:
        user_content = user_message

    history = config.CONVERSATIONS.get(sender, [])
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_content}]

    payload = {
        "model": config.GROQ_MODEL,
        "messages": messages,
        "max_tokens": 250
    }
    print(f"Calling Groq with model: {config.GROQ_MODEL}, with {len(relevant_chunks)} knowledge chunks, {len(history)} history messages")
    response = requests.post(url, headers=headers, json=payload)
    print(f"Groq status: {response.status_code}")
    print(f"Groq response: {response.text}")
    reply = response.json()["choices"][0]["message"]["content"][:config.VIBER_TEXT_LIMIT]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    config.CONVERSATIONS[sender] = history[-config.MAX_HISTORY_MESSAGES:]

    return reply


def remember_notification(to, context_summary):
    if not context_summary:
        return
    history = config.CONVERSATIONS.get(to, [])
    history.append({"role": "assistant", "content": context_summary})
    config.CONVERSATIONS[to] = history[-config.MAX_HISTORY_MESSAGES:]
