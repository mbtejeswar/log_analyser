# Enhanced main RCA function
def enhanced_perform_rca(query: str, session_id: str, jira_logs: List[Dict] = None) -> Dict:
    """Enhanced RCA with multi-layered context awareness."""
    
    print("🚀 Enhanced RCA Analysis Starting...")
    
    # Build comprehensive context
    context_manager = ContextAwareConversationManager()
    context = context_manager.build_enhanced_context(query, session_id, jira_logs)
    
    # Build intelligent prompt
    prompt_builder = EnhancedPromptBuilder()
    enhanced_prompt = prompt_builder.build_enhanced_prompt(context)
    
    # Add current query to context for prompt building
    context['current_query'] = query
    enhanced_prompt = prompt_builder.build_enhanced_prompt(context)
    
    # Call Stork with enhanced prompt
    analysis = call_stork_with_enhanced_prompt(enhanced_prompt)
    
    # Store in conversation history
    context_manager.add_to_conversation_history(session_id, query, analysis)
    
    return {
        'query': query,
        'analysis': analysis,
        'search_metadata': context['query_metadata'],
        'code_chunks_used': len(context['search_results']['primary_results']),
        'log_correlation': context['search_results'].get('log_correlation', []),
        'conversation_context_used': len(context['conversation_history']) > 0,
        'session_id': session_id
    }
