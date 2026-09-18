import json

from app.services import llm


def test_llm_disabled(monkeypatch):
    monkeypatch.setattr(
        llm.settings,
        "LLM_ENABLED",
        False,
    )

    items = [
        {
            "name": "Milk",
            "quantity": 1,
            "price": 2.50,
            "category": "food",
        }
    ]

    result = llm.categorize_with_llm(items)

    assert result == items


def test_llm_without_api_key(monkeypatch):
    monkeypatch.setattr(
        llm.settings,
        "LLM_ENABLED",
        True,
    )
    monkeypatch.setattr(
        llm.settings,
        "OPENAI_API_KEY",
        None,
    )

    items = [
        {
            "name": "Milk",
            "quantity": 1,
            "price": 2.50,
            "category": "food",
        }
    ]

    result = llm.categorize_with_llm(items)

    assert result == items


def test_llm_categorization(monkeypatch):
    monkeypatch.setattr(
        llm.settings,
        "LLM_ENABLED",
        True,
    )
    monkeypatch.setattr(
        llm.settings,
        "OPENAI_API_KEY",
        "fake-key",
    )

    class FakeMessage:
        content = json.dumps(
            {
                "categories": [
                    {
                        "name": "Milk",
                        "category": "food",
                    },
                    {
                        "name": "Shampoo",
                        "category": "hygiene",
                    },
                ]
            }
        )

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, **kwargs):
            return type(
                "Response",
                (),
                {
                    "choices": [
                        FakeChoice()
                    ]
                },
            )()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    class FakeOpenAI:
        def __new__(
            cls,
            api_key,
        ):
            return FakeClient()

    monkeypatch.setitem(
        __import__(
            "sys"
        ).modules,
        "openai",
        type(
            "OpenAI",
            (),
            {
                "OpenAI": FakeOpenAI
            },
        ),
    )

    items = [
        {
            "name": "Milk",
            "quantity": 1,
            "price": 2.50,
            "category": "other",
        },
        {
            "name": "Shampoo",
            "quantity": 1,
            "price": 4.90,
            "category": "other",
        },
    ]

    result = llm.categorize_with_llm(items)

    assert result[0]["category"] == "food"
    assert result[1]["category"] == "hygiene"


def test_llm_invalid_response(monkeypatch):
    monkeypatch.setattr(
        llm.settings,
        "LLM_ENABLED",
        True,
    )
    monkeypatch.setattr(
        llm.settings,
        "OPENAI_API_KEY",
        "fake-key",
    )

    class FakeMessage:
        content = "invalid json"

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletions:
        def create(self, **kwargs):
            return type(
                "Response",
                (),
                {
                    "choices": [
                        FakeChoice()
                    ]
                },
            )()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    class FakeOpenAI:
        def __new__(
            cls,
            api_key,
        ):
            return FakeClient()

    monkeypatch.setitem(
        __import__(
            "sys"
        ).modules,
        "openai",
        type(
            "OpenAI",
            (),
            {
                "OpenAI": FakeOpenAI
            },
        ),
    )

    items = [
        {
            "name": "Unknown",
            "quantity": 1,
            "price": 5.0,
            "category": "other",
        }
    ]

    result = llm.categorize_with_llm(items)

    assert result[0]["category"] == "other"