from src.models import FunctionDefinition, PromptInput
from src.prompt import build_function_call_prompt
from src.llm_client import LLMClient


def select_function_with_llm(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
    client: LLMClient,
) -> tuple[list[int], str, list[FunctionDefinition]]:
    system_prompt = build_function_call_prompt(prompt, functions)
    prompt_ids = client.encode(system_prompt)

    options = [function.name for function in functions]
    generated_ids = []
    while options and any(r != "" for r in options):
        allowed = []
        for func_name in options:
            function_id = client.encode(func_name)
            allowed.append(function_id[0])
        logits = client.get_logits(prompt_ids + generated_ids)
        for index in range(len(logits)):
            if index not in allowed:
                logits[index] = float("-inf")
        next_token = logits.index(max(logits))
        generated_ids.append(next_token)
        next_text = client.decode([next_token])
        new_options = []
        for remain in options:
            if remain.startswith(next_text):
                chunk = remain[len(next_text):]
                new_options.append(chunk)
        options = new_options
    result = prompt_ids + generated_ids
    selected_fun = client.decode(generated_ids)
    return (result, selected_fun, functions)