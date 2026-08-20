import os

from app.errors import ProviderError

MODEL = "claude-haiku-4-5-20251001"
NO_RELEVANT_CONTENT_ANSWER = "I don't have any saved content relevant to that question."

_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic

        _client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


def _build_prompt(question: str, matches: list[dict]) -> str:
    context = "\n\n".join(f"[Source {i + 1}: {m['title']}]\n{m['chunk_text']}" for i, m in enumerate(matches))
    return (
        "Answer the question using only the sources below. "
        "If the sources don't contain the answer, say so plainly.\n\n"
        f"{context}\n\nQuestion: {question}"
    )


def answer_question(question: str, matches: list[dict]) -> tuple[str, list[dict]]:
    if not matches:
        return NO_RELEVANT_CONTENT_ANSWER, []

    try:
        response = _get_client().messages.create(
            model=MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": _build_prompt(question, matches)}],
        )
    except Exception as exc:
        raise ProviderError("failed to get an answer from the LLM", detail=str(exc)) from exc

    answer = "".join(block.text for block in response.content if block.type == "text")
    sources = [
        {
            "item_id": m["item_id"],
            "title": m["title"],
            "source_type": m["source_type"],
            "snippet": m["chunk_text"][:300],
        }
        for m in matches
    ]
    return answer, sources
