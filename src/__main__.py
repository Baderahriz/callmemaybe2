import argparse
from src.models import FunctionDefinition, PromptInput
from src.validator import validate_output
from src.io_utils import load_json, write_json
from src.generator import generate_output
from src.llm_client import LLMClient
from argparse import Namespace
import sys
from pydantic import ValidationError


def parse_args() -> Namespace:
    """Parse command line arguments for the CLI.

    Returns:
        An argparse `Namespace` with parsed CLI options.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
    )

    parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json",
    )
    parser.add_argument(
        "--output",
        default="data/output/function_calling_results.json",
    )
    return parser.parse_args()


def main() -> None:
    """Run the full pipeline: load, generate, validate, and write results.

    This function is the CLI entrypoint. It loads function definitions
    and prompts, runs the generator, validates outputs, and writes
    the final JSON file.
    """
    args = parse_args()
    raw_functions = load_json(args.functions_definition)
    raw_prompts = load_json(args.input)

    try:
        functions = [
            FunctionDefinition.model_validate(item)
            for item in raw_functions
        ]
        prompts = [
            PromptInput.model_validate(item)
            for item in raw_prompts
        ]
    except ValidationError as exc:
        print(f"Error: input does not match expected schema:\n{exc}")
        sys.exit(1)

    client = LLMClient()

    outputs = []
    for prompt in prompts:
        try:
            output = generate_output(prompt, functions, client)

            if not validate_output(output, functions):
                print(f"Invalid output for prompt: {prompt.prompt}")

            outputs.append(output.model_dump())
        except Exception as exc:
            print(f"Failed to process prompt '{prompt.prompt}': {exc}")
    write_json(args.output, outputs)


if __name__ == "__main__":
    main()
