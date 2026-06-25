from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(128), unique=True, nullable=False, index=True)
    history = db.Column(db.JSON, nullable=False, default=list)
    agent_mode = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            "sender": self.sender,
            "history": self.history,
            "agent_mode": self.agent_mode,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
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
    for entry in DEFAULT_TEMPLATES:
        if not Template.query.filter_by(key=entry["key"]).first():
            db.session.add(Template(**entry))
    db.session.commit()


def init_db(app):
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        print("DATABASE_URL not set - skipping DB initialization")
        return
    db.init_app(app)
    try:
        with app.app_context():
            db.create_all()
            seed_default_templates()
    except Exception as e:
        print(f"DB initialization failed, continuing without it: {e}")
