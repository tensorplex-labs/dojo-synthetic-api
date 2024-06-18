import pandas as pd
from collections import Counter
from math import comb

# Read the CSV file as a single string
csv_file = 'sampled_objects_objects_only.csv'  # Replace with your CSV file path
with open(csv_file, 'r') as file:
    words_string = file.read()

# Split the string by commas to get the list of words
words = words_string.split(',')

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
num_unique_words = len(unique_words)

# Calculate the number of duplicate words
num_duplicate_words = total_words - num_unique_words

# Calculate probabilities
prob_unique_word = num_unique_words / total_words
prob_duplicate_word = num_duplicate_words / total_words

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

for n in tries:
    print(f"Probability of getting the same word at least twice over {n} tries: {probabilities[n]:.4f}")
