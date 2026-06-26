import secrets

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    role = db.Column(db.String(16), nullable=False, default="agent")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {"id": self.id, "email": self.email, "phone": self.phone, "role": self.role}


class OtpCode(db.Model):
    __tablename__ = "otp_codes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True, default=lambda: secrets.token_urlsafe(32))
    expires_at = db.Column(db.DateTime, nullable=False)


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(128), unique=True, nullable=False, index=True)
    history = db.Column(db.JSON, nullable=False, default=list)
    agent_mode = db.Column(db.Boolean, nullable=False, default=False)
    channel = db.Column(db.String(32), nullable=False, default="VIBER_BOT")
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        from viberbot.services.state import is_active

        return {
            "sender": self.sender,
            "history": self.history,
            "agent_mode": self.agent_mode,
            "channel": self.channel,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": is_active(self.updated_at),
        }


class ConversationSession(db.Model):
    """Archived snapshot of a conversation's history once it times out, so the
    live Conversation row can start a fresh session without losing the log."""
    __tablename__ = "conversation_sessions"

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(128), nullable=False, index=True)
    channel = db.Column(db.String(32), nullable=False, default="VIBER_BOT")
    history = db.Column(db.JSON, nullable=False, default=list)
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "channel": self.channel,
            "history": self.history,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }


class Template(db.Model):
    __tablename__ = "templates"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    template_id = db.Column(db.String(128), nullable=False)
    language = db.Column(db.String(8), nullable=False, default="bg")
    params = db.Column(db.JSON, nullable=False, default=list)
    description = db.Column(db.String(512), nullable=True)

    def to_dict(self):
        return {
            "key": self.key,
            "id": self.template_id,
            "language": self.language,
            "params": self.params,
            "description": self.description,
        }


DEFAULT_TEMPLATES = [
    {
        "key": "order_confirmation",
        "template_id": "bb862b91-b6f0-4e1c-a31e-ebdcc822b240",
        "language": "bg",
        "params": ["1", "2", "3", "4", "5"],
        "description": "name, order_id, item, amount, delivery_address - confirmed working via API"
    },
    {
        "key": "otp",
        "template_id": "5fafdcbe-8f81-4116-a14f-fabedb38b194",
        "language": "en",
        "params": ["pin"],
        "description": None,
    },
    {
        "key": "euromaster",
        "template_id": "97510a1e-11c6-4748-b4f4-b9c78e1a7b6b",
        "language": "bg",
        "params": ["First_name"],
        "description": "rich media (image + button) - operator rejects via API, use Broadcast instead"
    },
]


def seed_default_templates():
    """Only seeds on a completely empty table - once the user manages templates
    (including deleting one of the defaults), redeploys must not resurrect them."""
    if Template.query.count() > 0:
        return
    for entry in DEFAULT_TEMPLATES:
        db.session.add(Template(**entry))
    db.session.commit()


def promote_first_user_to_admin():
    """Guarantees there's always at least one admin: if none exists yet,
    promote whoever registered first."""
    if User.query.filter_by(role="admin").first():
        return
    first_user = User.query.order_by(User.created_at.asc()).first()
    if first_user:
        first_user.role = "admin"
        db.session.commit()


def init_db(app):
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        print("DATABASE_URL not set - skipping DB initialization")
        return
    db.init_app(app)
    try:
        with app.app_context():
            db.create_all()
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS channel VARCHAR(32) NOT NULL DEFAULT 'VIBER_BOT'"
                ))
                conn.execute(db.text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(16) NOT NULL DEFAULT 'agent'"
                ))
                conn.commit()
            seed_default_templates()
            promote_first_user_to_admin()
    except Exception as e:
        print(f"DB initialization failed, continuing without it: {e}")
