import os
import json
import argparse
from tqdm import tqdm
from typing import Dict, List, Set
from Levenshtein import distance


def word_overlap(s1, s2):
    words1 = s1.split()
    words2 = s2.split()
    if not words1 or not words2:
        return 0.0, 0.0
    common_words = set(words1).intersection(words2)
    overlap1 = len(common_words) / len(words1)
    overlap2 = len(common_words) / len(words2)
    return overlap1, overlap2

def bigram_overlap(s1, s2):
    bigrams1 = set(zip(s1.split(), s1.split()[1:]))
    bigrams2 = set(zip(s2.split(), s2.split()[1:]))
    if not bigrams1 or not bigrams2:
        return 0.0, 0.0
    common_bigrams = bigrams1.intersection(bigrams2)
    overlap1 = len(common_bigrams) / len(bigrams1)
    overlap2 = len(common_bigrams) / len(bigrams2)
    return overlap1, overlap2

def trigram_overlap(s1, s2):
    trigrams1 = set(zip(s1.split(), s1.split()[1:], s1.split()[2:]))
    trigrams2 = set(zip(s2.split(), s2.split()[1:], s2.split()[2:]))
    if not trigrams1 or not trigrams2:
        return 0.0, 0.0
    common_trigrams = trigrams1.intersection(trigrams2)
    overlap1 = len(common_trigrams) / len(trigrams1)
    overlap2 = len(common_trigrams) / len(trigrams2)
    return overlap1, overlap2

def levenstein_distance(s1, s2):
    return distance(s1, s2), distance(s2, s1)


def deduplicate_sentences(sentences: List[str], threshold: float, overlap_fn) -> Set[str]:
    """Deduplicate sentences based on overlap threshold."""
    if not sentences:
        return set()

    unique_sentences = [sentences[0]]
    
    for s1 in sentences[1:]:
        modified = False
        new_unique = []
        
        for s2 in unique_sentences:
            overlap1, overlap2 = overlap_fn(s1, s2)

            if overlap1 > threshold and overlap2 > threshold:
                longer = s1 if len(s1) > len(s2) else s2
                new_unique.append(longer)
                modified = True
            elif overlap1 > threshold and overlap2 <= threshold:
                new_unique.append(s2)
                modified = True
            elif overlap1 <= threshold and overlap2 > threshold:
                new_unique.append(s1)
                modified = True
            else:
                if s2 not in new_unique:
                    new_unique.append(s2)

        if not modified and s1 not in new_unique:
            new_unique.append(s1)

        unique_sentences = list(set(new_unique))

    return set(unique_sentences)

def process_data(input_path, overlap_fn, threshold):
    """Process and filter the input data."""
    with open(input_path) as f:
        all_gens = json.load(f)

    # Remove duplicates and passages from instructionss
    to_keep = []
    seen_instructions = set()
    for item in all_gens:
        if "passage" not in item["instruction"].lower() and item["instruction"].lower() not in seen_instructions:
            to_keep.append(item)
            seen_instructions.add(item["instruction"].lower())

    # Group by passage
    passage_items = {}
    for item in to_keep:
        if item["passage"] not in passage_items:
            passage_items[item["passage"]] = []
        passage_items[item["passage"]].append(item)

    # Deduplicate instructionss for each passage
    filtered_items = []
    for passage in passage_items:
        items = passage_items[passage]
        instructions = [item["instruction"] for item in items]
        instructions.sort(key=lambda x: len(x))
        new_instructions = deduplicate_sentences(instructions, threshold, overlap_fn)
        
        for item in items:
            if item["instruction"] in new_instructions:
                filtered_items.append(item)

    return filtered_items

def main():
    parser = argparse.ArgumentParser(description='Filter and deduplicate instructions-answer pairs.')
    parser.add_argument('--input_file', required=True, help='Input JSON file path')
    parser.add_argument('--output_file', required=True, help='Output JSON file path')
    parser.add_argument('--overlap_fn', default='bigram', choices=['word', 'bigram', 'trigram', 'levenshtein'])
    parser.add_argument('--threshold', type=float, default=0.3, 
                        help='Overlap threshold for deduplication (default: 0.3)')
    
    
    args = parser.parse_args()

    if args.overlap_fn == 'word':
        overlap_fn = word_overlap
    elif args.overlap_fn == 'bigram':
        overlap_fn = bigram_overlap
    elif args.overlap_fn == 'trigram':
        overlap_fn = trigram_overlap
    elif args.overlap_fn == 'levenshtein':
        overlap_fn = levenstein_distance
    else:
        raise ValueError(f"Invalid overlap function: {args.overlap_fn}")
    
    # Process the data
    filtered_data = process_data(args.input, overlap_fn, args.threshold)
    
    print(f"Original items: {len(json.load(open(args.input)))}")
    print(f"Filtered items: {len(filtered_data)}")

    # Save results
    with open(args.output, "w") as f:
        json.dump(filtered_data, f, indent=2)
    
    print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()
