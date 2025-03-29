# Semantic Product Search with Sentence Transformers

This project demonstrates a real-world implementation of semantic search using Sentence Transformers and allows users to search for products using natural language queries.

## Demo
<video src="https://github.com/user-attachments/assets/bcd0390f-669c-45f4-b5fb-c55bd09125a2"></video>

## What is Semantic Search?

Unlike traditional keyword-based search that only finds exact matches, semantic search understands the meaning behind words. This means it can find relevant results even when the exact keywords aren't present in the product descriptions.

## How It Works?

### 1. Sentence Transformers

Sentence Transformers is a Python library that provides easy-to-use methods to compute dense vector representations (embeddings) for sentences, paragraphs, and images. These embeddings capture semantic meaning, making them perfect for tasks like semantic search.

### 2. The Embedding Process

When our application starts:

1. We load a pre-trained model (`all-MiniLM-L6-v2`) from the Sentence Transformers library
2. This model was trained on massive text datasets to understand semantic relationships
3. We encode our product catalog (names and descriptions) into vector embeddings
4. These embeddings are numerical representations that capture the meaning of each product

### 3. Search Process

When a user searches:

1. **Query Encoding**: The user's search query is converted into a vector embedding using the same model
2. **Similarity Calculation**: We calculate the cosine similarity between the query vector and all product vectors
   - Cosine similarity measures the angle between vectors (closer to 1 = more similar)
   - This is much more powerful than simple keyword matching
3. **Ranking**: Products are ranked by their similarity score
4. **Filtering**: Only products above a certain similarity threshold are returned

### 4. Why This Works So Well

- **Understanding Concepts**: The model understands conceptual relationships between words
- **Handling Synonyms**: It recognizes that different words can mean the same thing
- **Context Awareness**: It considers the entire query context, not just individual words

## Technical Details

### Backend (FastAPI)

The backend uses FastAPI to create a simple API with two endpoints:
- `GET /`: Serves the main HTML page
- `POST /search`: Accepts search queries and returns relevant products

Key components:
- `SentenceTransformer`: The model that converts text to embeddings
- `util.cos_sim()`: Calculates cosine similarity between vectors
- Pre-computed embeddings: Product embeddings are calculated once at startup for efficiency

### Frontend (HTML/CSS/JS)

The frontend is a simple single-page application that:
1. Provides a search input for users
2. Sends search queries to the backend via AJAX
3. Displays search results with relevance scores
4. Shows a loading indicator during searches

## Limitations and Potential Improvements

- **Model Size**: The current model is small and fast but less accurate than larger models
- **Product Catalog**: This demo uses a small hardcoded product list; a real application would use a database
- **Performance**: For large catalogs, vector databases like FAISS or Pinecone would be more efficient
- **Multilingual Support**: The current model works best in English; other models support multiple languages

## Learn More

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Understanding Semantic Search](https://huggingface.co/blog/semantic-search)

## How to Run the Project

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```
   uvicorn app.main:app --reload
   ```

3. Open your browser and navigate to `http://localhost:8000`
