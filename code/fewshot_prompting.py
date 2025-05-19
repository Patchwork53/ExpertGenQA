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
    parser.add_argument('--output_file', type=str, default="fewshotprompting_generations.json",
                        help='Path to output file for generated QA pairs')
    parser.add_argument('--num_combos', type=int, default=1,
                        help='Number of combinations to try')
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



def create_user_template():
    template = f"Passage: {{PASSAGE}}\n\n-----\nGenerate a question from the passage."

    forbidden_list = [
        "Ask about specific fields/blocks/codes in forms",
        "Ask about obscure codes that even a domain expert would not memorize",
        "Ask questions without providing sufficient context for answerers who won't have access to the passage"
    ]

    if forbidden_list:
        template += f"\n\nDo NOT:\n{list_to_string(forbidden_list)}"
    
    return template

def main():
    args = parse_args()
    
    # Load data
    human_data = load_data(args.input_file)
    document_chunks_with_topic = load_document_chunks()
    user_template = create_user_template()
    
    # Generate synthetic questions
    synthetic_generations = []
    
    for passage_id, item in enumerate(tqdm(document_chunks_with_topic)):
        passage = item["chunk"]

        for i in range(args.num_combos):
                random.seed(i)
                sampled_examples = random.sample(human_data, args.num_fewshots)
                history = build_history(sampled_examples, user_template)

                
                prompt = user_template.format(PASSAGE=passage)
                responses = generate_gpt(prompt, 
                                         history, 
                                         temperature=1,   
                                         n=args.num_samples)

                for response in responses:
                    # print(response)
                    synthetic_generations.append({
                        "passage": passage,
                        "instruction": response,
                        "prompt": prompt
                    })

    # Save generations
    with open(args.output_file, "w") as f:
        json.dump(synthetic_generations, f, indent=4)

if __name__ == "__main__":
    main()
