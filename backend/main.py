from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gensim.models import Word2Vec
import os
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import json
import numpy as np

app = FastAPI()

# Enable CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and file paths
model_path = "processed.word2vec"
wv = Word2Vec.load(model_path).wv
folder_path = "scraped_articles"
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

# Utility functions
def tokenize_text(text: str) -> List[str]:
    return text.split()

def compute_similarity(phrase: str, document: str) -> float:
   phrase_tokens = tokenize_text(phrase)
   doc_tokens = tokenize_text(document)


   phrase_vecs = [wv[token] for token in phrase_tokens if token in wv]
   doc_vecs = [wv[token] for token in doc_tokens if token in wv]


   if not phrase_vecs or not doc_vecs:
       return 0.0


   phrase_vector = np.sum(phrase_vecs, axis=0)
   doc_vector = np.sum(doc_vecs, axis=0)


   return cosine_similarity([phrase_vector], [doc_vector])[0][0]
# Pydantic models
class SearchRequest(BaseModel):
    phrase: str
    top_k: int = 10

class SearchResponse(BaseModel):
    Title: str
    Edition_Info: str
    filename: str

# Endpoints
@app.get("/articles/{filename}")
async def get_article(filename: str):
    file_path = os.path.join(folder_path, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Article not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/search", response_model=List[SearchResponse])
async def search(request: SearchRequest):
    document_scores = []
    
    for file in files:
        with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
            content = f.read()
            similarity = compute_similarity(request.phrase, content)
            document_scores.append((file, similarity))
    
    sorted_files = sorted(document_scores, key=lambda x: x[1], reverse=True)[:request.top_k]
    
    results = []
    for file, _ in sorted_files:
        with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
            data = json.load(f)
            results.append(SearchResponse(
                Title=data.get("Title", ""),
                Edition_Info=data.get("Edition Info", ""),
                filename=file
            ))
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
