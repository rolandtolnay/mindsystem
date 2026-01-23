"""Token estimation and truncation utilities."""


def estimate_tokens(text: str) -> int:
    """Estimate token count using word count * 1.3."""
    if not text:
        return 0
    word_count = len(text.split())
    return int(word_count * 1.3)


def truncate_results(results: list[dict], max_tokens: int) -> tuple[list[dict], int]:
    """Truncate results to fit within token budget.

    Args:
        results: List of result dicts with 'content' field
        max_tokens: Maximum token budget

    Returns:
        Tuple of (truncated_results, total_tokens_used)
    """
    truncated = []
    tokens_used = 0

    for result in results:
        content = result.get("content", "")
        result_tokens = estimate_tokens(content)

        # Add metadata overhead estimate (title, url, etc.)
        overhead = 50
        total_result_tokens = result_tokens + overhead

        if tokens_used + total_result_tokens <= max_tokens:
            result_with_tokens = {**result, "tokens": result_tokens}
            truncated.append(result_with_tokens)
            tokens_used += total_result_tokens
        else:
            # Try to fit partial content if we have room
            remaining = max_tokens - tokens_used - overhead
            if remaining > 100:  # Only include if meaningful content fits
                words = content.split()
                truncated_word_count = int(remaining / 1.3)
                if truncated_word_count > 0:
                    truncated_content = " ".join(words[:truncated_word_count]) + "..."
                    truncated_tokens = estimate_tokens(truncated_content)
                    result_with_tokens = {
                        **result,
                        "content": truncated_content,
                        "tokens": truncated_tokens,
                        "truncated": True
                    }
                    truncated.append(result_with_tokens)
                    tokens_used += truncated_tokens + overhead
            break

    return truncated, tokens_used
