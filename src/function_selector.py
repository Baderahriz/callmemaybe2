
from src.llm_client import LLMClient
from src.models import FunctionDefinition, PromptInput


def build_function_call_prompt(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
) -> str:
    lines = ["You are a function calling assistant. Available functions:"]
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
        quote = client.encode('"')[0]
        brace = client.encode("}")[0]
        newline = client.encode("\n")[0]
        # brace = client.encode("")[0]
        value_ids = []
        for _ in range(66):
            logits = client.get_logits(prompt_context_ids + value_ids)
            next_token = logits.index(max(logits))
            if next_token in (quote, brace, newline):
                break
            value_ids.append(next_token)
        return value_ids
    
    def find_paramter(client):
        digit_tokens = {client.encode(d)[0] for d in "0123456789"}
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
        # print(client.decode(prompt_context_ids))
        value_ids = []
        if value.type in ("number", "integer"):
            value_ids = find_paramter(client)
            raw = client.decode(value_ids).strip()
            params[key] = float(raw) if raw else 0.0
        else:
            value_ids = find_string()
            raw = client.decode(value_ids).strip()
            params[key] = raw
        
        prompt_context_ids += value_ids
        prompt_context_ids += client.encode("}" if is_last else ",")

    print(params)
    print(client.decode(prompt_context_ids))


# def find_string(prompt_context_ids, client):
#     
#     # force the opening quote of the string value
#     prompt_context_ids = prompt_context_ids + [quote]
#     value_ids = []
#     for _ in range(64):                      # higher cap — strings are longer
#         logits = client.get_logits(prompt_context_ids + value_ids)
#         next_token = logits.index(max(logits))   # no masking
#         if next_token == quote:              # closing quote → string done
#             break
#         value_ids.append(next_token)
#     return value_ids

# def extract_parameters(result_text, selected, client):
#     context_id = client.encode(result_text + '", "parameters": {')
#     params = {}
#     items = list(selected.parameters.items())
#     for i, (key, pdef) in enumerate(items):
#         is_last = (i == len(items) - 1)
#         context_id += client.encode(f'"{key}":')
#         if pdef.type in ("number", "integer"):
#             value_ids = find_parameter(context_id, client)
#             raw = client.decode(value_ids).strip()
#             params[key] = float(raw) if raw else 0.0
#         else:
#             value_ids = []          # string stub for now
#             params[key] = ""
#         context_id += value_ids
#         context_id += client.encode("}" if is_last else ",")
#     return params