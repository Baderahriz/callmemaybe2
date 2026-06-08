# # 1. Build system prompt with function descriptions
# # 2. Append: User request: "Greet john"
# # 3. Append: {"name":"           ← force this prefix
# # 4. Call pick_from_options(["fn_add_numbers", "fn_greet", "fn_reverse_string"])
# #    → model picks "fn_greet"
# # 5. Force: ","parameters":{
# # 6. Look up parameters for fn_greet → ["name"]
# # 7. Force: "name":"
# # 8. Call generate_string_value()
# #    → model generates "john"
# # 9. Force: "}}
# # 10. Parse the complete JSON and return the result


# # 1. Build the system prompt:
# #    - Header: "You are a function calling assistant."
# #    - For each function in functions:
# #      - Add: "- {name}: {description}. Parameters: {param list}"
# #    - Add: 'User request: "{prompt}"'
# #    - Add: 'Function call: {"name":"'






# # 2. Encode the system prompt to get prompt_ids

# # 3. STAGE 1 — Pick the function name:
# #    - options = [f.name for f in functions]
# #    - chosen_function_name, new_tokens = pick_from_options(options, prompt_ids, model)
# #    - Append new_tokens to prompt_ids
# #    - Look up which FunctionDefinition matches chosen_function_name
   
# # 4. Force the structural part: '","parameters":{'
# #    - new_tokens = force_string('","parameters":{', prompt_ids, model)
# #    - Append new_tokens to prompt_ids
   
# # 5. STAGE 2 — Generate each parameter:
# #    - parameters_dict = {}
# #    - For each (param_name, param_type) in chosen function's parameters:
# #      - Force the key: '"{param_name}":'
# #      - If param_type == "string":
# #        - Force opening quote: '"'
# #        - value, new_tokens = generate_string_value(prompt_ids, model)
# #        - parameters_dict[param_name] = value
# #      - If param_type == "number":
# #        - value, new_tokens = generate_number(prompt_ids, model)
# #        - parameters_dict[param_name] = value
# #      - If param_type == "boolean":
# #        - value, new_tokens = pick_from_options(["true","false"], prompt_ids, model)
# #        - parameters_dict[param_name] = (value == "true")
# #      - Append new_tokens to prompt_ids
# #      - If not the last parameter, force ","
   
# # 6. Build the result object:
# #    - { "prompt": prompt, "name": chosen_function_name, "parameters": parameters_dict }

# # 7. Return result

# from llm_sdk.llm_sdk import Small_LLM_Model
# import json
# smallLLM = Small_LLM_Model()

# prompt = "Greet Bader"
# import json

# # output = f'["prompt": "{prompt}"]'
# try:
#     with open('data/input/functions_definition.json') as fun_def:
#         fun_def = json.load(fun_def)
# except FileNotFoundError:
#     print("Error: functions_definition.json not found")
#     exit(1)
# except json.JSONDecodeError:
#     print("Error: functions_definition.json contains invalid JSON")
#     exit(1)
# with open('data/input/function_calling_tests.json') as fun_call:
#     fun_call = json.load(fun_call)

# # for item in fun_def:
# #     print(item["description"])
# # function_name = [item["name"] for item in fun_def]
# # print(function_name)


# # Build the prompt for the model. Take the user's request ("Greet Bader") and combine it with the function descriptions 
# # into a single text string that ends right at the point where the model should start generating the function name. 
# # The descriptions give the model the context it needs to pick correctly.


# # function_descriptions_list = [item["description"] for item in fun_def]

# # function_descriptions = " ".join(function_descriptions_list)
# # print(function_descriptions)

# vocabPath = smallLLM.get_path_to_vocab_file()


# # print(helloID.tolist())
# # print(vocabPath)

# with open(vocabPath,"r") as file:
#     vocab = json.load(file)
# id_to_token = {int(v) : k for k,v in vocab.items()}
# # for item in prompt_with_descriptions:
# #     print(item)

# # You are a function calling assistant. Available functions:
# # - fn_add_numbers:(a: number, b: number) Add two numbers together and return their sum.
# # - fn_greet: Generate a greeting message for a person by name.
# # - fn_reverse_string: Reverse a string and return the reversed result.

# # User prompt: "Greet Bader"

# # Function call: {"name":"
# # format json : {"prompt":(...) , "name": (...)a}
# llm_header_prompt = "You are a function calling assistant. Available functions:"
# func_result = ' Function call: {"name":"'

# func_descriptions_list = ["- " + item["name"] + ": "+item["description"] for item in fun_def]
# func_descriptions = " ".join(func_descriptions_list)


# prompt_enhance = llm_header_prompt + " " + func_descriptions

# prompt_with_descriptions = [ prompt_enhance + " User request:" + '"' + item["prompt"] + '"' + func_result  for item in fun_call]

# # for item in prompt_with_descriptions:
# #     print(item)

# # print(prompt_with_descriptions[5])


# promptID = smallLLM.encode(prompt_with_descriptions[2]).tolist()[0]

# # print(promptID)
# # print(smallLLM.decode(promptID))

# target_remain = [item["name"] for item in fun_def ]
# # print(target_remain)
# generated_ids = []
# output_ID = []
# allowed = []
# while target_remain and any(r != "" for r in target_remain):
#     allowed = []
#     for func_name in target_remain:
#         function_id = smallLLM.encode(func_name).tolist()[0]
#         allowed.append(function_id[0])

#     logits = smallLLM.get_logits_from_input_ids(promptID + generated_ids)

#     for index, value in enumerate(logits):
#         if index not in allowed:
#             logits[index] = float("-inf")

#     next_id = logits.index(max(logits))
#     generated_ids.append(next_id)

#     token_text = id_to_token[next_id]
#     new_remain = []
#     for remain in target_remain:
#         if remain.startswith(token_text):
#             chunk = remain[len(token_text):]
#             new_remain.append(chunk)
    
#     target_remain = new_remain

# # generated_ids_text = smallLLM.decode(generated_ids)
# # print(len(generated_ids))

# new_prompt = promptID + generated_ids
# paramter_id = smallLLM.encode('","parameters":{').tolist()[0]
# new_prompt = new_prompt + paramter_id
# print(smallLLM.decode(new_prompt))
# # print(smallLLM.decode(generated_ids))

# func_name = smallLLM.decode(generated_ids)

# paramters = [ item["parameters"] for item in fun_def if item["name"] == func_name]
# print(paramters)
# print(type(paramters))

# quote_id = smallLLM.encode('"').tolist()[0]
# # print(quote_id)


# param_name = list(paramters[0].keys())[0]   # "name"
# key_str = '"' + param_name + '":"'           # '"name":"'
# key_ids = smallLLM.encode(key_str).tolist()[0]
# new_prompt = new_prompt + key_ids


# import string
# allowed_chars = string.ascii_letters + string.digits + " "
# allowed_string_tokens = []

# for ch in allowed_chars:
#     ids = smallLLM.encode(ch).tolist()[0]
#     allowed_string_tokens.append(ids[0])

# print(len(smallLLM.decode(allowed_string_tokens)))

# allowed_tokens = allowed_string_tokens + quote_id
# tokens_value = []
# counter = 0
# while counter < 50:
#     counter += 1
#     logits = smallLLM.get_logits_from_input_ids(new_prompt + tokens_value)
    
#     for index, value in enumerate(logits):
#         if index not in allowed_tokens:
#             logits[index] = float("-inf")

#     next_id = logits.index(max(logits))
#     print(f"Step {counter}: picked '{id_to_token[next_id]}' (id {next_id})")
    
#     if next_id == quote_id[0]:
#         print("  → closing quote, stopping")
#         break
#     else:
#         tokens_value.append(next_id) 

# print(smallLLM.decode(tokens_value))