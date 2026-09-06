"""Generate a Kerala pincode prefix -> district table using the LLM, once.

The result gets bundled as static data so no LLM call is needed at call time.
Prints JSON to stdout for review before we trust it.
"""
import json

import requests

from app.config import settings

PROMPT = (
    "List every 3-digit Indian PIN code prefix that belongs to Kerala state "
    "(the range 670 to 695), and the district each prefix mainly covers.\n\n"
    "Reply with strict JSON only: an object mapping the 3-digit prefix string "
    "to the district name. If a prefix spans more than one district, give the "
    "district that most of its PIN codes fall in. No prose, no markdown."
)


def main() -> None:
    resp = requests.post(
        f"{settings.azure_openai_endpoint}/chat/completions",
        headers={"Content-Type": "application/json",
                 "api-key": settings.azure_openai_key},
        json={
            "model": settings.azure_openai_model,
            "messages": [{"role": "user", "content": PROMPT}],
            "max_completion_tokens": 3000,
            "reasoning_effort": "low",
        },
        timeout=180,
    )
    if resp.status_code != 200:
        print(f"HTTP {resp.status_code}: {resp.text[:300]}")
        return

    raw = (resp.json()["choices"][0]["message"]["content"] or "").strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        table = json.loads(raw)
    except json.JSONDecodeError:
        print("Not valid JSON:\n" + raw[:800])
        return

    print(json.dumps(table, indent=2, sort_keys=True))
    print(f"\n{len(table)} prefixes")
    districts = sorted(set(table.values()))
    print(f"{len(districts)} districts: {', '.join(districts)}")


if __name__ == "__main__":
    main()
