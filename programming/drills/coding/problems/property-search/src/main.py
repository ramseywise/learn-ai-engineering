from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from contextlib import asynccontextmanager
from typing import List, Optional
import faiss
import numpy as np
import json
from pathlib import Path

# Global variables
model = None
index = None
properties = []

# Configuration
TOP_K_RESULTS = 5
PRICE_BOOST_FACTOR = 10

class SearchQuery(BaseModel):
    query: str
    max_results: Optional[int] = 5

class SearchResult(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    bedrooms: List[str]
    features: List[str]
    score: float

def apply_price_boost(score: float, price: float) -> float:
    """Apply price-based boosting to properties cheaper than 500000."""
    price_factor = 1.0 - ((500000 - min(price, 500000)) / 500000) * PRICE_BOOST_FACTOR
    return score * price_factor

def load_properties():
    """Load properties and build search index."""
    global properties, index, model

    model = SentenceTransformer('all-MiniLM-L6-v2')

    properties_file = Path(__file__).parent / "properties.json"
    with open(properties_file, 'r') as f:
        properties = json.load(f)

    property_texts = []
    for property in properties:
        text = (
            f"name: {property['name']}\n"
            f"description: {property['description']}\n"
            f"category: {property['category']}\n"
            f"bedrooms: {', '.join(property['bedrooms'])}\n"
            f"features: {', '.join(property['features']) }\n"
        )
        property_texts.append(text)

    embeddings = model.encode(property_texts)
    embeddings = np.array(embeddings).astype('float32')

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    # Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup."""
    load_properties()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    """Serve the main HTML page."""
    html_file = Path(__file__).parent / "index.html"
    with open(html_file, 'r') as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.post("/search")
async def search(query: SearchQuery):
    """Search for properties based on semantic similarity."""
    query_embedding = model.encode([query.query])
    query_embedding = np.array(query_embedding).astype('float32')
    faiss.normalize_L2(query_embedding)

    k = query.max_results or TOP_K_RESULTS
    distances, indices = index.search(query_embedding, k)

    results = []
    for idx, distance in zip(indices[0][1:], distances[0][1:]):
        property = properties[idx]

        score = float(distance)

        score = apply_price_boost(score, property['price'])

        result = SearchResult(
            id=property['id'],
            name=property['name'],
            description=property['description'],
            price=property['price'],
            category=property['category'],
            bedrooms=property['bedrooms'],
            features=property['features'],
            score=score
        )
        results.append(result)

    return {"results": results, "total": len(results)}
