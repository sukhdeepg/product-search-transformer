import torch
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util

app = FastAPI(title="Product Search with Sentence Transformers")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# we'll load model on demand
model = None

# Function to get the model (lazy loading)
def get_model():
    global model
    if model is None:
        try:
            print("Loading sentence transformer model...")
            model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Smaller model
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    return model

# Sample product data with expanded categories
products = [
    # Electronics
    {"id": 1, "name": "Smartphone", "description": "High-end smartphone with advanced camera and long battery life", "category": "Electronics"},
    {"id": 2, "name": "Laptop", "description": "Powerful laptop for professional use with dedicated graphics card", "category": "Electronics"},
    {"id": 3, "name": "Headphones", "description": "Wireless noise-cancelling headphones with premium sound quality", "category": "Electronics"},
    {"id": 4, "name": "Smart Watch", "description": "Fitness tracker and smartwatch with heart rate monitoring", "category": "Electronics"},
    {"id": 5, "name": "Tablet", "description": "Lightweight tablet with high-resolution display for reading and browsing", "category": "Electronics"},
    {"id": 6, "name": "Bluetooth Speaker", "description": "Portable waterproof speaker with deep bass and long battery life", "category": "Electronics"},
    {"id": 7, "name": "Digital Camera", "description": "Professional DSLR camera with multiple lenses and 4K video recording", "category": "Electronics"},
    {"id": 8, "name": "Gaming Console", "description": "Next-generation gaming console with 4K graphics and fast loading times", "category": "Electronics"},
    {"id": 9, "name": "External Hard Drive", "description": "High-capacity storage device for backups and file transfers", "category": "Electronics"},
    {"id": 10, "name": "Wireless Mouse", "description": "Ergonomic wireless mouse with customizable buttons and long battery life", "category": "Electronics"},
    
    # Food Items
    {"id": 11, "name": "Organic Pasta", "description": "Whole grain pasta made from organic ingredients, perfect for healthy meals", "category": "Food"},
    {"id": 12, "name": "Chocolate Cookies", "description": "Delicious cookies with chunks of premium dark chocolate", "category": "Food"},
    {"id": 13, "name": "Fresh Fruit Basket", "description": "Assortment of seasonal fruits including apples, oranges, and berries", "category": "Food"},
    {"id": 14, "name": "Gourmet Coffee", "description": "Premium single-origin coffee beans with rich flavor and aroma", "category": "Food"},
    {"id": 15, "name": "Artisan Bread", "description": "Freshly baked sourdough bread made with traditional methods", "category": "Food"},
    {"id": 16, "name": "Protein Bars", "description": "Nutritious snack bars with 20g of protein and natural ingredients", "category": "Food"},
    {"id": 17, "name": "Organic Honey", "description": "Raw, unfiltered honey from local beekeepers with natural health benefits", "category": "Food"},
    {"id": 18, "name": "Gourmet Cheese Selection", "description": "Curated selection of artisanal cheeses from around the world", "category": "Food"},
    
    # Clothing
    {"id": 19, "name": "Winter Jacket", "description": "Insulated waterproof jacket for cold weather with adjustable hood", "category": "Clothing"},
    {"id": 20, "name": "Running Shoes", "description": "Lightweight athletic shoes with cushioned soles for runners", "category": "Clothing"},
    {"id": 21, "name": "Cotton T-Shirt", "description": "Soft, breathable cotton t-shirt available in various colors", "category": "Clothing"},
    {"id": 22, "name": "Denim Jeans", "description": "Classic fit jeans made from premium denim with stretch comfort", "category": "Clothing"},
    
    # Home & Kitchen
    {"id": 23, "name": "Coffee Maker", "description": "Programmable coffee machine with built-in grinder for fresh coffee", "category": "Home & Kitchen"},
    {"id": 24, "name": "Non-stick Cookware Set", "description": "Complete set of pots and pans with durable non-stick coating", "category": "Home & Kitchen"},
    {"id": 25, "name": "Smart Thermostat", "description": "Wi-Fi enabled thermostat that learns your schedule to save energy", "category": "Home & Kitchen"},
    {"id": 26, "name": "Air Purifier", "description": "HEPA filter air purifier that removes allergens and pollutants", "category": "Home & Kitchen"}
]

# Compute embeddings on demand
product_embeddings = None

def get_product_embeddings():
    global product_embeddings
    if product_embeddings is None:
        model_instance = get_model()
        if model_instance is None:
            return None
        
        # Prepare product texts
        product_texts = [f"{p['name']} {p['description']}" for p in products]
        
        # Encode products
        try:
            product_embeddings = model_instance.encode(product_texts, convert_to_tensor=True)
            return product_embeddings
        except Exception as e:
            print(f"Error encoding products: {e}")
            return None
    return product_embeddings

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with search functionality."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/status")
async def status():
    """Check if the model is loaded and ready"""
    model_loaded = get_model() is not None
    embeddings_loaded = get_product_embeddings() is not None
    return {"model_loaded": model_loaded, "embeddings_loaded": embeddings_loaded}

@app.post("/search")
async def search(query: str = Form(...)):
    """
    Search for products using semantic similarity with sentence transformers.
    
    Args:
        query: The search query from the user
        
    Returns:
        A list of relevant products sorted by similarity score
    """
    # Get model
    model_instance = get_model()
    if model_instance is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Model is still loading or failed to load. Please try again later."}
        )
    
    # Get product embeddings
    embeddings = get_product_embeddings()
    if embeddings is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Product embeddings are still being computed. Please try again later."}
        )
    
    try:
        # Encode the query
        query_embedding = model_instance.encode(query, convert_to_tensor=True)
        
        # Calculate cosine similarity between query and all products
        cos_scores = util.cos_sim(query_embedding, embeddings)[0]
        
        # Get top matches
        top_results = []
        for idx in torch.argsort(cos_scores, descending=True):
            idx = idx.item()
            score = cos_scores[idx].item()
            if score > 0.1:  # Threshold for relevance
                product = products[idx].copy()
                product["score"] = round(score * 100, 2)  # Convert to percentage for display
                top_results.append(product)
        
        return {"results": top_results}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred during search: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
