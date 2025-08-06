import re
from enum import Enum
from typing import Dict, List, Tuple

class QueryType(Enum):
    SPECIFIC_CLASS = "specific_class"
    SPECIFIC_METHOD = "specific_method"
    ERROR_ANALYSIS = "error_analysis"
    CONCEPTUAL = "conceptual"
    LOG_ANALYSIS = "log_analysis"
    FLOW_UNDERSTANDING = "flow_understanding"

class EnhancedQueryProcessor:
    def __init__(self):
        self.patterns = {
            QueryType.SPECIFIC_CLASS: [
                r'\b[A-Z][a-zA-Z0-9_]*Service\b',
                r'\b[A-Z][a-zA-Z0-9_]*Controller\b',
                r'\b[A-Z][a-zA-Z0-9_]*Repository\b',
                r'\bclass\s+[A-Z][a-zA-Z0-9_]*\b'
            ],
            QueryType.SPECIFIC_METHOD: [
                r'\b[a-z][a-zA-Z0-9_]*\(\)',
                r'\bmethod\s+[a-z][a-zA-Z0-9_]*\b',
                r'\bfunction\s+[a-z][a-zA-Z0-9_]*\b'
            ],
            QueryType.ERROR_ANALYSIS: [
                r'\b(?:exception|error|null|timeout|connection|failed)\b',
                r'\b(?:stack trace|stacktrace)\b',
                r'\b(?:why.*fail|what.*wrong|cause.*error)\b'
            ],
            QueryType.LOG_ANALYSIS: [
                r'\b(?:log|logging|trace|debug)\b',
                r'\b(?:show.*log|find.*log|log.*show)\b'
            ],
            QueryType.FLOW_UNDERSTANDING: [
                r'\b(?:how.*work|what.*do|explain.*flow)\b',
                r'\b(?:process|workflow|sequence)\b'
            ]
        }
    
    def classify_query(self, query: str) -> Tuple[QueryType, float, Dict]:
        """Classify user query and extract key entities."""
        query_lower = query.lower()
        
        # Extract entities
        entities = {
            'class_names': re.findall(r'\b[A-Z][a-zA-Z0-9_]*(?:Service|Controller|Repository)\b', query),
            'method_names': re.findall(r'\b[a-z][a-zA-Z0-9_]*\(\)', query),
            'error_terms': re.findall(r'\b(?:exception|error|null|timeout|connection|failed)\b', query_lower),
            'technical_terms': re.findall(r'\b(?:database|api|rest|http|sql|json)\b', query_lower)
        }
        
        # Score each query type
        scores = {}
        for query_type, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            scores[query_type] = score
        
        # Get highest scoring type
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type] / (len(query.split()) + 1)  # Normalize
        
        return best_type, confidence, entities
