import chromadb
from abc.langchain.embeddings import StorkEmbeddings
from config import (
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_NAME,
)

# --- Initialize ChromaDB Client ---
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

# --- Initialize Stork Embeddings ---
embedModel = StorkEmbeddings(
    provider='GCP_VERTEX_AI', 
    provider_id='textembedding-gecko@001'
)

def get_embeddings_from_stork(texts: list[str]) -> list[list[float]]:
    """Generates embeddings using Stork's LangChain integration."""
    try:
        # LangChain's embed_documents method handles batch processing
        embeddings = embedModel.embed_documents(texts)
        return embeddings
    except Exception as e:
        print(f"Error calling Stork embeddings: {e}")
        return []

def upsert_to_chromadb(chunks: list[dict]):
    """Generates embeddings via Stork and upserts chunks into ChromaDB in batches."""
    if not chunks:
        return

    batch_size = 50  # Process chunks in batches for efficiency
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        
        ids = [chunk['id'] for chunk in batch_chunks]
        documents = [chunk['code'] for chunk in batch_chunks]
        metadatas = [chunk['metadata'] for chunk in batch_chunks]
        
        # Generate embeddings using Stork
        embeddings = get_embeddings_from_stork(documents)
        
        if not embeddings:
            print("Skipping batch due to embedding generation failure.")
            continue
        
        # Upsert the batch to ChromaDB
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Upserted {len(batch_chunks)} vectors to ChromaDB via Stork.")
