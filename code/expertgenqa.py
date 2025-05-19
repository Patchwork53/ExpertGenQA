import pickle
import json
import random
import math
from tqdm import tqdm
import time
from copy import deepcopy
import ast
from utils import *
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Generate synthetic QA pairs from documents')
    parser.add_argument('--input_file', type=str, default="expert_written_qa.json",
                        help='Path to input file containing expert-written QAs examples')
    parser.add_argument('--output_file', type=str, default="expertgenqa_generations.json",
                        help='Path to output file for generated QA pairs')
    parser.add_argument('--num_combos', type=int, default=1,
                        help='Number of combinations of examples to try')
    parser.add_argument('--num_samples', type=int, default=1,
                        help='Number of generations to sample per prompt')
    parser.add_argument('--num_fewshots', type=int, default=1,
                        help='Number of few-shot examples used')
    parser.add_argument('--doc_set_path', type=str, default="doc_set_with_topics.pkl",
                        help='Path to document set with topics')
    return parser.parse_args()

def load_data(input_file):
    with open(input_file, "r") as f:
        return json.load(f)

def load_document_chunks(doc_set_path):
    with open(doc_set_path, "rb") as f:
        document_chunks = pickle.load(f)
    return document_chunks

def build_style_dict(human_data):
    style_dict = {}
    for d in human_data:
        style = d["style"]
        if style not in style_dict:
            style_dict[style] = []
        d2 = d.copy()
        del d2["style"]
        style_dict[style].append(d2)
    return style_dict

def create_user_template():
    template = f"""Passage: {{PASSAGE}}

-----

The passage above covers the following topics:
{{topics}}

Generate a question from the passage related to '{{selected_topic}}'."""

    forbidden_list = [
        "Ask about specific fields/blocks/codes in forms",
        "Ask about obscure codes that even a domain expert would not memorize",
        "Ask questions without providing sufficient context for answerers who won't have access to the passage"
    ]

    if forbidden_list:
        template += f"\n\nDo NOT:\n{list_to_string(forbidden_list)}"
    
    return template


def extract_topics(passage):
    extraction_template = """{passage}

    -----
    What are the main topics covered in the above passage?
    """

    follow_up_prompt = "Extract the topics in a JSON with key `topics` and its value being the the list of topic names. Reply with only the JSON without any other text."

    prompt = extraction_template.format(passage=passage)
    unstructured_topics = generate_gpt(prompt)[0]

    history = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": unstructured_topics},
    ]

    while True:
        structured_topics = generate_gpt(follow_up_prompt, history=history)[0]
        try:
            extracted_topics = extract_json(structured_topics)['topics']
            break
        except Exception as e:
            # Alternative: Use openai JSON mode to guarantee that the response is a JSON
            print(e)
            print(structured_topics)
    
    return extracted_topics

def main():
    args = parse_args()
    
    # Load data
    human_data = load_data(args.input_file)
    document_chunks_with_topic = load_document_chunks(args.doc_set_path)
    
    # Build categories dictionary
    style_dict = build_style_dict(human_data)
    
    # Print style statistics
    for style in style_dict:
        print(style, len(style_dict[style]))
    
    # Create template
    user_template = create_user_template()
    
    # Generate synthetic questions
    synthetic_generations = []
    
    for passage_id, item in enumerate(tqdm(document_chunks_with_topic)):
        passage = item["chunk"]
        topics_in_passage = extract_topics(passage)

        for style in style_dict.keys():
            q_list = []
            num_human_questions = len(style_dict[style])
            num_combos_to_try = min(args.num_combos, 
                                          math.ceil(num_human_questions/args.num_fewshots))

            for i in range(num_combos_to_try):
                random.seed(i)
                sampled_examples = random.sample(style_dict[style], 
                                               min(args.num_fewshots, len(style_dict[style])))

                history = build_history(sampled_examples, user_template)

                for possible_topic in topics_in_passage:
                    prompt = user_template.format(PASSAGE=passage, 
                                                topics=list_to_string(topics_in_passage), 
                                                selected_topic=possible_topic)
                    responses = generate_gpt(prompt, history, temperature=1, 
                                           n=args.num_samples)

                    for response in responses:
                        # print(response)
                        synthetic_generations.append({
                            "passage": passage,
                            "instruction": response,
                            "prompt": prompt,
                            "instruction_style": style,
                            "instruction_topic": possible_topic,
                        })

    # Save generations
    with open(args.output_file, "w") as f:
        json.dump(synthetic_generations, f, indent=4)

if __name__ == "__main__":
    main()
