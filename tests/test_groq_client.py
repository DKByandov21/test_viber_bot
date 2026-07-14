"""
Unit тестове за ask_groq — проверяват channel-базираното поведение:
VBM не ползва knowledge base, VIBER_BOT я ползва.
"""
from unittest.mock import MagicMock, patch


def _groq_response(reply="AI отговор"):
    m = MagicMock()
    m.status_code = 200
    m.text = "{}"
    m.json.return_value = {"choices": [{"message": {"content": reply}}]}
    return m


def _run_ask_groq(channel, history=None):
    from viberbot.services.groq_client import ask_groq

    with patch("viberbot.services.groq_client.find_relevant_chunks") as mock_chunks, \
         patch("viberbot.services.groq_client.state") as mock_state, \
         patch("viberbot.services.groq_client.requests.post") as mock_post:
        mock_chunks.return_value = ["chunk от документацията"]
        mock_state.get_history.return_value = history or []
        mock_post.return_value = _groq_response()

        reply = ask_groq("sender_x", "какво е това", channel)
        payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")

    return reply, mock_chunks, payload


class TestVbmPath:
    def test_vbm_skips_knowledge_base(self):
        _, mock_chunks, _ = _run_ask_groq("VIBER_BM")
        mock_chunks.assert_not_called()

    def test_vbm_uses_vbm_system_prompt(self):
        from viberbot import config

        _, _, payload = _run_ask_groq("VIBER_BM")
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][0]["content"] == config.VBM_SYSTEM_PROMPT

    def test_vbm_user_message_sent_without_doc_context(self):
        _, _, payload = _run_ask_groq("VIBER_BM")
        assert payload["messages"][-1]["content"] == "какво е това"

    def test_vbm_notification_context_stays_in_history(self):
        history = [{"role": "assistant", "content": "Изпратено известие: пратка 12 очаква получаване."}]
        _, _, payload = _run_ask_groq("VIBER_BM", history=history)
        assert any("пратка 12" in m["content"] for m in payload["messages"])


class TestViberBotPath:
    def test_bot_uses_knowledge_base(self):
        _, mock_chunks, payload = _run_ask_groq("VIBER_BOT")
        mock_chunks.assert_called_once()
        assert "Контекст от Infobip документация" in payload["messages"][-1]["content"]

    def test_bot_uses_default_system_prompt(self):
        from viberbot import config

        _, _, payload = _run_ask_groq("VIBER_BOT")
        assert payload["messages"][0]["content"] == config.SYSTEM_PROMPT
