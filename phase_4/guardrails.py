import re

class Guardrails:
    KNOWN_SCHEMES = [
        "axis liquid",
        "axis elss",
        "axis tax saver",
        "axis flexi cap",
        "axis large cap",
        "axis midcap",
        "axis small cap",
        "axis focused"
    ]
    
    ADVICE_KEYWORDS = [
        "should i invest",
        "is it good to buy",
        "suggest a fund",
        "best fund to invest",
        "which one is better",
        "is it risky",
        "give me advice"
    ]
    
    @staticmethod
    def is_asking_advice(query: str) -> bool:
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.ADVICE_KEYWORDS) if hasattr(self, 'ADVICE_KEYWORDS') else any(keyword in query_lower for keyword in Guardrails.ADVICE_KEYWORDS)

    @staticmethod
    def is_unknown_scheme(query: str) -> bool:
        query_lower = query.lower()
        # If the query contains "fund" or "scheme", check if any known scheme name is present
        if "fund" in query_lower or "scheme" in query_lower:
            # Check if any known scheme is mentioned
            mentioned_known = any(scheme in query_lower for scheme in Guardrails.KNOWN_SCHEMES)
            
            # If "axis" is mentioned but not a known one, it might be another axis fund
            if not mentioned_known:
                # Common axis funds not in our list
                return True
        return False

    @staticmethod
    def get_guardrail_response(query: str, context_found: bool) -> str:
        query_lower = query.lower()
        
        # 1. Advice Check
        if any(keyword in query_lower for keyword in Guardrails.ADVICE_KEYWORDS):
            return "I am only here to provide information regarding mutual funds."
            
        # 2. Unknown Scheme Check
        # Check if user mentions a specific fund brand other than Axis, or Axis funds not in our list
        if ("fund" in query_lower or "scheme" in query_lower or "invest in" in query_lower):
            has_known = any(scheme in query_lower for scheme in Guardrails.KNOWN_SCHEMES)
            if not has_known and ("axis" in query_lower or "hdfc" in query_lower or "sbi" in query_lower or "icici" in query_lower or "quant" in query_lower):
                return "I dont have information regarding the scheme."
        
        # 3. Context Check (handled after RAG)
        if not context_found:
            return "I don't have an answer to the question you are asking."
            
        return None
