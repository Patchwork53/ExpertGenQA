
import json
from openai import OpenAI
import os
import ast

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def extract_json(text):
    starting_index = text.find("{")
    #find the last occurence of }
    ending_index = len(text) - text[::-1].find("}")
    return json.loads(text[starting_index:ending_index])
          

def list_to_string(l):
    result = ""
    for i, x in enumerate(l):
        result += f"{i+1}. {x}\n"
    return result

def extract_list(text):
    starting_index = text.find("[")
    ending_index = text.find("]")
    return ast.literal_eval(text[starting_index:ending_index+1])


def build_history(dict_list, user_template):
    history = []

    for i, d in enumerate(dict_list):
        passage = d["passage"]
        instruction = d["instruction"]

        selected_topic = d["instruction_topic"]
        topics = d["topics_in_passage"]
        prompt = user_template.format(PASSAGE=passage, selected_topic=selected_topic, topics=topics)
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": instruction})

    return history

def generate_gpt(prompt, history=[], temperature=None, model="gpt-4o-mini", n = 1):
    messages = history + [{"role": "user", "content": prompt}]
    if temperature is not None:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            n = n
        )
    else:
            
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            n = n
        )
    
    responses = [x.message.content for x in completion.choices]
    return responses

