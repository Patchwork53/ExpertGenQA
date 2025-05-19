from utils import *
from tqdm import tqdm
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Extract topics from passages and questions')
    parser.add_argument('--input_file', type=str, default='expert_written_qa.json',
                        help='Path to input JSON file')
    parser.add_argument('--output_file', type=str, default='expert_written_qa_with_topics.json',
                        help='Path to output JSON file')
    return parser.parse_args()

def process_data(input_file, output_file):
    extraction_template = """{passage}

    -----
    What are the main topics covered in the above passage?
    """

    follow_up_prompt = "Extract the topics in a JSON with key `topics` and its value being the the list of topic names. Reply with only the JSON without any other text."

    follow_up_question = "Which of the topics is the following question related to?\n\nQuestion: {question}"

    follow_up_prompt_2 = "Reply with only the topic name related to the question without any other text. If the question relates to multiple topics, reply with a python list of the topic names. If the question is not related to any of the topics, reply with 'None'."

    with open(input_file, 'r') as f:
        input_data = json.load(f)

    passage_topics = {}
    to_save = []

    for item in tqdm(input_data):
        passage = item['passage']
        if passage not in passage_topics:
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
                    print(extracted_topics)
                    break
                except Exception as e:
                    print(e)
                    print(structured_topics)
                    
            passage_topics[passage] = extracted_topics
        else:
            extracted_topics = passage_topics[passage]

        item['topics_in_passage'] = extracted_topics
        
        history.append({"role": "user", "content": follow_up_prompt})
        history.append({"role": "assistant", "content": structured_topics})

        follow_up_response = generate_gpt(follow_up_question.format(question=item['instruction']), 
                                        history=history)[0]

        history.append({"role": "user", "content": follow_up_response})

        follow_up_response = generate_gpt(follow_up_prompt_2, history=history)

        item['instruction_topic'] = follow_up_response

        to_save.append(item)

    with open(output_file, 'w') as f:
        json.dump(to_save, f, indent=4)

def main():
    args = parse_args()
    process_data(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
