# enhanced_retrieval.py

import re
import chromadb
# from your_embedding_module import embedModel # Your embedding model
# Note: For this example, we'll simulate the embedding model and DB client.

class EnhancedRetriever:
    def __init__(self):
        # self.client = chromadb.PersistentClient(path="/path/to/your/db")
        # self.collection = self.client.get_collection("java_code_analysis")
        # self.embedModel = embedModel
        print(" retriever initialized.")

    def _query_collection(self, query_text: str, top_k: int = 5) -> list:
        """Simulates querying the ChromaDB collection."""
        print(f"  -> Searching for: '{query_text[:50]}...'")
        # In a real scenario:
        # query_embedding = self.embedModel.embed_query(query_text)
        # results = self.collection.query(
        #     query_embeddings=[query_embedding],
        #     n_results=top_k
        # )
        # return results['documents'][0] if results['documents'] else []
        return [f"// Mock code snippet found for query: {query_text}\npublic void exampleMethod() {{}}"] # Placeholder

    def _extract_log_keywords(self, error_log: str) -> list:
        """Extracts key technical terms from error logs for keyword search."""
        keywords = re.findall(r'([a-zA-Z0-9_]*Exception|FATAL|ERROR|timeout|[A-Z][a-zA-Z]+Service)', error_log)
        return list(set(keywords))

    def _extract_history_themes(self, chat_history: list[dict]) -> list:
        """Extracts key nouns and technical terms from conversation history."""
        full_text = " ".join([turn.get('content', '') for turn in chat_history])
        themes = re.findall(r'([A-Z][a-zA-Z]+Service|database|API|authentication)', full_text)
        return list(set(themes))

    def find_relevant_code(self, user_query: str, error_log: str, chat_history: list[dict], top_k: int = 10) -> dict:
        """
        Performs multiple targeted searches and combines results for maximum relevance.
        """
        print("🔎 Performing multi-query hybrid search...")
        all_snippets = {}

        # 1. Semantic search on the user's direct query
        user_query_results = self._query_collection(user_query, top_k=3)
        for snippet in user_query_results:
            all_snippets[snippet] = all_snippets.get(snippet, 0) + 1.5 # Higher weight for direct query

        # 2. Semantic search on the raw error log
        log_query_results = self._query_collection(error_log, top_k=3)
        for snippet in log_query_results:
            all_snippets[snippet] = all_snippets.get(snippet, 0) + 1.0

        # 3. Keyword-based search for technical terms from logs
        log_keywords = self._extract_log_keywords(error_log)
        if log_keywords:
            keyword_query = "Code related to " + " ".join(log_keywords)
            keyword_results = self._query_collection(keyword_query, top_k=3)
            for snippet in keyword_results:
                all_snippets[snippet] = all_snippets.get(snippet, 0) + 1.2 # High weight for keywords

        # 4. Contextual search based on conversation themes
        history_themes = self._extract_history_themes(chat_history)
        if history_themes:
            theme_query = "Follow-up on " + " ".join(history_themes)
            theme_results = self._query_collection(theme_query, top_k=2)
            for snippet in theme_results:
                all_snippets[snippet] = all_snippets.get(snippet, 0) + 0.8 # Lower weight for general themes

        # 5. Rank results by frequency and weight
        ranked_snippets = sorted(all_snippets.keys(), key=lambda k: all_snippets[k], reverse=True)

        return {
            "ranked_code_snippets": ranked_snippets[:top_k],
            "log_keywords": log_keywords,
            "history_themes": history_themes
        }
