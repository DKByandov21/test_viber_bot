"""
Unit тестове за контекста, който VBM AI получава след изпращане на template
през /notify/raw — реалният текст на съобщението, не технически данни.
"""
from unittest.mock import patch

from viberbot.routes.notify import _build_notification_context, _summarize_raw_message


EXPRESS_ONE_BODY = (
    "Express One Пратка за получаване {{tovar}} в доставящ партньор {{office}} "
    "Срок за получаване до {{data}}. За точен адрес и работно време посетете {{link}} "
    "Поздрави и успешен ден."
)


class TestSummarizeRawMessage:
    def test_renders_actual_message_text(self):
        message = {
            "channel": "VIBER_BM",
            "template": {"templateName": "08714a48-f238-44aa-8a09-df6d9e808946", "language": "bg"},
            "destinations": [{"to": "359888000000"}],
            "content": {"body": {
                "type": "TEXT", "tovar": "123", "office": "Офис 12",
                "data": "20.07", "link": "https://exp.bg",
            }},
        }
        with patch("viberbot.routes.notify.get_rendered_template_text") as mock_get:
            mock_get.return_value = (
                "Express One Пратка за получаване 123 в доставящ партньор Офис 12 "
                "Срок за получаване до 20.07. За точен адрес и работно време посетете "
                "https://exp.bg Поздрави и успешен ден."
            )
            summary = _summarize_raw_message(message)

        assert summary.startswith('Клиентът получи следното съобщение: "Express One')
        assert "123" in summary and "Офис 12" in summary
        # Никакви технически термини в контекста
        assert "template" not in summary
        assert "08714a48" not in summary

    def test_falls_back_to_placeholders_when_template_unavailable(self):
        message = {
            "template": {"templateName": "greeting", "language": "bg"},
            "content": {"body": {"type": "TEXT", "name": "Иван"}},
        }
        with patch("viberbot.routes.notify.get_rendered_template_text", return_value=None):
            summary = _summarize_raw_message(message)

        assert "greeting" in summary
        assert "name: Иван" in summary

    def test_non_template_message_returns_none(self):
        message = {
            "channel": "VIBER_BM",
            "content": {"body": {"type": "TEXT", "text": "здравей"}},
        }
        assert _summarize_raw_message(message) is None


class TestRenderedTemplateText:
    def test_placeholder_substitution(self):
        from viberbot.services.infobip_client import get_rendered_template_text

        api_response = {
            "templates": [{
                "templateId": "08714a48-f238-44aa-8a09-df6d9e808946",
                "body": [{"language": "bg", "template": EXPRESS_ONE_BODY}],
            }]
        }
        with patch("viberbot.services.infobip_client.requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = api_response
            text = get_rendered_template_text(
                "08714a48-f238-44aa-8a09-df6d9e808946", "bg",
                {"tovar": "555", "office": "Спиди Младост", "data": "22.07", "link": "https://x.bg"},
            )

        assert text == (
            "Express One Пратка за получаване 555 в доставящ партньор Спиди Младост "
            "Срок за получаване до 22.07. За точен адрес и работно време посетете https://x.bg "
            "Поздрави и успешен ден."
        )

    def test_unknown_template_returns_none(self):
        from viberbot.services.infobip_client import get_rendered_template_text

        with patch("viberbot.services.infobip_client.requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {"templates": []}
            assert get_rendered_template_text("missing-id", "bg", {}) is None

    def test_api_error_returns_none(self):
        from viberbot.services.infobip_client import get_rendered_template_text

        with patch("viberbot.services.infobip_client.requests.get") as mock_get:
            mock_get.return_value.ok = False
            mock_get.return_value.status_code = 500
            assert get_rendered_template_text("any", "bg", {}) is None
