from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gensim.models import Word2Vec
import os
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import json

app = FastAPI()

# Enable CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Add your frontend URL here
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the Word2Vec model
model_path = "processed.word2vec"  # Path to your Word2Vec model
wv = Word2Vec.load(model_path).wv  # Load the word vectors

# List of files in the "scraped_articles" folder
folder_path = "scraped_articles"
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Function to tokenize a document (you can adapt this based on your tokenizer)
def tokenize_text(text: str) -> List[str]:
    return text.split()  # Tokenization by space, modify if needed for better handling

# Function to compute similarity of a document to the phrase
def compute_similarity(phrase: str, document: str) -> float:
    # Tokenize the phrase and the document
    phrase_tokens = tokenize_text(phrase)
    doc_tokens = tokenize_text(document)

    # Get word vectors for the phrase and the document
    phrase_vector = sum([wv[token] for token in phrase_tokens if token in wv])
    doc_vector = sum([wv[token] for token in doc_tokens if token in wv])

    # Compute cosine similarity
    if phrase_vector.any() and doc_vector.any():
        similarity = cosine_similarity([phrase_vector], [doc_vector])[0][0]
        return similarity
    else:
        return 0

# Pydantic model for request body
class SearchRequest(BaseModel):
    phrase: str
    top_k: int = 10

# Pydantic model for response body
class SearchResponse(BaseModel):
    Title: str
    Edition_Info: str

@app.post("/search", response_model=List[SearchResponse])
async def search(request: SearchRequest):
    phrase = request.phrase
    top_k = request.top_k
    document_scores = []

    # Process each document in the folder
    for file in files:
        document_path = os.path.join(folder_path, file)
        with open(document_path, "r", encoding="utf-8") as f:
            document_content = f.read()

        # Compute similarity between the document and the phrase
        similarity_score = compute_similarity(phrase, document_content)
        document_scores.append((file, similarity_score))

    # Sort documents based on similarity score in descending order
    document_scores.sort(key=lambda x: x[1], reverse=True)

    # Get the top k files
    top_k_files = document_scores[:top_k]

    # Extract relevant information from the top k files
    response = []
    for file, _ in top_k_files:
        document_path = os.path.join(folder_path, file)
        with open(document_path, "r", encoding="utf-8") as f:
            document_content = f.read()

        # Extract relevant information
        data = json.loads(document_content)
        response.append(SearchResponse(
            Title=data.get("Title", ""),
            Edition_Info=data.get("Edition Info", "")
        ))

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
