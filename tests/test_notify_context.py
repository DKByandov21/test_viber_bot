"""
Unit тестове за _summarize_raw_message — контекстът, който VBM AI получава
след изпращане на template през /notify/raw.
"""
from viberbot.routes.notify import _summarize_raw_message


class TestSummarizeRawMessage:
    def test_template_with_placeholders(self):
        message = {
            "channel": "VIBER_BM",
            "template": {"templateName": "express_one_pickup", "language": "bg"},
            "destinations": [{"to": "359888000000"}],
            "content": {"body": {"type": "TEXT", "pickup_place": "Офис 12", "deadline": "20.07"}},
        }
        summary = _summarize_raw_message(message)
        assert "express_one_pickup" in summary
        assert "Офис 12" in summary
        assert "deadline: 20.07" in summary
        assert "type" not in summary

    def test_template_without_placeholders(self):
        message = {
            "template": {"templateName": "greeting", "language": "bg"},
            "content": {"body": {"type": "TEXT"}},
        }
        summary = _summarize_raw_message(message)
        assert summary == "Изпратено известие по template 'greeting'."

    def test_non_template_message_returns_none(self):
        message = {
            "channel": "VIBER_BM",
            "content": {"body": {"type": "TEXT", "text": "здравей"}},
        }
        assert _summarize_raw_message(message) is None
