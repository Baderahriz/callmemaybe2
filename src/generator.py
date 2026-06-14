from src.models import FunctionCallOutput, FunctionDefinition, PromptInput
from src.llm_client import LLMClient


def build_function_call_prompt(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
) -> str:
    lines = ["You are a function calling assistant.(You are a parameter extraction engine.Extract the function parameters from the user request.Use the exact parameter names.Do not add extra keys.Do not explain.Return only a valid JSON object. ) Available functions:"]
    func_descriptions_list = ["- " + item.name + ": "+item.description for item in functions]
    lines.append("\n".join(func_descriptions_list))

    lines.append(f'User request: "{prompt.prompt}"')
    lines.append('Function call: {"name": "')

    return "\n".join(lines)


def select_function_with_llm(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
    client: LLMClient,
):
    system_prompt = build_function_call_prompt(prompt, functions)
    prompt_ids = client.encode(system_prompt)

    options = [function.name for function in functions]
    allowed = []
    generated_ids = []
    while options and any(r != "" for r in options):
        allowed = []
        for func_name in options:
            function_id = client.encode(func_name)
            allowed.append(function_id[0])
        logits = client.get_logits(prompt_ids + generated_ids)
        for index, item in enumerate(logits):
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


def extract_parameters(prompt_context_ids, selected, functions, client):
    params = {}
    is_last = False
    selected = next((f for f in functions if f.name == selected))
    ordered_params = selected.parameters
    paramter_ids = client.encode('", "parameters": {')
    prompt_context_ids += paramter_ids

    def find_string():
        value_ids = []
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
    
    def find_paramter(client):
        digit_tokens = {client.encode(d)[0] for d in "0123456789."}
        comma = client.encode(",")[0]
        brace = client.encode("}")[0]
        allowed = digit_tokens | {comma, brace}
        value_ids = []
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

    for i, (key, value) in enumerate(ordered_params.items()):
        is_last = (i == len(ordered_params) - 1)
        prompt_context_ids += client.encode(f'"{key}":')
        value_ids = []
        if value.type in ("number", "integer"):
            value_ids = find_paramter(client)
            raw = client.decode(value_ids).strip()
            if value.type == "number":
                params[key] = float(raw) if raw else 0.0
            else:
                params[key] = int(raw) if raw else 0

        else:
            quote = client.encode('"')[0]
            prompt_context_ids += [quote]
            value_ids = find_string()
            raw = client.decode(value_ids).strip()
            params[key] = raw
        
        prompt_context_ids += value_ids
        prompt_context_ids += client.encode("}" if is_last else ",")

    return params


def generate_output(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
    client: LLMClient,
) -> FunctionCallOutput:
     prompt_ids, selected_fun, functions = select_function_with_llm(prompt, functions, client)
     return FunctionCallOutput(
        prompt=prompt.prompt,
        name=selected_fun,
        parameters=extract_parameters(prompt_ids, selected_fun, functions, client)
    )




#commande moulinette data dyalhom
# cd moulinette ; uv run python -m moulinette grade_student_answers  --set private  --student_answer_path ../data/output/function_calling_results.json


#commande moulinette data dyali
# cd moulinette ; uv run python -m moulinette grade_student_answers   --student_answer_path ../data/output/function_calling_results.json