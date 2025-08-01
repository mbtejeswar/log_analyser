import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import PROJECT_PATH
from parser import extract_method_chunks
from vector_store import upsert_to_chromadb

class CodeChangeHandler(FileSystemEventHandler):
    """Handles file system events for Java source files."""
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".java"):
            print(f"Change detected in: {event.src_path}")
            chunks = extract_method_chunks(event.src_path)
            if chunks:
                upsert_to_chromadb(chunks)

def main():
    print(f"Starting file watcher for directory: {PROJECT_PATH}")
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, PROJECT_PATH, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
