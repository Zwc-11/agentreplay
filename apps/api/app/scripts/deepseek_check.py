"""Verify your DeepSeek connection end to end.

Usage:
    DEEPSEEK_API_KEY=<your-deepseek-api-key> python -m app.scripts.deepseek_check
"""

from __future__ import annotations

from app.adapters.llm.deepseek import get_default_client
from app.config import settings


def main() -> None:
    client = get_default_client()
    if client is None:
        print("DeepSeek is NOT configured.")
        print("  -> set DEEPSEEK_API_KEY (and `pip install openai`).")
        print(f"  current model={settings.deepseek_model}  base_url={settings.deepseek_base_url}")
        return

    print(
        f"Calling {settings.deepseek_model} at {settings.deepseek_base_url} (thinking={settings.deepseek_thinking}) ..."
    )
    out = client.complete(
        [
            {"role": "system", "content": "You are a terse assistant."},
            {"role": "user", "content": "Reply with exactly: AgentReplay DeepSeek OK"},
        ]
    )
    print(f"\nreasoning_content returned: {'yes' if out.get('reasoning') else 'no'}")
    print("\ncontent:\n  " + str(out.get("content")))


if __name__ == "__main__":
    main()
