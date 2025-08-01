import os
from config import PROJECT_PATH
from parser import extract_method_chunks
from vector_store import upsert_to_chromadb

def crawl_and_index_project():
    """
    Crawls the entire project directory, finds all Java files,
    and indexes them in a single run.
    """
    print(f"--- Starting bulk indexing for project at: {PROJECT_PATH} ---")
    
    java_files_found = 0
    chunks_indexed = 0
    
    # os.walk recursively visits all directories and files from the root path
    for root, dirs, files in os.walk(PROJECT_PATH):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(root, file)
                java_files_found += 1
                
                print(f"Processing: {file_path}")
                
                # Use the existing parsing and upserting logic
                chunks = extract_method_chunks(file_path)
                
                if chunks:
                    upsert_to_chromadb(chunks)
                    chunks_indexed += len(chunks)

    print("\n--- Bulk Indexing Complete ---")
    print(f"Total Java files found: {java_files_found}")
    print(f"Total method chunks indexed: {chunks_indexed}")


if __name__ == "__main__":
    # Ensure the project path is valid before starting
    if not os.path.isdir(PROJECT_PATH):
        print(f"Error: The provided PROJECT_PATH is not a valid directory.")
        print(f"Path: {PROJECT_PATH}")
    else:
        crawl_and_index_project()
