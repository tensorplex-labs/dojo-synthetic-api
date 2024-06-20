from nomic import atlas, embed
import pandas
import numpy as np


# def csv_to_numpy_array(file_path):
#     with open(file_path, 'r') as file:
#         # Read the entire file content
#         content = file.read()
        
#         # Split the content by commas to get the list of words
#         words = content.split(',')
        
#         # Convert the list of words to a NumPy array
#         words_array = np.array(words)
        
#     return words_array

# words_list = csv_to_numpy_array('test.csv')

# embeddings = embed.text(words_list.tolist(), model='nomic-embed-text-v1.5', task_type='clustering')
# embeddings = np.array(embeddings['embeddings'])
# # dataset = atlas.map_data(embeddings=embeddings)
# dataset = atlas.map_data(data=words_list)

import csv

def convert_csv_in_place(file_path):
    # Read the input CSV file
    with open(file_path, 'r') as file:
        content = file.read()
        
        # Split the content by commas to get the list of words
        words = content.split(',')
    
    # Write to the same CSV file
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header
        writer.writerow(['objects'])
        
        # Write each word in a new row
        for word in words:
            writer.writerow([word.strip()])

# Example usage
file_path = 'sampled_objects_new_version.csv'  # Replace with the path to your CSV file
# convert_csv_in_place(file_path)

words = pandas.read_csv(file_path)
dataset = atlas.map_data(data=words, indexed_field='objects')
