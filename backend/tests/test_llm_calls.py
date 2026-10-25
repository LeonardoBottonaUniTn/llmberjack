import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts import llm_calls


class RetryTests(TestCase):
    @patch.object(llm_calls.time, "sleep")
    def test_retries_transient_errors_then_returns_result(self, sleep_mock: Mock) -> None:
        transient_error = Exception("rate limited")
        transient_error.status_code = 429
        operation = Mock(side_effect=[transient_error, "ok"])

        with patch.object(llm_calls, "LLM_MAX_RETRIES", 2):
            result = llm_calls._call_with_retry(operation, provider="groq")

        self.assertEqual(result, "ok")
        self.assertEqual(operation.call_count, 2)
        sleep_mock.assert_called_once()

    @patch.object(llm_calls.time, "sleep")
    def test_does_not_retry_client_errors(self, sleep_mock: Mock) -> None:
        client_error = Exception("bad request")
        client_error.status_code = 400
        operation = Mock(side_effect=client_error)

        with patch.object(llm_calls, "LLM_MAX_RETRIES", 2):
            with self.assertRaises(Exception):
                llm_calls._call_with_retry(operation, provider="groq")

        operation.assert_called_once()
        sleep_mock.assert_not_called()


class HealthCheckTests(TestCase):
    @patch.object(llm_calls, "_create_client")
    def test_health_check_validates_selected_model(self, create_client_mock: Mock) -> None:
        client = Mock()
        client.models.retrieve.return_value = SimpleNamespace(id="active-model")
        create_client_mock.return_value = client

        result = llm_calls.check_llm_health(
            provider="groq",
            api_key="test-key",
            model="active-model",
        )

        self.assertEqual(
            result,
            {"status": "ok", "provider": "groq", "model": "active-model"},
        )
        client.models.retrieve.assert_called_once_with("active-model")


class ChatCompletionTests(TestCase):
    @patch.object(llm_calls, "_create_client")
    def test_empty_content_raises_instead_of_returning_blank(self, create_client_mock: Mock) -> None:
        client = Mock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=""), finish_reason="length")]
        )
        create_client_mock.return_value = client

        with self.assertRaises(llm_calls.EmptyLLMResponseError) as ctx:
            llm_calls._chat_completion(
                provider="groq",
                api_key="test-key",
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.7,
                max_completion_tokens=16,
            )

        self.assertIn("token limit", str(ctx.exception))
