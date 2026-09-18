import json

from ..config import settings


ALLOWED_CATEGORIES = {
    "food",
    "beverages",
    "hygiene",
    "clothing",
    "electronics",
    "transport",
    "medicine",
    "restaurant",
    "other",
}


def categorize_with_llm(
    items: list[dict],
) -> list[dict]:

    result_items = [
        item.copy()
        for item in items
    ]

    if not settings.LLM_ENABLED:
        return result_items

    if not settings.OPENAI_API_KEY:
        return result_items
    unknown_items = [
        item
        for item in result_items
        if item.get("category", "other") == "other"
    ]

    if not unknown_items:
        return result_items

    try:
        from openai import OpenAI
    except ImportError:
        return result_items

    names = [
        item.get("name", "")
        for item in unknown_items
        if item.get("name")
    ]

    if not names:
        return result_items

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY
    )

    prompt = f"""
Classify the following receipt products.

The product names may be in English,
French, Russian, or may contain OCR errors.

Allowed categories:

food
beverages
hygiene
clothing
electronics
transport
medicine
restaurant
other

Use "other" when the category cannot be
determined reliably.

Return ONLY valid JSON using exactly
this structure:

{{
  "categories": [
    {{
      "name": "product name",
      "category": "food"
    }}
  ]
}}

Do not invent products.
Keep every product name exactly as provided.

Products:

{json.dumps(
    names,
    ensure_ascii=False,
)}
"""

    try:
        response = (
            client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You classify products "
                            "extracted from shopping "
                            "receipts."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0,
                response_format={
                    "type": "json_object"
                },
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:
            return result_items

        data = json.loads(content)

        categories = data.get(
            "categories",
            [],
        )

        llm_categories = {}

        for entry in categories:
            if not isinstance(
                entry,
                dict,
            ):
                continue

            name = entry.get("name")
            category = entry.get("category")

            if not isinstance(
                name,
                str,
            ):
                continue

            if not isinstance(
                category,
                str,
            ):
                continue

            category = (
                category
                .strip()
                .lower()
            )

            if (
                name
                and category
                in ALLOWED_CATEGORIES
            ):
                llm_categories[name] = category

        for item in result_items:
            if item.get(
                "category",
                "other",
            ) != "other":
                continue

            name = item.get("name")

            if not name:
                continue

            category = llm_categories.get(
                name
            )

            if category:
                item["category"] = category

    except Exception:
        
        return result_items

    return result_items