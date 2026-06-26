from datetime import datetime, timedelta, timezone

from viberbot import config
from viberbot.db import Conversation, Template, db


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


def ensure_fresh_session(sender):
    """If the conversation went quiet for longer than the timeout, treat the
    next message as a brand new session (clears AI memory, keeps agent_mode off)."""
    convo = Conversation.query.filter_by(sender=sender).first()
    if convo and convo.history and not is_active(convo.updated_at):
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
        convo.history = []
        convo.agent_mode = False
        db.session.commit()


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
