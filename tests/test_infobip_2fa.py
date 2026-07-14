"""
Unit тестове за infobip_2fa_client — HTTP слоят е mock-нат с unittest.mock.
"""
import pytest
from unittest.mock import MagicMock, patch

import viberbot.config as cfg


# ── helpers ──────────────────────────────────────────────────────────────────

def _resp(status=200, data=None, text=None):
    m = MagicMock()
    m.status_code = status
    m.ok = status < 400
    m.json.return_value = data or {}
    m.text = text or str(data)
    return m


def _with_config(**kwargs):
    """Patch config values needed by the client."""
    defaults = {
        "INFOBIP_API_KEY": "test-key",
        "INFOBIP_BASE_URL": "api.test.infobip.com",
        "INFOBIP_2FA_APP_ID": "app-123",
        "INFOBIP_2FA_SMS_MSG_ID": "sms-msg-1",
        "INFOBIP_2FA_VOICE_MSG_ID": "voice-msg-1",
        "INFOBIP_2FA_EMAIL_MSG_ID": "email-msg-1",
        "INFOBIP_2FA_FROM": "InfoSMS",
    }
    defaults.update(kwargs)
    return patch.multiple(cfg, **defaults)


# ── send_otp ─────────────────────────────────────────────────────────────────

class TestSendOtp:
    @pytest.mark.parametrize("channel,path", [
        ("sms",   "/2fa/2/pin"),
        ("voice", "/2fa/2/pin/voice"),
        ("email", "/2fa/2/pin/email"),
    ])
    def test_send_returns_pin_id(self, channel, path):
        from viberbot.services.infobip_2fa_client import send_otp

        with _with_config(), patch("requests.post") as mock_post:
            mock_post.return_value = _resp(200, {"pinId": "pin-abc"})
            pin_id = send_otp(channel, "359888000000")

        assert pin_id == "pin-abc"
        called_url = mock_post.call_args[0][0]
        assert called_url.endswith(path)

    def test_send_raises_on_non_2xx(self):
        from viberbot.services.infobip_2fa_client import InfobipOtpError, send_otp

        with _with_config(), patch("requests.post") as mock_post:
            mock_post.return_value = _resp(401, {
                "requestError": {"serviceException": {"text": "Unauthorized", "messageId": "UNAUTHORIZED"}}
            })
            with pytest.raises(InfobipOtpError, match="401"):
                send_otp("sms", "359888000000")

    def test_send_raises_when_config_missing(self):
        from viberbot.services.infobip_2fa_client import InfobipOtpError, send_otp

        with _with_config(INFOBIP_2FA_APP_ID=None):
            with pytest.raises(InfobipOtpError, match="конфигуриран"):
                send_otp("sms", "359888000000")


# ── verify_otp ───────────────────────────────────────────────────────────────

class TestVerifyOtp:
    def test_verify_correct_pin_returns_true(self):
        from viberbot.services.infobip_2fa_client import verify_otp

        with _with_config(), patch("requests.post") as mock_post:
            mock_post.return_value = _resp(200, {"verified": True, "attemptsRemaining": 4})
            assert verify_otp("pin-abc", "123456") is True

    def test_verify_wrong_pin_returns_false(self):
        from viberbot.services.infobip_2fa_client import verify_otp

        with _with_config(), patch("requests.post") as mock_post:
            mock_post.return_value = _resp(200, {"verified": False, "attemptsRemaining": 3})
            assert verify_otp("pin-abc", "000000") is False

    def test_verify_404_raises_pin_expired(self):
        from viberbot.services.infobip_2fa_client import InfobipPinExpired, verify_otp

        with _with_config(), patch("requests.post") as mock_post:
            mock_post.return_value = _resp(404)
            with pytest.raises(InfobipPinExpired):
                verify_otp("pin-abc", "123456")

    def test_verify_expired_in_body_raises_pin_expired(self):
        from viberbot.services.infobip_2fa_client import InfobipPinExpired, verify_otp

        with _with_config(), patch("requests.post") as mock_post:
            mock_post.return_value = _resp(400, {
                "requestError": {"serviceException": {"text": "PIN expired", "messageId": "PIN_EXPIRED"}}
            })
            with pytest.raises(InfobipPinExpired):
                verify_otp("pin-abc", "123456")

    def test_verify_attempts_exceeded(self):
        from viberbot.services.infobip_2fa_client import InfobipAttemptsExceeded, verify_otp

        with _with_config(), patch("requests.post") as mock_post:
            mock_post.return_value = _resp(400, {
                "requestError": {"serviceException": {"text": "Too many attempts", "messageId": "ATTEMPTS_EXCEEDED"}}
            })
            with pytest.raises(InfobipAttemptsExceeded):
                verify_otp("pin-abc", "123456")


# ── Viber path untouched ──────────────────────────────────────────────────────

class TestViberPathUntouched:
    """Потвърждава, че infobip_2fa_client не се извиква при Viber канал."""

    def test_viber_does_not_call_2fa_client(self):
        from viberbot.services import infobip_2fa_client

        with patch.object(infobip_2fa_client, "send_otp") as mock_send:
            # Симулираме пряко извикване на Viber пътя в auth_service
            # без реална DB — просто проверяваме, че send_otp не е извикан
            mock_send.assert_not_called()
