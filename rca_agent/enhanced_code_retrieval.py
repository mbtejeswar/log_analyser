class EnhancedCodeRetrieval:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.code_collection = self.chroma_client.get_collection("java_code_analysis")
        self.log_collection = self.chroma_client.get_or_create_collection("application_logs")
        self.embedModel = StorkEmbeddings(provider='GCP_VERTEX_AI', provider_id='gemini-embedding-001')
        self.query_processor = EnhancedQueryProcessor()
    
    def enhanced_search(self, query: str, conversation_history: List[Dict] = None, 
                       jira_logs: List[Dict] = None, top_k: int = 8) -> Dict:
        """Enhanced search combining multiple strategies."""
        
        # Step 1: Classify the query
        query_type, confidence, entities = self.query_processor.classify_query(query)
        
        print(f"🎯 Query classified as: {query_type.value} (confidence: {confidence:.2f})")
        print(f"📝 Entities found: {entities}")
        
        # Step 2: Multi-strategy search based on query type
        search_results = self.execute_multi_strategy_search(query, query_type, entities, top_k)
        
        # Step 3: Enhance with conversation context
        if conversation_history:
            context_enhanced = self.enhance_with_conversation_context(
                search_results, conversation_history, query
            )
            search_results.update(context_enhanced)
        
        # Step 4: Enhance with log correlation
        if jira_logs:
            log_enhanced = self.correlate_with_logs(search_results, jira_logs, query)
            search_results.update(log_enhanced)
        
        return search_results
    
    def execute_multi_strategy_search(self, query: str, query_type: QueryType, 
                                    entities: Dict, top_k: int) -> Dict:
        """Execute different search strategies based on query type."""
        
        results = {
            'primary_results': [],
            'supporting_results': [],
            'search_strategy': query_type.value,
            'confidence': 0
        }
        
        if query_type == QueryType.SPECIFIC_CLASS:
            results = self.search_specific_classes(entities['class_names'], query, top_k)
        
        elif query_type == QueryType.SPECIFIC_METHOD:
            results = self.search_specific_methods(entities['method_names'], query, top_k)
        
        elif query_type == QueryType.ERROR_ANALYSIS:
            results = self.search_error_related_code(query, entities['error_terms'], top_k)
        
        elif query_type == QueryType.FLOW_UNDERSTANDING:
            results = self.search_workflow_code(query, entities, top_k)
        
        else:  # CONCEPTUAL or others
            results = self.search_conceptual(query, top_k)
        
        return results
    
    def search_specific_classes(self, class_names: List[str], original_query: str, top_k: int) -> Dict:
        """Targeted search for specific classes."""
        primary_results = []
        
        for class_name in class_names:
            # Exact metadata search
            exact_matches = self.code_collection.get(
                where={
                    "$or": [
                        {"class_name": {"$contains": class_name}},
                        {"file_path": {"$contains": class_name}}
                    ]
                },
                limit=top_k // len(class_names) if class_names else top_k
            )
            
            if exact_matches['documents']:
                primary_results.extend(exact_matches['documents'])
        
        # If no exact matches, fall back to semantic search
        if not primary_results:
            query_embedding = self.embedModel.embed_query(original_query)
            semantic_results = self.code_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            primary_results = semantic_results['documents'][0] if semantic_results['documents'] else []
        
        return {
            'primary_results': primary_results[:top_k],
            'supporting_results': [],
            'search_strategy': 'specific_class_search',
            'confidence': 0.9 if primary_results else 0.1
        }
    
    def search_error_related_code(self, query: str, error_terms: List[str], top_k: int) -> Dict:
        """Search for code related to specific errors."""
        
        # Enhance query with error context
        enhanced_query = f"{query} exception handling error management try catch"
        
        # Semantic search
        query_embedding = self.embedModel.embed_query(enhanced_query)
        semantic_results = self.code_collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Filter for error-handling patterns
        error_handling_results = []
        if semantic_results['documents']:
            for doc in semantic_results['documents'][0]:
                if any(term in doc.lower() for term in ['try', 'catch', 'throw', 'exception', 'error', 'null']):
                    error_handling_results.append(doc)
        
        return {
            'primary_results': error_handling_results[:top_k//2],
            'supporting_results': semantic_results['documents'][0][top_k//2:top_k] if semantic_results['documents'] else [],
            'search_strategy': 'error_analysis_search',
            'confidence': 0.8 if error_handling_results else 0.3
        }
    
    def correlate_with_logs(self, search_results: Dict, jira_logs: List[Dict], query: str) -> Dict:
        """Enhance search results with log correlation."""
        
        # Extract relevant log entries
        relevant_logs = []
        for log in jira_logs:
            log_text = log.get('message', '') + ' ' + log.get('stackTrace', '')
            
            # Check if log mentions any classes from search results
            for code_chunk in search_results['primary_results']:
                # Extract class names from code chunks
                class_matches = re.findall(r'class\s+([A-Z][a-zA-Z0-9_]*)', code_chunk)
                method_matches = re.findall(r'public\s+\w+\s+([a-z][a-zA-Z0-9_]*)\(', code_chunk)
                
                if any(cls in log_text for cls in class_matches) or any(method in log_text for method in method_matches):
                    relevant_logs.append(log)
                    break
        
        return {
            'log_correlation': relevant_logs,
            'correlation_score': len(relevant_logs) / max(len(jira_logs), 1)
        }
