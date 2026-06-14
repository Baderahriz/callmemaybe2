import argparse
from src.models import FunctionDefinition, PromptInput
from src.validator import validate_output
from src.io_utils import load_json, write_json
from src.generator import generate_output
from src.llm_client import LLMClient
# from llm_sdk import Small_LLM_Model


def parse_args():
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


def main():
    args = parse_args()
    raw_functions = load_json(args.functions_definition)
    raw_prompts = load_json(args.input)

    functions = [
        FunctionDefinition.model_validate(item)
        for item in raw_functions
    ]

    prompts = [
        PromptInput.model_validate(item)
        for item in raw_prompts
    ]

    client = LLMClient()

    outputs = []
    for prompt in prompts:
        output = generate_output(prompt, functions, client)

        if not validate_output(output, functions):
            print(f"Invalid output for prompt: {prompt.prompt}")

        outputs.append(output.model_dump())

    write_json(args.output, outputs)

    # all_valid = True

    # for output in manual_output:
    #     if not validate_output(output, functions):
    #         all_valid = False

    # if all_valid:
    #     out = [output.model_dump() for output in manual_output]
    #     write_json(args.output, out)
    # else:
    #     print("At least one json is invalid")


if __name__ == "__main__":
    main()


# client = LLMClient()  # load model ONCE, not per prompt
#
#     outputs = []
#     for prompt in prompts:
#         output = generate_output(prompt, functions, client)
#         if not validate_output(output, functions):
#             print(f"Invalid output for prompt: {prompt.prompt}")
#             return
#         outputs.append(output.model_dump())
#
#     write_json(args.output, outputs)
