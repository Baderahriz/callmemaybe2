from src.models import FunctionCallOutput, FunctionDefinition, PromptInput
from src.llm_client import LLMClient
from src.selector import select_function_with_llm
from src.extract_paramters import extract_parameters


def generate_output(
    prompt: PromptInput,
    functions: list[FunctionDefinition],
    client: LLMClient,
) -> FunctionCallOutput:
    """Generate a FunctionCallOutput for the given prompt.

    The pipeline selects a function and extracts parameters using the LLM
    client, then builds a `FunctionCallOutput` instance.

    Args:
        prompt: The prompt input to process.
        functions: Available function definitions.
        client: LLM client used for selection and extraction.

    Returns:
        A `FunctionCallOutput` with `name` and `parameters` filled.
    """
    prompt_ids, selected_fun, functions = select_function_with_llm(
        prompt,
        functions,
        client,
    )
    return FunctionCallOutput(
        prompt=prompt.prompt,
        name=selected_fun,
        parameters=extract_parameters(
            prompt_ids,
            selected_fun,
            functions,
            client,
        ),
    )

# commande moulinette data dyalhom
# cd moulinette ; uv run python -m moulinette grade_student_answers \
#   --set private \
#   --student_answer_path ../data/output/function_calling_results.json

# commande moulinette data dyali
# cd moulinette ; uv run python -m moulinette grade_student_answers \
#   --student_answer_path ../data/output/function_calling_results.json
