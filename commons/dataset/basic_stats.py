import pandas as pd
from collections import Counter
from math import comb

import csv

# Read the CSV file as a list
csv_file = 'sampled_objects_new_version.csv'  # Replace with your CSV file path
# csv_file = 'sampled_objects_baseline.csv'
with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    words = [row[0] for row in reader if row]

# Remove any empty strings that might result from trailing commas
words = [word for word in words if word]

# Calculate total number of words
total_words = len(words)

# Calculate word frequencies
word_counts = Counter(words)

# Identify unique words and duplicates
unique_words = [word for word, count in word_counts.items() if count == 1]
duplicate_words = {word: count for word, count in word_counts.items() if count > 1}

# Calculate the number of unique words
num_unique_words = len(unique_words) + len(duplicate_words.items())

# Calculate the number of duplicate words
num_duplicate_words = total_words - num_unique_words 


# Calculate probability of not getting the same word at least twice over n tries
def prob_all_different(n, total_words):
    if n > total_words:
        return 0
    prob = 1.0
    for i in range(n):
        prob *= (total_words - i) / total_words
    return prob

# Calculate probability of getting the same word at least twice over n tries
def prob_same_word_at_least_twice(n, total_words):
    return 1 - prob_all_different(n, total_words)

# Test for different values of n
tries = [2, 3, 4, 5, 10]
probabilities = {n: prob_same_word_at_least_twice(n, total_words) for n in tries}

# Output statistics
print(f"Total number of words: {total_words}")
print(f"Number of unique words: {num_unique_words}")
print(f"Number of duplicate words: {num_duplicate_words}")

print("\nDuplicates (word: count):")
for word, count in duplicate_words.items():
    print(f"{word}: {count}")

def calculate_repetition_probability(words_list, n):
    # Count the frequency of each word in the list
    word_counts = Counter(words_list)
    
    # Calculate total number of unique words
    unique_words = len(word_counts)
    
    # If n is greater than the number of unique words, repetition is certain
    if n > unique_words:
        return 1.0
    
    # Calculate the probability of no repetition using the complement of the birthday problem
    no_repetition_prob = 1.0
    for i in range(n):
        no_repetition_prob *= (unique_words - i) / unique_words
    
    # The probability of at least one repetition
    repetition_prob = 1 - no_repetition_prob
    
    return repetition_prob

# Example usage
n = 10  # Number of samples
probability = calculate_repetition_probability(words, n)
print(f"Probability of getting at least one word twice after {n} samples: {probability:.4f}")


# for n in tries:
#     print(f"Probability of getting the same word at least twice over {n} tries: {probabilities[n]:.4f}")
