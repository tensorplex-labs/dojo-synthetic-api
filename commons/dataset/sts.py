from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sys
sys.path.append("./")
from commons.dataset import GENERATOR_MODELS
import os
import json
import numpy as np
import matplotlib.pyplot as plt

directory = "commons/dataset/sample_synthetic_bank"
sentences = []

# optional filename to use file instead of directory
# file = None
file = "output_gpt4_turbo_40_v4.json"

for filename in os.listdir(directory):
    extension = str(file) if file else ".json"
    if filename.endswith(extension): 
        file_path = os.path.join(directory, filename)
        
        # Read the JSON file
        with open(file_path, "r") as file:
            json_data = json.load(file)
            
            # Append each question-model pair to sentences list
            for item in json_data:
                sentences.append({
                    'question': item['question'], 
                    'model': item['model']
                })
model = SentenceTransformer('all-MiniLM-L6-v2')
# model = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1")


sentence_embeddings = model.encode([obj['question'] for obj in sentences])
# sentence_embeddings = model.encode(sentences)

print("Sentence embeddings:")
print(sentence_embeddings)

cos_sim_matrix = cosine_similarity(sentence_embeddings)
print("Cosine Similarity Matrix:")
print(np.array2string(cos_sim_matrix, precision=2, separator=', '))



def process_cos_sim_matrix (sentences, prompt_model):
    trimmed_sentences = [sentence for sentence in sentences if sentence['model'] == prompt_model]
    print(trimmed_sentences)
    trimmed_sentence_embeddings = model.encode([obj['question'] for obj in trimmed_sentences])
    trimmed_cos_sim_matrix = cosine_similarity(trimmed_sentence_embeddings)
    for i in range(len(trimmed_cos_sim_matrix)):
        row = trimmed_cos_sim_matrix[i]
        second_largest = np.partition(row, -2)[-2]
        second_largest_position = np.where(row == second_largest)[0][0]
        smallest = np.min(row)
        smallest_position = np.where(row == smallest)[0][0]
        print(f"The prompt: \n {trimmed_sentences[i]['question']}")
        print(f"produced by {trimmed_sentences[i]['model']}")
        print(f"is most similar to the prompt: \n {trimmed_sentences[second_largest_position]['question']}")
        print(f"produced by {trimmed_sentences[second_largest_position]['model']}")
        print(f"with cosine similarity of {second_largest:.3f}")
        print(f"and least similar to the prompt: \n {trimmed_sentences[smallest_position]['question']}")
        print(f"produced by {trimmed_sentences[smallest_position]['model']}")
        print(f"with cosine similarity of {smallest:.3f}")
        print()

    cos_sim_adjacent = []
    for i in range(len(trimmed_cos_sim_matrix) -1):
      cos_sim_adjacent.append(trimmed_cos_sim_matrix[i][i+1])

    series = []
    for i in range(len(cos_sim_adjacent) - 1):
      series.append(cos_sim_adjacent[i + 1] - cos_sim_adjacent[i])


    # Start of Selection
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))


    # Start of Selection
    ax1.plot(series)
    ax1.plot(cos_sim_adjacent)
    window_size = 5
    moving_avg = np.convolve(cos_sim_adjacent, np.ones(window_size)/window_size, mode='valid')
    ax1.axhline(y=np.mean(cos_sim_adjacent), color='blue', linewidth=2)  # Add a bold horizontal line at the simple moving average of last 5 points
    print(f"Mean of cosine similarity for {len(cos_sim_adjacent)} : {np.mean(cos_sim_adjacent)}")

    ax1.plot(moving_avg, label='Moving Average')
    ax1.legend()
    ax1.set_xlabel('Instruction Iterations')
    
    # Highlight negative points in red
    negative_points = [i for i, value in enumerate(series) if value < 0]
    ax1.plot(negative_points, [series[i] for i in negative_points], 'ro')
    
    
    ax1.set_ylabel('Value')
    ax1.set_title('Timeseries Plot')
    ax1.grid(True)
    ax1.axhline(y=0, color='black', linewidth=2)  # Add a bold horizontal line at y=0

    im = ax2.imshow(trimmed_cos_sim_matrix, cmap='viridis')
    fig.colorbar(im, ax=ax2, label='Cosine Similarity')

    # Add labels for each sentence
    labels = [f"{trimmed_sentences[i]['model']}" for i in range(len(trimmed_sentences))]
    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels, rotation=90)
    ax2.set_yticks(range(len(labels)))
    ax2.set_yticklabels(labels)

    ax2.set_xlabel('Models')
    ax2.set_ylabel('Models')
    ax2.set_title('Cosine Similarity Matrix')

    plt.tight_layout()
    # save as file
    plt.savefig(f"cos_sim_matrix_new.png")
    plt.show()



for prompt_model in set(GENERATOR_MODELS):
    process_cos_sim_matrix (sentences, prompt_model)





