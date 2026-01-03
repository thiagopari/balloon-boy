"""
Intelligent routing between local Gemma 2 9B and Claude API
"""
import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ModelChoice(Enum):
    """Which model to use"""
    LOCAL = "local"  # Gemma 2 9B via Ollama
    CLAUDE = "claude"  # Claude Sonnet 4.5 API

@dataclass
class RoutingDecision:
    """Result of routing decision"""
    model: ModelChoice
    complexity_score: float
    reasoning: str
    
class ModelRouter:
    """
    Decides which model to use based on query complexity
    
    Strategy:
    - Local (Gemma 9B): Simple queries, fast tasks, privacy-sensitive
    - Claude API: Complex reasoning, code generation, multi-step tasks
    """
    
    def __init__(self, complexity_threshold: float = 3.0):
        self.threshold = complexity_threshold
        
        # Pattern matching for fast routing
        self.simple_patterns = [
            r"^(what|when|where|who)\s+(is|was|are|were)",  # Simple wh-questions
            r"^(tell me|give me|show me)\s+\w+$",  # Simple commands
            r"^(hi|hello|hey|good morning|good evening)",  # Greetings
            r"weather",
            r"time",
            r"(set|add|create)\s+(reminder|alarm|calendar)",
        ]
        
        # Indicators of complex tasks
        self.complexity_indicators = {
            "multi_step": ["then", "after that", "next", "finally", "also", "and then"],
            "reasoning": ["why", "how", "explain", "analyze", "compare", "evaluate"],
            "code": ["write code", "function", "class", "implement", "debug", "refactor"],
            "creative": ["write", "create", "generate", "design", "compose", "draft"],
        }
        
    def route(self, user_message: str, conversation_history: list = None) -> RoutingDecision:
        """
        Determine which model should handle this message
        
        Args:
            user_message: The user's input
            conversation_history: Recent messages for context
            
        Returns:
            RoutingDecision with model choice and reasoning
        """
        # Fast path: simple pattern matching
        if self._is_simple_query(user_message):
            return RoutingDecision(
                model=ModelChoice.LOCAL,
                complexity_score=1.0,
                reasoning="Matches simple query pattern"
            )
        
        # Calculate complexity score
        complexity = self._calculate_complexity(user_message, conversation_history)
        
        # Make decision
        if complexity < self.threshold:
            model = ModelChoice.LOCAL
            reasoning = f"Low complexity ({complexity:.1f} < {self.threshold})"
        else:
            model = ModelChoice.CLAUDE
            reasoning = f"High complexity ({complexity:.1f} ≥ {self.threshold})"
            
        return RoutingDecision(
            model=model,
            complexity_score=complexity,
            reasoning=reasoning
        )
    
    def _is_simple_query(self, message: str) -> bool:
        """Fast pattern matching for common simple queries"""
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in self.simple_patterns)
    
    def _calculate_complexity(
        self, 
        message: str, 
        conversation_history: Optional[list] = None
    ) -> float:
        """
        Estimate query complexity on 0-10 scale
        
        Factors:
        - Length (longer = more complex)
        - Multi-step indicators
        - Reasoning requirements
        - Code generation
        - Creative writing
        - Conversation context
        """
        score = 0.0
        message_lower = message.lower()
        word_count = len(message.split())
        
        # 1. Length penalty (longer messages tend to be more complex)
        score += min(word_count / 50, 2.0)
        
        # 2. Multi-step indicators
        multi_step_count = sum(
            1 for word in self.complexity_indicators["multi_step"]
            if word in message_lower
        )
        score += min(multi_step_count * 2.0, 3.0)
        
        # 3. Reasoning indicators
        reasoning_count = sum(
            1 for word in self.complexity_indicators["reasoning"]
            if word in message_lower
        )
        score += min(reasoning_count * 1.5, 2.5)
        
        # 4. Code generation (always complex)
        if any(word in message_lower for word in self.complexity_indicators["code"]):
            score += 3.0
            
        # 5. Creative writing (moderately complex)
        if any(word in message_lower for word in self.complexity_indicators["creative"]):
            if word_count > 20:  # "Write a story..." vs "Write hi"
                score += 2.0
        
        # 6. Long conversation context adds complexity
        if conversation_history and len(conversation_history) > 5:
            score += 0.5
            
        # 7. Question about previous answers (needs context)
        if any(word in message_lower for word in ["you said", "you mentioned", "earlier", "before"]):
            score += 1.0
        
        return min(score, 10.0)
    
    def explain_decision(self, decision: RoutingDecision) -> str:
        """Human-readable explanation of routing decision"""
        if decision.model == ModelChoice.LOCAL:
            return (
                f"✓ Using Gemma 2 9B (local) - {decision.reasoning}\n"
                f"  Fast, private, no API costs"
            )
        else:
            return (
                f"⚡ Using Claude Sonnet 4.5 (API) - {decision.reasoning}\n"
                f"  Advanced reasoning, better quality for complex tasks"
            )


# Example usage and testing
if __name__ == "__main__":
    router = ModelRouter(complexity_threshold=3.0)
    
    test_queries = [
        "What time is it?",
        "When is my next meeting?",
        "Explain quantum computing and compare it to classical computing",
        "Write a Python function to implement a binary search tree",
        "Hi! How are you?",
        "Plan a 3-day trip to Paris, optimize for museums and food, budget $2000",
        "What's the weather today?",
        "Debug this code and then refactor it to use async/await patterns",
    ]
    
    print("🧠 Model Router Test\n")
    for query in test_queries:
        decision = router.route(query)
        print(f"Query: {query[:60]}...")
        print(f"{router.explain_decision(decision)}")
        print()
