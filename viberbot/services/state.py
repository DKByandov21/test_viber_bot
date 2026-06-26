from datetime import datetime, timedelta, timezone

from viberbot import config
from viberbot.db import Conversation, ConversationSession, Template, db


def _now():
    return datetime.now(timezone.utc)


def is_active(updated_at):
    if not updated_at:
        return False
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    return _now() - updated_at < timedelta(minutes=config.CONVERSATION_TIMEOUT_MINUTES)


def _get_or_create(sender):
    convo = Conversation.query.filter_by(sender=sender).first()
    if not convo:
        convo = Conversation(sender=sender, history=[], agent_mode=False)
        db.session.add(convo)
        db.session.commit()
    return convo


def get_history(sender):
    convo = Conversation.query.filter_by(sender=sender).first()
    return convo.history if convo else []


def _archive_session(convo):
    """Snapshots the current history into conversation_sessions before it's
    cleared, so past sessions stay browsable instead of being lost."""
    if not convo.history:
        return
    started_at = None
    first_at = convo.history[0].get("at") if convo.history else None
    if first_at:
        started_at = datetime.fromisoformat(first_at)
    db.session.add(ConversationSession(
        sender=convo.sender,
        channel=convo.channel,
        history=convo.history,
        started_at=started_at,
        ended_at=convo.updated_at or _now(),
    ))


def ensure_fresh_session(sender):
    """If the conversation went quiet for longer than the timeout, archive the
    old history and start a brand new session (keeps agent_mode off)."""
    convo = Conversation.query.filter_by(sender=sender).first()
    if convo and convo.history and not is_active(convo.updated_at):
        _archive_session(convo)
        convo.history = []
        convo.agent_mode = False
        db.session.commit()


def append_history(sender, user_message, assistant_reply):
    convo = _get_or_create(sender)
    history = list(convo.history or [])
    now = _now().isoformat()
    history.append({"role": "user", "content": user_message, "at": now})
    history.append({"role": "assistant", "content": assistant_reply, "at": now})
    convo.history = history[-config.MAX_HISTORY_MESSAGES:]
    db.session.commit()


def append_user_message(sender, text):
    convo = _get_or_create(sender)
    history = list(convo.history or [])
    history.append({"role": "user", "content": text, "at": _now().isoformat()})
    convo.history = history[-config.MAX_HISTORY_MESSAGES:]
    db.session.commit()


def append_assistant_note(sender, content):
    convo = _get_or_create(sender)
    history = list(convo.history or [])
    history.append({"role": "assistant", "content": content, "at": _now().isoformat()})
    convo.history = history[-config.MAX_HISTORY_MESSAGES:]
    db.session.commit()


def append_agent_message(sender, content):
    convo = _get_or_create(sender)
    history = list(convo.history or [])
    history.append({"role": "agent", "content": content, "at": _now().isoformat()})
    convo.history = history[-config.MAX_HISTORY_MESSAGES:]
    db.session.commit()


def is_agent_mode(sender):
    convo = Conversation.query.filter_by(sender=sender).first()
    return bool(convo and convo.agent_mode)


def set_agent_mode(sender, enabled):
    convo = _get_or_create(sender)
    convo.agent_mode = enabled
    db.session.commit()


def get_channel(sender):
    convo = Conversation.query.filter_by(sender=sender).first()
    return convo.channel if convo else "VIBER_BOT"


def set_channel(sender, channel):
    convo = _get_or_create(sender)
    if convo.channel != channel:
        convo.channel = channel
        db.session.commit()


def clear_conversation(sender):
    convo = Conversation.query.filter_by(sender=sender).first()
    if convo:
        _archive_session(convo)
        convo.history = []
        convo.agent_mode = False
        db.session.commit()


def list_sessions(sender):
    return [
        s.to_dict() for s in
        ConversationSession.query.filter_by(sender=sender).order_by(ConversationSession.ended_at.desc()).all()
    ]


def get_session(session_id):
    s = ConversationSession.query.get(session_id)
    return s.to_dict() if s else None


def get_stats():
    conversations = Conversation.query.all()
    sessions = ConversationSession.query.all()

    today = _now().date()

    def count_messages(history, role=None):
        if not role:
            return len(history)
        return sum(1 for m in history if m.get("role") == role)

    def is_today(msg_at):
        if not msg_at:
            return False
        try:
            return datetime.fromisoformat(msg_at).date() == today
        except ValueError:
            return False

    total_messages = 0
    messages_today = 0
    agent_handled = 0
    ai_only = 0

    all_histories = [c.history or [] for c in conversations] + [s.history or [] for s in sessions]

    for history in all_histories:
        total_messages += len(history)
        messages_today += sum(1 for m in history if is_today(m.get("at")))
        if any(m.get("role") == "agent" for m in history):
            agent_handled += 1
        elif history:
            ai_only += 1

    return {
        "total_customers": len(conversations),
        "total_sessions": len(sessions) + sum(1 for c in conversations if c.history),
        "total_messages": total_messages,
        "messages_today": messages_today,
        "agent_handled_sessions": agent_handled,
        "ai_only_sessions": ai_only,
        "agent_queue_count": sum(1 for c in conversations if c.agent_mode),
        "active_now": sum(1 for c in conversations if is_active(c.updated_at)),
    }


def list_conversations():
    return [c.to_dict() for c in Conversation.query.order_by(Conversation.updated_at.desc()).all()]


def list_agent_queue():
    return [c.to_dict() for c in Conversation.query.filter_by(agent_mode=True).all()]


def list_templates():
    return [t.to_dict() for t in Template.query.order_by(Template.key).all()]


def get_template(key):
    t = Template.query.filter_by(key=key).first()
    return t.to_dict() if t else None


def upsert_template(key, template_id, language, params, description=None):
    t = Template.query.filter_by(key=key).first()
    if not t:
        t = Template(key=key)
        db.session.add(t)
    t.template_id = template_id
    t.language = language
    t.params = params
    t.description = description
    db.session.commit()
    return t.to_dict()


def delete_template(key):
    t = Template.query.filter_by(key=key).first()
    if t:
        db.session.delete(t)
        db.session.commit()
        return True
    return False
