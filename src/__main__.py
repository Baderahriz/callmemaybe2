import argparse
from src.models import FunctionCallOutput, FunctionDefinition, PromptInput
from src.validator import validate_output
from src.io_utils import load_json, write_json
from src.generator import generate_output

# from llm_sdk import Small_LLM_Model


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--functions_definition", default="data/input/functions_definition.json",)

    parser.add_argument("--input", default="data/input/function_calling_tests.json",)
    parser.add_argument("--output", default="data/output/function_calling_results.json",)
    return parser.parse_args()

def build_manual_output_for_prompt(
    index: int,
    prompt: PromptInput,
) -> FunctionCallOutput:
    manual_parameters = [
        {
            "name": "fn_add_numbers",
            "parameters": {
                "a": 2.0,
                "b": 3.0,
            },
        },
        {
            "name": "fn_add_numbers",
            "parameters": {
                "a": 265.0,
                "b": 345.0,
            },
        },
        {
            "name": "fn_greet",
            "parameters": {
                "name": "shrek",
            },
        },
        {
            "name": "fn_greet",
            "parameters": {
                "name": "john",
            },
        },
        {
            "name": "fn_reverse_string",
            "parameters": {
                "s": "hello",
            },
        },
        {
            "name": "fn_reverse_string",
            "parameters": {
                "s": "world",
            },
        },
        {
            "name": "fn_get_square_root",
            "parameters": {
                "a": 16.0,
            },
        },
        {
            "name": "fn_get_square_root",
            "parameters": {
                "a": 144.0,
            },
        },
        {
            "name": "fn_substitute_string_with_regex",
            "parameters": {
                "source_string": "Hello 34 I'm 233 years old",
                "regex": "\\d+",
                "replacement": "NUMBERS",
            },
        },
        {
            "name": "fn_substitute_string_with_regex",
            "parameters": {
                "source_string": "Programming is fun",
                "regex": "[aeiouAEIOU]",
                "replacement": "*",
            },
        },
        {
            "name": "fn_substitute_string_with_regex",
            "parameters": {
                "source_string": "The cat sat on the mat with another cat",
                "regex": "cat",
                "replacement": "dog",
            },
        },
    ]

    item = manual_parameters[index]

    return FunctionCallOutput.model_validate(
        {
            "prompt": prompt.prompt,
            "name": item["name"],
            "parameters": item["parameters"],
        }
    )



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

    outputs = []
    for prompt in prompts:
        output = generate_output(prompt, functions)
    
        if not validate_output(output, functions):
            print(f"Invalid output for prompt: {prompt.prompt}")
            return
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