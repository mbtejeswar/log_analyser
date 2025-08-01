import chromadb
import requests
from abc.langchain.embeddings import StorkEmbeddings
from config import (
    CHROMA_DB_PATH, CHROMA_COLLECTION_NAME,
    STORK_API_URL, STORK_API_KEY
)

# Initialize clients
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)

# Initialize Stork Embeddings
embedModel = StorkEmbeddings(
    provider='GCP_VERTEX_AI', 
    provider_id='textembedding-gecko@001'
)

def get_embedding_for_error(text: str) -> list[float]:
    """Generates an embedding for the incoming error log using Stork."""
    try:
        # LangChain's embed_query method is for single text queries
        embedding = embedModel.embed_query(text)
        return embedding
    except Exception as e:
        print(f"Error generating embedding for error log: {e}")
        return []

def find_relevant_code(error_log: str, top_k: int = 5) -> list[str]:
    """Finds the most semantically similar code snippets from ChromaDB."""
    error_embedding = get_embedding_for_error(error_log)
    
    if not error_embedding:
        print("Failed to generate embedding for error log.")
        return []
    
    results = collection.query(
        query_embeddings=[error_embedding],
        n_results=top_k
    )
    return results['documents'][0] if results and results['documents'] else []

def get_rca_from_stork(error_log: str, code_context: list[str]) -> str:
    """Constructs a prompt and sends it to the Stork LLM gateway."""
    
    # Construct the detailed prompt
    prompt = f"""
    Analyze the following Java error log and the potentially relevant code snippets to determine the root cause.

    --- ERROR LOG ---
    {error_log}

    --- RELEVANT CODE CONTEXT ---
    {"".join(f"// Snippet {i+1}\\n{snippet}\\n" for i, snippet in enumerate(code_context))}

    --- ANALYSIS REQUEST ---
    Based on the provided context, please provide:
    1. A concise probable root cause of the error.
    2. A suggested fix or debugging step.
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {STORK_API_KEY}"
    }
    
    payload = {
        "model": "gemini-1.5-pro",
        "prompt": prompt
    }

    try:
        response = requests.post(STORK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("result", "No analysis returned from Stork.")
    except requests.exceptions.RequestException as e:
        print(f"Error calling Stork API: {e}")
        return "Failed to get analysis from Stork LLM Gateway."

def perform_root_cause_analysis(error_log: str) -> dict:
    """Orchestrates the end-to-end RCA process."""
    print("Finding relevant code context using Stork embeddings...")
    relevant_code = find_relevant_code(error_log)
    
    if not relevant_code:
        print("No relevant code context found. Relying on error log alone.")
    
    print("Getting analysis from Stork LLM Gateway...")
    analysis = get_rca_from_stork(error_log, relevant_code)
    
    return {
        "error_log": error_log,
        "analysis": analysis,
        "context_provided": relevant_code
    }
