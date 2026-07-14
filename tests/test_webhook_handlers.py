"""
Unit тестове за webhook_handlers — DB и HTTP слоевете са mock-нати.
"""
import pytest
from unittest.mock import MagicMock, call, patch


def _make_patches(agent_mode=False, channel="VIBER_BM"):
    """Returns a dict of patches needed for webhook handler tests."""
    return {
        "viberbot.handlers.webhook_handlers.state.set_channel": MagicMock(),
        "viberbot.handlers.webhook_handlers.state.ensure_fresh_session": MagicMock(),
        "viberbot.handlers.webhook_handlers.state.is_agent_mode": MagicMock(return_value=agent_mode),
        "viberbot.handlers.webhook_handlers.state.set_agent_mode": MagicMock(),
        "viberbot.handlers.webhook_handlers.state.clear_conversation": MagicMock(),
        "viberbot.handlers.webhook_handlers.state.append_user_message": MagicMock(),
        "viberbot.handlers.webhook_handlers.state.append_assistant_note": MagicMock(),
        "viberbot.handlers.webhook_handlers.state.get_channel": MagicMock(return_value=channel),
        "viberbot.handlers.webhook_handlers.send_sms_notification": MagicMock(),
        "viberbot.handlers.webhook_handlers.reply_on_same_channel": MagicMock(),
        "viberbot.handlers.webhook_handlers.ask_groq": MagicMock(return_value="AI reply"),
    }


# ── VBM keyword → agent handoff ───────────────────────────────────────────────

class TestVbmAgentKeywords:
    @pytest.mark.parametrize("text", [
        "агент",
        "Агент",
        "АГЕНТ",
        "искам агент",
        "оператор",
        "служител",
        "жив човек",
        "agent",
    ])
    def test_agent_keyword_activates_agent_mode(self, text):
        from viberbot.handlers.webhook_handlers import handle_text_message

        patches = _make_patches()
        with patch.multiple("viberbot.handlers.webhook_handlers", **{
            k.split(".")[-1]: v for k, v in patches.items()
            if "state." not in k
        }), patch.multiple(
            "viberbot.handlers.webhook_handlers.state",
            set_channel=patches["viberbot.handlers.webhook_handlers.state.set_channel"],
            ensure_fresh_session=patches["viberbot.handlers.webhook_handlers.state.ensure_fresh_session"],
            is_agent_mode=patches["viberbot.handlers.webhook_handlers.state.is_agent_mode"],
            set_agent_mode=patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"],
            clear_conversation=patches["viberbot.handlers.webhook_handlers.state.clear_conversation"],
            append_user_message=patches["viberbot.handlers.webhook_handlers.state.append_user_message"],
            append_assistant_note=patches["viberbot.handlers.webhook_handlers.state.append_assistant_note"],
        ):
            handle_text_message("test_sender", "VIBER_BM", text)

        patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"].assert_called_once_with("test_sender", True)
        patches["viberbot.handlers.webhook_handlers.reply_on_same_channel"].assert_called_once()
        patches["viberbot.handlers.webhook_handlers.send_sms_notification"].assert_called_once()
        patches["viberbot.handlers.webhook_handlers.ask_groq"].assert_not_called()
        # The trigger message itself must be logged so the agent sees it.
        patches["viberbot.handlers.webhook_handlers.state.append_user_message"].assert_called_once_with("test_sender", text)

    @pytest.mark.parametrize("text", ["край", "стоп", "довиждане", "end", "stop"])
    def test_end_chat_keyword_clears_conversation(self, text):
        from viberbot.handlers.webhook_handlers import handle_text_message

        patches = _make_patches()
        with patch.multiple("viberbot.handlers.webhook_handlers", **{
            k.split(".")[-1]: v for k, v in patches.items()
            if "state." not in k
        }), patch.multiple(
            "viberbot.handlers.webhook_handlers.state",
            set_channel=patches["viberbot.handlers.webhook_handlers.state.set_channel"],
            ensure_fresh_session=patches["viberbot.handlers.webhook_handlers.state.ensure_fresh_session"],
            is_agent_mode=patches["viberbot.handlers.webhook_handlers.state.is_agent_mode"],
            set_agent_mode=patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"],
            clear_conversation=patches["viberbot.handlers.webhook_handlers.state.clear_conversation"],
            append_user_message=patches["viberbot.handlers.webhook_handlers.state.append_user_message"],
            append_assistant_note=patches["viberbot.handlers.webhook_handlers.state.append_assistant_note"],
        ):
            handle_text_message("test_sender", "VIBER_BM", text)

        patches["viberbot.handlers.webhook_handlers.state.clear_conversation"].assert_called_once_with("test_sender")
        patches["viberbot.handlers.webhook_handlers.ask_groq"].assert_not_called()

    def test_normal_message_goes_to_ai(self):
        from viberbot.handlers.webhook_handlers import handle_text_message

        patches = _make_patches()
        with patch.multiple("viberbot.handlers.webhook_handlers", **{
            k.split(".")[-1]: v for k, v in patches.items()
            if "state." not in k
        }), patch.multiple(
            "viberbot.handlers.webhook_handlers.state",
            set_channel=patches["viberbot.handlers.webhook_handlers.state.set_channel"],
            ensure_fresh_session=patches["viberbot.handlers.webhook_handlers.state.ensure_fresh_session"],
            is_agent_mode=patches["viberbot.handlers.webhook_handlers.state.is_agent_mode"],
            set_agent_mode=patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"],
            clear_conversation=patches["viberbot.handlers.webhook_handlers.state.clear_conversation"],
            append_user_message=patches["viberbot.handlers.webhook_handlers.state.append_user_message"],
            append_assistant_note=patches["viberbot.handlers.webhook_handlers.state.append_assistant_note"],
        ):
            handle_text_message("test_sender", "VIBER_BM", "Какво е Infobip?")

        patches["viberbot.handlers.webhook_handlers.ask_groq"].assert_called_once()
        patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"].assert_not_called()
        # VBM replies always carry the agent hint (no buttons on that channel).
        sent_text = patches["viberbot.handlers.webhook_handlers.reply_on_same_channel"].call_args[0][2]
        assert "искам агент" in sent_text

    def test_bot_reply_has_no_agent_hint(self):
        from viberbot.handlers.webhook_handlers import handle_text_message

        patches = _make_patches()
        with patch.multiple("viberbot.handlers.webhook_handlers", **{
            k.split(".")[-1]: v for k, v in patches.items()
            if "state." not in k
        }), patch.multiple(
            "viberbot.handlers.webhook_handlers.state",
            set_channel=patches["viberbot.handlers.webhook_handlers.state.set_channel"],
            ensure_fresh_session=patches["viberbot.handlers.webhook_handlers.state.ensure_fresh_session"],
            is_agent_mode=patches["viberbot.handlers.webhook_handlers.state.is_agent_mode"],
            set_agent_mode=patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"],
            clear_conversation=patches["viberbot.handlers.webhook_handlers.state.clear_conversation"],
            append_user_message=patches["viberbot.handlers.webhook_handlers.state.append_user_message"],
            append_assistant_note=patches["viberbot.handlers.webhook_handlers.state.append_assistant_note"],
        ):
            handle_text_message("test_sender", "VIBER_BOT", "Какво е Infobip?")

        sent_text = patches["viberbot.handlers.webhook_handlers.reply_on_same_channel"].call_args[0][2]
        assert "искам агент" not in sent_text

    def test_vbm_reply_with_hint_respects_text_limit(self):
        from viberbot import config
        from viberbot.handlers.webhook_handlers import handle_text_message

        patches = _make_patches()
        patches["viberbot.handlers.webhook_handlers.ask_groq"] = MagicMock(return_value="х" * config.VIBER_TEXT_LIMIT)
        with patch.multiple("viberbot.handlers.webhook_handlers", **{
            k.split(".")[-1]: v for k, v in patches.items()
            if "state." not in k
        }), patch.multiple(
            "viberbot.handlers.webhook_handlers.state",
            set_channel=patches["viberbot.handlers.webhook_handlers.state.set_channel"],
            ensure_fresh_session=patches["viberbot.handlers.webhook_handlers.state.ensure_fresh_session"],
            is_agent_mode=patches["viberbot.handlers.webhook_handlers.state.is_agent_mode"],
            set_agent_mode=patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"],
            clear_conversation=patches["viberbot.handlers.webhook_handlers.state.clear_conversation"],
            append_user_message=patches["viberbot.handlers.webhook_handlers.state.append_user_message"],
            append_assistant_note=patches["viberbot.handlers.webhook_handlers.state.append_assistant_note"],
        ):
            handle_text_message("test_sender", "VIBER_BM", "Кога пристига пратката?")

        sent_text = patches["viberbot.handlers.webhook_handlers.reply_on_same_channel"].call_args[0][2]
        assert len(sent_text) <= config.VIBER_TEXT_LIMIT
        assert sent_text.endswith(config.VBM_AGENT_HINT)

    def test_message_in_agent_mode_logs_without_ai(self):
        from viberbot.handlers.webhook_handlers import handle_text_message

        patches = _make_patches(agent_mode=True)
        with patch.multiple("viberbot.handlers.webhook_handlers", **{
            k.split(".")[-1]: v for k, v in patches.items()
            if "state." not in k
        }), patch.multiple(
            "viberbot.handlers.webhook_handlers.state",
            set_channel=patches["viberbot.handlers.webhook_handlers.state.set_channel"],
            ensure_fresh_session=patches["viberbot.handlers.webhook_handlers.state.ensure_fresh_session"],
            is_agent_mode=patches["viberbot.handlers.webhook_handlers.state.is_agent_mode"],
            set_agent_mode=patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"],
            clear_conversation=patches["viberbot.handlers.webhook_handlers.state.clear_conversation"],
            append_user_message=patches["viberbot.handlers.webhook_handlers.state.append_user_message"],
            append_assistant_note=patches["viberbot.handlers.webhook_handlers.state.append_assistant_note"],
        ):
            handle_text_message("test_sender", "VIBER_BM", "Здравейте, кога ще отговорите?")

        patches["viberbot.handlers.webhook_handlers.state.append_user_message"].assert_called_once_with(
            "test_sender", "Здравейте, кога ще отговорите?"
        )
        patches["viberbot.handlers.webhook_handlers.ask_groq"].assert_not_called()
        patches["viberbot.handlers.webhook_handlers.reply_on_same_channel"].assert_not_called()


# ── SMS нотификация съдържа channel label ─────────────────────────────────────

class TestChannelLabelInSms:
    def _trigger_contact_agent(self, channel):
        from viberbot.handlers.webhook_handlers import handle_button_reply

        patches = _make_patches(channel=channel)
        mock_sms = patches["viberbot.handlers.webhook_handlers.send_sms_notification"]
        with patch.multiple("viberbot.handlers.webhook_handlers", **{
            k.split(".")[-1]: v for k, v in patches.items()
            if "state." not in k
        }), patch.multiple(
            "viberbot.handlers.webhook_handlers.state",
            set_channel=patches["viberbot.handlers.webhook_handlers.state.set_channel"],
            ensure_fresh_session=patches["viberbot.handlers.webhook_handlers.state.ensure_fresh_session"],
            is_agent_mode=patches["viberbot.handlers.webhook_handlers.state.is_agent_mode"],
            set_agent_mode=patches["viberbot.handlers.webhook_handlers.state.set_agent_mode"],
            clear_conversation=patches["viberbot.handlers.webhook_handlers.state.clear_conversation"],
            append_user_message=patches["viberbot.handlers.webhook_handlers.state.append_user_message"],
            append_assistant_note=patches["viberbot.handlers.webhook_handlers.state.append_assistant_note"],
        ):
            handle_button_reply("sender_x", channel, "CONTACT_AGENT")
        return mock_sms

    def test_vbm_label_in_sms(self):
        mock_sms = self._trigger_contact_agent("VIBER_BM")
        sms_text = mock_sms.call_args[0][1]
        assert "VBM" in sms_text

    def test_bot_label_in_sms(self):
        mock_sms = self._trigger_contact_agent("VIBER_BOT")
        sms_text = mock_sms.call_args[0][1]
        assert "Viber Bot" in sms_text
