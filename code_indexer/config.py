import os

# --- Project and Path Settings ---
# The absolute path to the Java Spring Boot project you want to monitor.
PROJECT_PATH = os.getenv("PROJECT_PATH", "/path/to/your/java-project")

# --- Pinecone Vector Database Settings ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "java-code-analysis")

# --- Google Cloud and Vertex AI Settings ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_REGION = os.getenv("GCP_REGION", "us-central1")
# The full resource name of the Vertex AI embedding model endpoint.
VERTEX_EMBEDDING_ENDPOINT = (
    f"projects/{GCP_PROJECT_ID}/locations/{GCP_REGION}/"
    "publishers/google/models/textembedding-gecko@003"
)
