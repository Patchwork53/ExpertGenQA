# %%
from utils import *
from tqdm import tqdm
import json
import pickle

# %%
# FOLDER = "static_random_example_no_sys"
# FOLDER = "static_random_example"
# FOLDER = "static_passage_cluster"
# FOLDER = "bloom_random_no_sys"
# FOLDER = "double_categorization_sys_cluster"
# %%
# Change this as needed

input_file_path = 'reward_topic_bloom/mdcure.json'
output_file_path = input_file_path

with open(input_file_path, 'r') as f:
    input_data = json.load(f)

example_file_path = "reward_topic_bloom/human.json"

import random



with open(example_file_path, 'r') as f:
    examples = json.load(f)

example_instructions = [x['instruction'] for x in examples]

random_examples = random.sample(example_instructions, min(50, len(example_instructions)))


paraphrase_template = """<target_question>
{question}
</target_question>

<examples>
{examples}
</examples>

Please paraphrase the target question to match the style of the examples. Do not make any changes that would alter the meaning and change its answer. Do not answer the question. Respond with only the rephrased question (without any tags)."""

with open(input_file_path, 'r') as f:
    to_rephrase_data = json.load(f)

output_data = []
for item in tqdm(input_data):
    instruction = item['instruction']
    prompt = paraphrase_template.format(question=instruction, examples=list_to_string(random_examples))

    rephrased_instruction = generate_gpt(prompt)
    item['rephrased'] = rephrased_instruction
    output_data.append(item)

with open(output_file_path, 'w') as f:
    json.dump(output_data, f, indent=4)





