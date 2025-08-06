class ContextAwareConversationManager:
    def __init__(self):
        self.conversation_memory = {}
        self.code_retrieval = EnhancedCodeRetrieval()
    
    def build_enhanced_context(self, query: str, session_id: str, 
                             jira_logs: List[Dict] = None) -> Dict:
        """Build comprehensive context for the query."""
        
        # Get conversation history
        conversation_history = self.get_conversation_history(session_id)
        
        # Enhanced search with all context
        search_results = self.code_retrieval.enhanced_search(
            query=query,
            conversation_history=conversation_history,
            jira_logs=jira_logs
        )
        
        # Build conversation themes
        themes = self.extract_conversation_themes(conversation_history)
        
        # Determine if this is a follow-up question
        is_followup = self.is_followup_question(query, conversation_history)
        
        return {
            'search_results': search_results,
            'conversation_history': conversation_history[-6:],  # Last 3 exchanges
            'conversation_themes': themes,
            'is_followup': is_followup,
            'jira_logs': jira_logs or [],
            'query_metadata': {
                'query_type': search_results.get('search_strategy', 'unknown'),
                'confidence': search_results.get('confidence', 0),
                'search_strategy': search_results.get('search_strategy')
            }
        }
    
    def extract_conversation_themes(self, history: List[Dict]) -> List[str]:
        """Extract recurring themes from conversation."""
        themes = []
        all_content = ' '.join([msg.get('content', '') for msg in history])
        
        # Extract common technical terms
        tech_patterns = [
            r'\b([A-Z][a-zA-Z0-9_]*Service)\b',
            r'\b([A-Z][a-zA-Z0-9_]*Controller)\b',
            r'\b(database|api|rest|http|json|authentication)\b',
            r'\b([a-z][a-zA-Z0-9_]*Exception)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, all_content, re.IGNORECASE)
            themes.extend(matches)
        
        # Return unique themes
        return list(set(themes))
