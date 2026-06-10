# from llm_sdk import Small_LLM_Model

# small_llm = Small_LLM_Model()


# mkdir -p /goinfre/bahriz/uv-cache
# mkdir -p /goinfre/bahriz/venvs

# export UV_CACHE_DIR=/goinfre/bahriz/uv-cache
# export UV_PROJECT_ENVIRONMENT=/goinfre/bahriz/venvs/callmemaybe
# export UV_LINK_MODE=copy

# uv add ./llm_sdk

from llm_sdk.llm_sdk import Small_LLM_Model

llm = Small_LLM_Model()

# ── tiny test data ──────────────────────────────────────────────
functions = [
    {"name": "fn_add_numbers",    "description": "Add two numbers."},
    {"name": "fn_greet",          "description": "Greet a person by name."},
    {"name": "fn_reverse_string", "description": "Reverse a string."},
]

prompt = "What is the sum of 3 and 5?"


# ── step 1: build prompt ─────────────────────────────────────────
def build_prompt(prompt: str, functions: list) -> str:
    lines = ["You are a function calling assistant.", "Available functions:"]
    for fn in functions:
        lines.append(f"- {fn['name']}: {fn['description']}")
    lines.append(f'\nUser request: "{prompt}"')
    lines.append("Respond with only the function name that matches.")
    return "\n".join(lines)


# ── step 2: encode ───────────────────────────────────────────────
def encode(text: str) -> list[int]:
    return llm.encode(text)[0].tolist()


# ── step 3: the selector ─────────────────────────────────────────
def select_function(prompt: str, functions: list) -> str:
    instruction = build_prompt(prompt, functions)
    prompt_ids  = encode(instruction)

    # encode every function name
    candidates = [encode(fn["name"]) for fn in functions]
    remaining  = candidates[:]

    answer   = []
    position = 0

    while remaining and position < max(len(c) for c in remaining):

        # tokens all candidates have at this position
        valid_tokens = set(
            c[position] for c in remaining if position < len(c)
        )

        if len(valid_tokens) == 1:
            # everyone agrees → free token, no LLM call
            chosen = valid_tokens.pop()
            print(f"[pos {position}] free token → {chosen}")

        else:
            # ambiguity → ask the LLM
            logits = llm.get_logits_from_input_ids(prompt_ids + answer)

            # mask everything except valid candidates
            masked = [-float("inf")] * len(logits)
            for t in valid_tokens:
                masked[t] = logits[t]

            chosen = masked.index(max(masked))
            print(f"[pos {position}] LLM chose  → {chosen} "
                  f"(from {valid_tokens})")

            # prune candidates that don't match
            remaining = [
                c for c in remaining
                if position < len(c) and c[position] == chosen
            ]

        answer.append(chosen)
        position += 1

        # done if one candidate fully matched
        if len(remaining) == 1 and position == len(remaining[0]):
            break

    return llm.decode(answer)


# ── run it ───────────────────────────────────────────────────────
result = select_function(prompt, functions)
print(f"\nprompt   : {prompt}")
print(f"selected : {result}")