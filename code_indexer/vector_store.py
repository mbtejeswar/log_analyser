import pinecone
from google.cloud import aiplatform
from config import (
    PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME,
    GCP_PROJECT_ID, GCP_REGION, VERTEX_EMBEDDING_ENDPOINT
)

# Initialize clients
aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pinecone.Index(PINECONE_INDEX_NAME)

def get_embeddings_from_vertex(texts: list[str]) -> list[list[float]]:
    """Sends a batch of text to Vertex AI and returns embeddings."""
    endpoint = aiplatform.Endpoint(VERTEX_EMBEDDING_ENDPOINT)
    response = endpoint.predict(instances=[{"content": text} for text in texts])
    return [embedding.values for embedding in response.predictions]

def upsert_to_pinecone(chunks: list[dict]):
    """Generates embeddings and upserts chunks into Pinecone in batches."""
    if not chunks:
        return

    batch_size = 50  # Optimal batch size for Vertex AI
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        code_snippets = [chunk['code'] for chunk in batch_chunks]
        
        embeddings = get_embeddings_from_vertex(code_snippets)
        
        vectors_to_upsert = []
        for chunk, embedding in zip(batch_chunks, embeddings):
            vectors_to_upsert.append({
                "id": chunk["id"],
                "values": embedding,
                "metadata": chunk["metadata"]
            })
        
        index.upsert(vectors=vectors_to_upsert)
        print(f"Upserted {len(vectors_to_upsert)} vectors to Pinecone.")

