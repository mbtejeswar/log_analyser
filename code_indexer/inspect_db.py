import os
import chromadb
import json

# --- Configuration ---
# This must match the path where your code_indexer service stores the database.
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./code_indexer/chroma_db_storage")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "java_code_analysis")

def inspect_collection():
    """Connects to the ChromaDB and prints its contents."""
    
    print(f"--- Inspecting ChromaDB at: {CHROMA_DB_PATH} ---")
    
    # Check if the database path exists
    if not os.path.exists(CHROMA_DB_PATH):
        print(f"Error: Database path not found. Please ensure the code_indexer has run at least once.")
        return

    # Connect to the persistent database
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    try:
        # Get the specific collection
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)
        
        # Get the total count of items
        count = collection.count()
        print(f"Collection '{CHROMA_COLLECTION_NAME}' contains {count} items.")
        
        if count == 0:
            return

        # Retrieve all items from the collection
        # Note: For very large collections, you might want to use a limit.
        results = collection.get() # You can add a limit, e.g., get(limit=10)
        
        # Pretty-print the first few results
        print("\n--- Sample of Stored Chunks ---")
        for i in range(min(5, count)): # Print up to 5 samples
            print(f"\n----- Item {i+1} -----")
            print(f"ID: {results['ids'][i]}")
            print("METADATA:")
            print(json.dumps(results['metadatas'][i], indent=2))
            print("DOCUMENT (Code Chunk):")
            print(results['documents'][i])
            # We don't print the embedding vector as it's just a long list of numbers.

    except Exception as e:
        print(f"An error occurred: {e}")
        print("This might mean the collection does not exist or the database is empty.")


if __name__ == "__main__":
    inspect_collection()
