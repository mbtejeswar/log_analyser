import os

# --- ChromaDB Settings ---
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "../code_indexer/chroma_db_storage")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "java_code_analysis")

# --- Stork LLM Gateway Settings ---
STORK_API_URL = os.getenv("STORK_API_URL", "http://stork.internal.yourcompany.com/api/v1/generate")
STORK_API_KEY = os.getenv("STORK_API_KEY")
