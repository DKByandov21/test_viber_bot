import random
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from viberbot.db import OtpCode, Session, User, db
from viberbot.services.infobip_client import send_template_notification

OTP_TTL_MINUTES = 5
SESSION_TTL_DAYS = 7


class AuthError(Exception):
    pass


def register(email, password, phone):
    email = email.strip().lower()
    if User.query.filter_by(email=email).first():
        raise AuthError("Имейлът вече е регистриран")

    user = User(email=email, password_hash=generate_password_hash(password, method="pbkdf2:sha256"), phone=phone)
    db.session.add(user)
    db.session.commit()
    return user


def start_login(email, password):
    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        raise AuthError("Грешен имейл или парола")

    code = f"{random.randint(0, 999999):06d}"
    otp = OtpCode(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_TTL_MINUTES),
    )
    db.session.add(otp)
    db.session.commit()

    send_template_notification(user.phone, template_name="5fafdcbe-8f81-4116-a14f-fabedb38b194", language="en", placeholders={"pin": code})

    return otp.id


def verify_otp(otp_id, code):
    otp = OtpCode.query.get(otp_id)
    if not otp or otp.used or otp.expires_at < datetime.utcnow() or otp.code != code:
        raise AuthError("Невалиден или изтекъл код")

    otp.used = True
    session = Session(
        user_id=otp.user_id,
        expires_at=datetime.utcnow() + timedelta(days=SESSION_TTL_DAYS),
    )
    db.session.add(session)
    db.session.commit()

    return session.token, User.query.get(otp.user_id)


def get_user_from_token(token):
    if not token:
        return None
    session = Session.query.filter_by(token=token).first()
    if not session or session.expires_at < datetime.utcnow():
        return None
    return User.query.get(session.user_id)


def update_profile(user, phone=None, current_password=None, new_password=None):
    if new_password:
        if not current_password or not check_password_hash(user.password_hash, current_password):
            raise AuthError("Грешна текуща парола")
        user.password_hash = generate_password_hash(new_password, method="pbkdf2:sha256")

    if phone:
        user.phone = phone

    db.session.commit()
    return user
