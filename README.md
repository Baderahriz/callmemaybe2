*This project has been created as part of the 42 curriculum by &lt;bahriz&gt;.*

# call me maybe

## Description

**call me maybe** is a function-calling engine for Large Language Models. Given a
set of available functions (each with a name, a description, and a typed
parameter schema) and a natural-language prompt, the program produces a
structured function call — a JSON object naming the function to invoke and the
arguments to pass it.

The core idea is that the model never *answers* the prompt and never *computes*
anything. It only **routes**: it decides which function fits the request and
extracts the argument values from the text. The actual work of calling the
function and computing a result is left to real code downstream.

The key technical constraint is that the output must be **valid JSON that
matches the function's schema, every single time**. A small model left to
generate freely produces malformed JSON often. This project guarantees validity
through **constrained decoding**: at every generation step the program forbids
any token that would break the JSON structure or the schema, so the model can
only ever build a correct call.

The program reads its inputs from `data/input/`, processes every prompt, and
writes an array of results to `data/output/function_calling_results.json`. The
function definitions and prompts are read at runtime and never hardcoded, so the
same code works unchanged when the input files are replaced.

## Instructions

The project uses [`uv`](https://docs.astral.sh/uv/) for dependency management
and a `Makefile` for the common tasks.

### Requirements

- Python 3.10 or newer
- `uv` installed
- The provided `llm_sdk/` package present at the repository root

### Installation

```bash
make install      # runs: uv sync
```

This creates an isolated virtual environment and installs every dependency
pinned in `uv.lock`, reproducibly.

### Execution

```bash
make run          # runs: uv run python -m src
```

By default this reads:

- `data/input/functions_definition.json` — available functions and their schemas
- `data/input/function_calling_tests.json` — the prompts to process

and writes `data/output/function_calling_results.json`.

You can override any path:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

### Other Makefile targets

```bash
make debug        # run under the Python debugger (pdb)
make lint         # flake8 + mypy with the project's type-checking flags
make clean        # remove caches, bytecode, and data/output
```

## Resources

References used to understand the topic:

- **Hugging Face Transformers documentation** — tokenization (`encode`/`decode`),
  logits, and autoregressive generation.
- **Byte-Pair Encoding (BPE)** — background on subword tokenization and why a
  character's token depends on its surrounding context.
- **Pydantic documentation** — model validation, `model_validate`, and strict
  configuration with `extra="forbid"`.
- **The JSON specification (json.org)** — the grammar rules the constrained
  decoder enforces.
- **The provided `llm_sdk`** — `Small_LLM_Model` and its
  `get_logits_from_input_ids`, `encode`, and `decode` methods.

### How AI was used

AI assistance (a coding assistant) was used as a **reviewer and tutor**, not as a
code generator for the core logic. Specifically:

- **Conceptual learning:** clarifying how next-token prediction, logits, and
  constrained decoding fit together before any code was written.
- **Code review:** reviewing the selection and parameter-extraction logic for
  bugs, especially the tokenization-boundary issues described in *Challenges
  faced*.
- **Debugging guidance:** diagnosing the integer/decimal coercion bugs and the
  fused-quote string-termination bug, pointing to the cause so I could write the
  fix myself.
- **Tooling and linting:** explaining `uv`, the `Makefile` targets, and how to
  satisfy `flake8` and `mypy`.

The algorithm design, the implementation, and all final code decisions are my
own.

## Algorithm explanation

The program guarantees valid, schema-compliant output through **constrained
decoding**. The principle is the same at every step:

1. Ask the model for the **logits** — one raw score per token in the vocabulary —
   for the current context.
2. **Forbid** every token that is not legal at this point by setting its logit to
   `-inf`.
3. Take the **argmax** (the highest-scoring token). Because the illegal tokens
   are `-inf`, the model can never pick one.
4. **Append** the chosen token to the context and repeat (autoregressive loop).

The structure of the JSON (braces, quotes, commas, the mandatory keys) is
**forced** by the program; the model is only free to choose the *values*. This is
the split that makes 100% valid JSON possible from a 0.6B model.

### Function-name selection

The function name is built token by token. Starting from the list of available
function names, at each step the program allows only the first token of each
still-matching candidate, masks everything else to `-inf`, and lets the model
pick. The chosen text is then chopped off the front of the candidates, narrowing
the set, until a single name remains. The decision of *which* function comes
purely from the model's logits — there is no keyword matching.

### Parameter extraction

Once the function is known, its parameter schema is read from the definition. For
each parameter the program forces the structural JSON (`"key":`) into the context
and then decodes the value according to its **type**:

- **`number` / `integer`:** only digit tokens, `.`, `-`, and the terminators `,`
  and `}` are allowed. Generation stops at a terminator. The text is then
  converted — `float(raw)` for `number`, `int(float(raw))` for `integer` (the
  inner `float` handles the model emitting `4.0`).
- **`string`:** the opening quote is forced, then the model generates freely
  until a closing quote appears in the decoded text; generation stops there.

The skeleton (`{ "name": "...", "parameters": { ... } }`), the commas between
parameters, and the closing brace are all forced by the program, so the assembled
output is always valid JSON.

## Design decisions

- **Token-space, decoded-text comparison for string termination.** A quote
  character does not always tokenize to the same id — after a word it can fuse
  into a single token (e.g. `Ali"`). The decoder therefore compares the *decoded
  text* of each token for a `"`, rather than comparing token ids, and splits on
  the quote to keep only the content before it.
- **Force structure, free values.** Only parameter values are model-chosen;
  every structural character is inserted by the program. This is what guarantees
  validity.
- **Load the model once.** The `LLMClient` is constructed a single time in
  `main` and passed down, rather than re-loading the model per prompt.
- **Pydantic for the input door, constrained decoding for the output door.**
  Pydantic validates the loaded definitions and prompts *after* they exist;
  constrained decoding prevents invalid output from ever being *created*. They
  are complementary, not the same mechanism.
- **No hardcoding.** Function names, parameter names, and types are all read from
  the input files at runtime, so a changed definition file requires no code
  changes.
- **A separate `validate_output` check.** After each call is built, it is
  re-validated against the schema (correct keys, correct value types, integers
  not booleans) as a final safety net.

## Performance analysis

- **Accuracy.** On the provided function/prompt sets the program selects the
  correct function and extracts well-typed parameters for every prompt. String
  and numeric values (including decimals such as `0.0375`) are extracted
  correctly. The main accuracy limitation is *value quality* on hard free-text
  cases such as complex regular expressions, which reflects the 0.6B model's
  capability rather than a decoding error — the output remains valid JSON of the
  correct type.
- **Validity.** Because structure is forced by constrained decoding, **100% of
  outputs are valid JSON** and conform to the schema's key set and types.
- **Speed.** The dominant cost is loading the model, done **once** at startup.
- **Reliability.** The program is designed never to crash: input errors exit
  cleanly with a clear message, and a failure on any single prompt is isolated so
  the rest of the batch still completes and a result file is always written.

## Challenges faced

- **Tokenization boundaries (the hardest bug).** A character's token id depends
  on its context. The closing quote of a string would fuse with the preceding
  word into one token, so comparing the next token's id against a standalone
  quote's id failed and let trailing garbage (`Ali"}}...`) leak into the value.
  *Solution:* decode each candidate token to text and test whether it *contains*
  a quote, then split on the quote and keep only the content before it.
- **Integers arriving as floats.** The numeric branch initially applied
  `float(raw)` to both `number` and `integer`, so integers came out as `4.0` and
  were rejected by the validator. *Solution:* use `int(float(raw))` for
  integers — the inner `float` tolerates the model writing `4.0`, the outer
  `int` produces a true integer.
- **Lost decimal points.** The number decoder first allowed only digits and
  terminators, so `0.0375` decoded to `0.0`. *Solution:* add `.` to the allowed
  token set.
- **Pipeline wiring.** Early on, the entry point called placeholder logic instead
  of the real constrained-decoding code. *Solution:* wire the generator to call
  the real selection and extraction functions, and load the model once.

## Testing strategy

- **Multiple function sets.** The implementation was tested against more than one
  `functions_definition.json` — including a second set with `integer` and
  `decimal` parameters — to confirm it does not depend on any particular function
  names or types. This directly exercised the robustness the subject asks for
  ("input files may change").
- **Edge cases.** Tested with decimals, multi-parameter functions, string values
  containing special characters, and prompts of varying phrasing.
- **Output validation.** Every produced call is re-checked by `validate_output`
  against the schema (key set, value types, integer-not-boolean), so any invalid
  result is reported.
- **Failure handling.** Tested with a missing input file and malformed JSON to
  confirm the program prints a clear message and exits without a traceback.
## Example usage

Run with the default paths:

```bash
make run
```

Run with explicit paths:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

Given a function definition for `multiply(a: number, b: number)` and the prompt
`"What is the product of 12 and 9?"`, the program writes an entry of the form:

```json
{
  "prompt": "What is the product of 12 and 9?",
  "name": "multiply",
  "parameters": { "a": 12.0, "b": 9.0 }
}
```

The full run writes an array of such objects to the output path.

Handling a missing input file:

```bash
$ uv run python -m src --functions_definition does_not_exist.json
Error: input file not found: does_not_exist.json
```