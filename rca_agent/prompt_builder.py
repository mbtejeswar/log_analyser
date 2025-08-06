class EnhancedPromptBuilder:
    def __init__(self):
        self.prompt_templates = {
            'specific_class': self.build_class_specific_prompt,
            'error_analysis': self.build_error_analysis_prompt,
            'flow_understanding': self.build_flow_prompt,
            'followup': self.build_followup_prompt,
            'general': self.build_general_prompt
        }
    
    def build_enhanced_prompt(self, context: Dict) -> str:
        """Build context-aware prompt based on query type and available information."""
        
        query_type = context['query_metadata']['search_strategy']
        is_followup = context['is_followup']
        
        # Select appropriate prompt builder
        if is_followup:
            prompt_builder = self.prompt_templates['followup']
        else:
            prompt_builder = self.prompt_templates.get(query_type, self.prompt_templates['general'])
        
        return prompt_builder(context)
    
    def build_error_analysis_prompt(self, context: Dict) -> str:
        """Build prompt for error analysis queries."""
        
        primary_code = '\n'.join(context['search_results']['primary_results'][:3])
        supporting_code = '\n'.join(context['search_results']['supporting_results'][:2])
        jira_logs = context.get('jira_logs', [])
        
        log_section = ""
        if jira_logs:
            log_section = f"""
--- RELEVANT JIRA LOGS ---
{chr(10).join([f"[{log.get('timestamp', 'N/A')}] {log.get('level', 'INFO')}: {log.get('message', '')}" for log in jira_logs[:5]])}
"""

        return f"""
You are an expert Java developer and system architect analyzing a production issue.

{log_section}

--- PRIMARY CODE CONTEXT ---
{primary_code}

--- SUPPORTING CODE CONTEXT ---
{supporting_code}

--- CONVERSATION THEMES ---
Previous discussion has covered: {', '.join(context.get('conversation_themes', []))}

--- USER QUERY ---
{context.get('current_query', '')}

--- ANALYSIS REQUEST ---
Based on the logs, code context, and conversation history:
1. Identify the root cause of the issue
2. Explain how the code relates to the logs/errors
3. Suggest specific fixes with code examples if possible
4. Highlight any patterns or recurring issues
5. Reference the relevant code sections and log entries

Provide a comprehensive but concise analysis focusing on actionable insights.
"""
    
    def build_followup_prompt(self, context: Dict) -> str:
        """Build prompt for follow-up questions."""
        
        recent_history = context['conversation_history'][-4:]  # Last 2 exchanges
        current_code = '\n'.join(context['search_results']['primary_results'][:2])
        
        history_text = '\n'.join([
            f"{'User' if msg.get('role') == 'user' else 'Assistant'}: {msg.get('content', '')}"
            for msg in recent_history
        ])
        
        return f"""
You are continuing a technical conversation about a Java application issue.

--- RECENT CONVERSATION ---
{history_text}

--- RELEVANT CODE CONTEXT ---
{current_code}

--- CURRENT FOLLOW-UP QUESTION ---
{context.get('current_query', '')}

--- RESPONSE GUIDELINES ---
1. Build upon the previous conversation context
2. Reference earlier points when relevant
3. Use the code context to provide specific answers
4. If the question asks about something new, incorporate it with the ongoing discussion
5. Keep responses focused and technically accurate

Respond as if you're an experienced developer who has been following this conversation from the start.
"""
