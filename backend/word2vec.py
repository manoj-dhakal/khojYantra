from gensim.models import Word2Vec
from itertools import combinations

# Load the Word2Vec model
model_path = "processed.word2vec"  # Path to your Word2Vec model
wv = Word2Vec.load(model_path).wv  # Load the word vectors

# List of Nepali words
nepali_words = ["नेपाल", "पुस्तक", "शिक्षा", "प्रेम", "खेलकुद","किताब" ]

# List to store similarity scores
similarity_scores = []

# Compute similarity scores for all combinations of words
for word1, word2 in combinations(nepali_words, 2):
    if word1 in wv and word2 in wv:
        similarity = wv.similarity(word1, word2)
        similarity_scores.append((word1, word2, similarity))
    else:
        print(f"One or both words ('{word1}', '{word2}') are not in the vocabulary.")

# Sort the scores in descending order based on similarity
similarity_scores.sort(key=lambda x: x[2], reverse=True)

# Print the sorted scores
print("\nWord Pair Similarity Scores (Descending Order):")
for word1, word2, similarity in similarity_scores:
    print(f"Similarity between '{word1}' and '{word2}': {similarity:.4f}")
    
    
    
    
