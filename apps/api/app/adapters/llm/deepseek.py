"""DeepSeek v4 client (OpenAI-SDK compatible) with thinking mode.

Docs: https://api-docs.deepseek.com/guides/thinking_mode
- base_url: https://api.deepseek.com
- model:    deepseek-v4-pro (thinking) / deepseek-v4-flash
- thinking: extra_body={"thinking": {"type": "enabled"}} + reasoning_effort
- reasoning_content may be returned alongside content; callers should not expose
  raw reasoning in user-facing summaries.

The OpenAI SDK is imported lazily, so the rest of the app runs without it
installed. `get_default_client()` returns None when no API key is configured,
which lets every caller fall back to deterministic behaviour.
"""

from __future__ import annotations

from typing import Optional

from app.config import settings


class DeepSeekClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-v4-pro",
        reasoning_effort: str = "high",
        thinking: bool = True,
    ):
        try:
            from openai import OpenAI  # imported lazily
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "The 'openai' package is required for DeepSeek. Run: pip install openai"
            ) from e
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.thinking = thinking

    def complete(self, messages: list[dict], json_mode: bool = False) -> dict:
        """Single chat completion. Returns {"content", "reasoning"}.

        Note: thinking mode ignores temperature/top_p/penalty params by design.
        """
        kwargs: dict = {"model": self.model, "messages": messages}
        if self.reasoning_effort:
            kwargs["reasoning_effort"] = self.reasoning_effort
        if self.thinking:
            kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        resp = self._client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        return {"content": msg.content, "reasoning": getattr(msg, "reasoning_content", None)}


def get_default_client() -> Optional[DeepSeekClient]:
    """Build a client from env settings, or None if no key / SDK is available."""
    if not settings.llm_enabled:
        return None
    try:
        return DeepSeekClient(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model,
            reasoning_effort=settings.deepseek_reasoning_effort,
            thinking=settings.deepseek_thinking,
        )
    except Exception as e:  # noqa: BLE001 - never let LLM setup crash a run
        import sys as _sys
        print(f"[agentreplay] DeepSeek client unavailable ({e}); falling back to heuristic.", file=_sys.stderr)
        return None
