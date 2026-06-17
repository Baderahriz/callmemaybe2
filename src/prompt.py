from src.models import FunctionDefinition, PromptInput


def build_function_call_prompt(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
) -> str:
    """Build the system prompt describing functions for the LLM.

    Args:
        prompt: The user's prompt to include in the system message.
        functions: List of function definitions to describe.

    Returns:
        A string suitable as a system prompt for the LLM.
    """
    lines = [
        "You are a function calling assistant. (You are a parameter "
        "extraction engine. Extract the function parameters from the user "
        "request. Use the exact parameter names. Do not add extra keys. Do "
        "not explain. Return only a valid JSON object.) Available functions:",
    ]
    func_descriptions_list = [
        "- " + item.name + ": " + item.description for item in functions
    ]
    lines.append("\n".join(func_descriptions_list))

    lines.append(f'User request: "{prompt.prompt}"')
    lines.append('Function call: {"name": "')

    return "\n".join(lines)
