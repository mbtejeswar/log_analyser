# prompt_engine.py

class PromptEngine:
    def _summarize_history(self, chat_history: list[dict]) -> str:
        """Creates a concise summary of the conversation."""
        if not chat_history:
            return "No previous conversation history."
        
        summary = "Key points from the conversation so far:\n"
        for turn in chat_history[-4:]: # Summarize last 4 turns
            role = turn.get('role', 'Unknown')
            content = turn.get('content', '')
            summary += f"- The {role} mentioned: '{content[:80]}...'\n"
        return summary

    def build_prompt(self, user_query: str, chat_history: list[dict], error_log: str, code_snippets: list[str]) -> str:
        """
        Dynamically constructs a prompt with all available context.
        """
        print("⚙️ Building dynamic LLM prompt...")

        conversation_summary = self._summarize_history(chat_history)
        code_context = "\n".join(code_snippets) if code_snippets else "No specific code snippets were found to be relevant."

        # A single, powerful prompt template that handles all cases
        prompt = f"""
You are an expert AI Root Cause Analysis assistant. Your goal is to provide a clear, accurate, and helpful analysis based on all available information.

--- CONVERSATION SUMMARY ---
{conversation_summary}

--- APPLICATION LOGS ---
{error_log}

--- RELEVANT CODE CONTEXT ---
Based on the query, logs, and history, the following code may be relevant:
{code_context}

--- LATEST USER QUERY ---
"{user_query}"

--- YOUR TASK ---
Based on ALL the context above (logs, code, and conversation history), provide a comprehensive response. Your response must include two parts in valid JSON format:
1.  A "conversational_analysis" key: A clear, conversational explanation answering the user's query. Reference the code, logs, and history where appropriate.
2.  An "structured_rca" key: A JSON object containing a detailed root cause analysis. If the user's query isn't about RCA, this can be an empty object. The RCA object should contain:
    - "root_cause": A brief statement of the most likely root cause.
    - "confidence_score": A float from 0.0 to 1.0.
    - "recommended_action": A specific, actionable recommendation.

Example Response Format:
{{
  "conversational_analysis": "It looks like the `NullPointerException` is occurring in the `UserService` because...",
  "structured_rca": {{
    "root_cause": "The 'user' object is not checked for null before being used.",
    "confidence_score": 0.85,
    "recommended_action": "Add a null check in `UserService.java` before line 42: `if (user != null) {{ ... }}`."
  }}
}}
"""
        return prompt
