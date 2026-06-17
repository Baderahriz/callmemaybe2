from src.models import FunctionDefinition
from src.llm_client import LLMClient
from typing import Any


def decode_string(
    client: LLMClient,
    prompt_context_ids: list[int],
) -> list[int]:
    """Decode a quoted string value from the LLM token stream.

    Args:
        client: LLM client used to query logits and decode tokens.
        prompt_context_ids: Current token context to condition on.

    Returns:
        Token ids representing the decoded string value.
    """
    value_ids: list[int] = []
    for _ in range(66):
        logits = client.get_logits(prompt_context_ids + value_ids)
        next_token = logits.index(max(logits))
        piece = client.decode([next_token])
        if '"' in piece:
            chunk = piece.split('"')
            value_ids += client.encode(chunk[0])
            break
        value_ids.append(next_token)
    return value_ids


def decode_number(
    client: LLMClient,
    prompt_context_ids: list[int],
) -> list[int]:
    """Decode a numeric token sequence from the LLM token stream.

    Args:
        client: LLM client used to query logits and decode tokens.
        prompt_context_ids: Current token context to condition on.

    Returns:
        Token ids representing the decoded numeric value.
    """
    digit_tokens = {client.encode(d)[0] for d in "0123456789."}
    comma = client.encode(",")[0]
    brace = client.encode("}")[0]
    minus = client.encode("-")[0]
    allowed = digit_tokens | {comma, brace, minus}
    value_ids: list[int] = []
    for _ in range(35):
        logits = client.get_logits(prompt_context_ids + value_ids)
        for index in range(len(logits)):
            if index not in allowed:
                logits[index] = float("-inf")
        next_token = logits.index(max(logits))
        if next_token in (comma, brace):
            break
        value_ids.append(next_token)
    return value_ids


def extract_parameters(
    prompt_context_ids: list[int],
    selected: str,
    functions: list[FunctionDefinition],
    client: LLMClient,
) -> dict[str, Any]:
    """Extract parameters for the selected function using the LLM client.

    Args:
        prompt_context_ids: Token ids forming the current prompt context.
        selected: The selected function name.
        functions: List of available function definitions.
        client: LLM client used for decoding parameter values.

    Returns:
        A mapping of parameter names to decoded Python values.
    """
    params: dict[str, Any] = {}
    is_last = False
    selected_function = None
    for function in functions:
        if function.name == selected:
            selected_function = function
            break
    if selected_function is None:
        return {}
    ordered_params = selected_function.parameters
    paramter_ids = client.encode('", "parameters": {')
    prompt_context_ids += paramter_ids

    for i, (key, value) in enumerate(ordered_params.items()):
        is_last = (i == len(ordered_params) - 1)
        prompt_context_ids += client.encode(f'"{key}":')
        value_ids = []
        if value.type in ("number", "integer"):
            value_ids = decode_number(client, prompt_context_ids)
            raw = client.decode(value_ids).strip()
            if value.type == "number":
                params[key] = float(raw) if raw else 0.0
            else:
                params[key] = int(float(raw)) if raw else 0

        else:
            quote = client.encode('"')[0]
            prompt_context_ids += [quote]
            value_ids = decode_string(client, prompt_context_ids)
            raw = client.decode(value_ids).strip()
            params[key] = raw

        prompt_context_ids += value_ids
        prompt_context_ids += client.encode("}" if is_last else ",")

    return params
