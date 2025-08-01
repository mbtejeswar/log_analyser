import os

# --- Project and Path Settings ---
PROJECT_PATH = os.getenv("PROJECT_PATH", "/path/to/your/java-project")

# --- ChromaDB Settings ---
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db_storage")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "java_code_analysis")
