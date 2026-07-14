import requests

from viberbot import config
from viberbot.services import state
from viberbot.services.knowledge_base import find_relevant_chunks


def ask_groq(sender, user_message, channel="VIBER_BOT"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # VBM conversations start from a template notification we sent - the AI
    # should answer about that notification, not consult the Infobip docs
    # knowledge base. The notification context is stored on the conversation
    # row (not in history) so it survives session archiving.
    if channel == "VIBER_BM":
        relevant_chunks = []
        system_prompt = config.VBM_SYSTEM_PROMPT
        last_notification = state.get_last_notification(sender)
        if last_notification:
            system_prompt += f"\n\nПоследно изпратено известие до този клиент: {last_notification}"
        user_content = user_message
    else:
        relevant_chunks = find_relevant_chunks(user_message)
        system_prompt = config.SYSTEM_PROMPT
        if relevant_chunks:
            context = "\n\n---\n\n".join(relevant_chunks)
            user_content = f"Контекст от Infobip документация:\n{context}\n\nВъпрос: {user_message}"
        else:
            user_content = user_message

    history = state.get_history(sender)
    # Groq's API only accepts system/user/assistant roles - "agent" (a human
    # support agent's message) gets relabeled as assistant for the AI's context.
    clean_history = [
        {"role": "assistant" if m["role"] == "agent" else m["role"], "content": m["content"]}
        for m in history
    ]
    messages = [{"role": "system", "content": system_prompt}] + clean_history + [{"role": "user", "content": user_content}]

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

    state.append_history(sender, user_message, reply)

    return reply


def remember_notification(to, context_summary):
    if context_summary:
        # Durable copy for the AI (survives session resets) + a history note
        # so the agent sees what was sent when browsing the conversation.
        state.set_last_notification(to, context_summary)
        state.append_assistant_note(to, context_summary)
