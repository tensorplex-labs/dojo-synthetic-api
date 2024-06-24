import asyncio
import random
import aiohttp
from nltk.corpus import wordnet
import ety
# Download WordNet data if not already available
import nltk
nltk.download('wordnet')

import requests
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# def get_total_abs_match_count(query_string):
#     url = f"https://api.ngrams.dev/eng/search?query={query_string}"
#     response = requests.get(url)
    
#     if response.status_code == 200:
#         data = response.json()
#         total_abs_match_count = sum(ngram['absTotalMatchCount'] for ngram in data['ngrams'])
#         return query_string, total_abs_match_count
#     else:
#         print(f"Failed to get data for query: {query_string}")
#         return query_string, 0

# def process_and_sort_strings(string_arr):
#     results = []
    
#     with ThreadPoolExecutor() as executor:
#         future_to_string = {executor.submit(get_total_abs_match_count, string): string for string in string_arr}
        
#         for future in as_completed(future_to_string):
#             string, total_abs_match_count = future.result()
#             print(f"Total match count for '{string}': {total_abs_match_count}")
#             results.append((string, total_abs_match_count))
    
#     # Sort the results in descending order by the total_abs_match_count
#     sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
#     return sorted_results

async def fetch_total_abs_match_count(session, query_string):
    url = f"https://api.ngrams.dev/eng/search?query={query_string}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()
            total_abs_match_count = sum(ngram['absTotalMatchCount'] for ngram in data['ngrams'])
            return query_string, total_abs_match_count
    except aiohttp.ClientError as e:
        print(f"Error fetching data for query '{query_string}': {e}")
        return query_string, 0

async def process_and_sort_strings(string_arr):
    results = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for string in string_arr:
            task = fetch_total_abs_match_count(session, string)
            tasks.append(task)
        
        # Gather all tasks concurrently
        responses = await asyncio.gather(*tasks)
        
        for response in responses:
            string, total_abs_match_count = response
            print(f"Total match count for '{string}': {total_abs_match_count}")
            results.append((string, total_abs_match_count))
    
    # Sort the results in descending order by the total_abs_match_count
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    return sorted_results


def get_all_words():
    noun_synsets = list(wordnet.all_synsets('n'))
    object_synsets = [synset for synset in noun_synsets if (synset.lexname() == 'noun.artifact' or synset.lexname == 'noun.food' or synset.lexname() == 'noun.shape')]
    # transform each to lowercase and convert _ to space
    transformed_words = [synset.lemmas()[0].name().replace('_', ' ').lower() for synset in object_synsets]
    return transformed_words

def write_results_to_csv(results, filename="results.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["word", "count"])
        writer.writerows(results)
    print(f"Results written to {filename}")

def get_random_object_words(n=10):
    # Get all noun synsets
    noun_synsets = list(wordnet.all_synsets('n'))
    # Filter to get only common objects (excluding abstract nouns)
    # object_synsets = [synset for synset in noun_synsets if (synset.lexname() == 'noun.artifact' or synset.lexname() == 'noun.object' or synset.lexname() == 'noun.plant' or synset.lexname == 'noun.food' or synset.lexname() == 'noun.shape')]
    object_synsets = [synset for synset in noun_synsets if (synset.lexname() == 'noun.artifact' or synset.lexname == 'noun.food' or synset.lexname() == 'noun.shape')]
    print("lenth of object_synsets", len(object_synsets))
    # Get random words from the filtered list
    random_words = [random.choice(object_synsets).lemmas()[0].name().replace('_', ' ').lower() for _ in range(n)]
    #unmodified random words
    # random_words = [random.choice(object_synsets).lemmas()[0].name() for _ in range(n)]
    for i in random_words:
        etymology = ety.tree(i)
        print(i, etymology)
    return random_words

# # Get 10 random object words
# random_object_words = get_random_object_words(100)
# print(random_object_words)

# words = get_all_words()

# one_word_strings = [s for s in words if len(s.split()) == 1]
# print("Total words:", len(words))
# print("Total one word strings:", len(one_word_strings))

# seen = set()
# unique_words = [x for x in words if not (x in seen or seen.add(x))]

# print("Total unique words:", len(unique_words))
# # print(words)
# processed = process_and_sort_strings(unique_words)
# write_results_to_csv(processed, filename="results_unique_words.csv")
# # print(processed)
    
    
async def main():
    words = get_all_words()

    one_word_strings = [s for s in words if len(s.split()) == 1]
    print("Total words:", len(words))
    print("Total one word strings:", len(one_word_strings))

    seen = set()
    unique_one_words = [x for x in one_word_strings if not (x in seen or seen.add(x))]

    print("Total unique words:", len(unique_one_words))
    # print(words)
    sorted_results = await process_and_sort_strings(unique_one_words)
    write_results_to_csv(sorted_results)

if __name__ == "__main__":
    asyncio.run(main())