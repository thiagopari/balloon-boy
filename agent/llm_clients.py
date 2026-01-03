"""
LLM Client interfaces for Ollama (Gemma 2 9B), Claude API, and OpenAI API
"""
import ollama
import anthropic
from openai import OpenAI
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass

@dataclass
class Message:
    """Standard message format"""
    role: str  # "user", "assistant", "system"
    content: str

class OllamaClient:
    """
    Client for local Gemma 2 9B via Ollama
    Fast, free, private - use for 80% of queries
    """
    
    def __init__(self, model: str = "gemma2:9b-instruct-q4_K_M", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        self.client = ollama.Client(host=host)
        
    def generate(
        self, 
        messages: List[Message], 
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Generate response from Gemma 2 9B"""
        # Convert to Ollama format
        ollama_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            if stream:
                return self._generate_stream(ollama_messages, temperature)
            else:
                response = self.client.chat(
                    model=self.model,
                    messages=ollama_messages,
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                )
                return response['message']['content']
                
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")
    
    def _generate_stream(self, messages: List[Dict], temperature: float) -> Generator:
        """Stream response token by token"""
        stream = self.client.chat(
            model=self.model,
            messages=messages,
            stream=True,
            options={"temperature": temperature}
        )
        
        for chunk in stream:
            if 'message' in chunk:
                yield chunk['message']['content']
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            models = self.client.list()
            return any(self.model in m['name'] for m in models['models'])
        except:
            return False


class OpenAIClient:
    """
    Client for OpenAI API (GPT-4, GPT-3.5, etc.)
    Uses your existing ChatGPT credits
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Args:
            api_key: OpenAI API key
            model: Model to use. Options:
                - "gpt-4o-mini" (cheap, fast, good quality)
                - "gpt-4o" (expensive, best quality)
                - "gpt-3.5-turbo" (cheapest, fast)
        """
        self.model = model
        self.client = OpenAI(api_key=api_key)
        
    def generate(
        self,
        messages: List[Message],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Generate response from OpenAI"""
        # Convert to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            if stream:
                return self._generate_stream(openai_messages, max_tokens, temperature)
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
                
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def _generate_stream(
        self, 
        messages: List[Dict], 
        max_tokens: int, 
        temperature: float
    ) -> Generator:
        """Stream response token by token"""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def is_available(self) -> bool:
        """Check if API key is valid"""
        try:
            self.client.models.list()
            return True
        except:
            return False


class ClaudeClient:
    """
    Client for Claude Sonnet 4.5 API
    Powerful reasoning, use for complex 20% of queries
    """
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def generate(
        self,
        messages: List[Message],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """Generate response from Claude"""
        # Convert to Claude format (exclude system messages)
        claude_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role != "system"
        ]
        
        # Extract system message if present
        if not system:
            system_msgs = [msg.content for msg in messages if msg.role == "system"]
            system = system_msgs[0] if system_msgs else None
        
        try:
            if stream:
                return self._generate_stream(claude_messages, max_tokens, temperature, system)
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system,
                    messages=claude_messages
                )
                return response.content[0].text
                
        except anthropic.APIError as e:
            raise RuntimeError(f"Claude API error: {e}")
    
    def _generate_stream(
        self, 
        messages: List[Dict], 
        max_tokens: int, 
        temperature: float,
        system: Optional[str]
    ) -> Generator:
        """Stream response token by token"""
        with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def is_available(self) -> bool:
        """Check if API key is valid"""
        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except:
            return False


class HybridLLM:
    """
    Unified interface that routes between local and API models
    Supports: Ollama (Gemma), OpenAI (GPT), Claude
    """
    
    def __init__(
        self, 
        local_client,  # OllamaClient or None
        api_client,    # OpenAIClient or ClaudeClient
        router,
        api_name: str = "openai"  # "openai" or "claude"
    ):
        self.local = local_client
        self.api = api_client
        self.router = router
        self.api_name = api_name
        
        # Track usage stats
        self.stats = {
            "local_calls": 0,
            "api_calls": 0,
            "total_tokens": {"local": 0, "api": 0}
        }
    
    def generate(
        self,
        messages: List[Message],
        force_model: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> tuple[str, str]:
        """
        Generate response using optimal model
        
        Args:
            messages: Conversation history
            force_model: Override routing ("local" or "api")
            stream: Stream response
            **kwargs: Additional generation parameters
            
        Returns:
            (response_text, model_used)
        """
        # Get user's latest message for routing
        user_message = next(
            (msg.content for msg in reversed(messages) if msg.role == "user"),
            ""
        )
        
        # Decide which model to use
        if force_model:
            model_choice = force_model
            routing_info = f"Forced to use {force_model}"
        else:
            # Only route to local if it's available
            if self.local and self.local.is_available():
                decision = self.router.route(user_message, messages)
                model_choice = "local" if decision.model.value == "local" else "api"
                routing_info = decision.reasoning
            else:
                # No local model, always use API
                model_choice = "api"
                routing_info = "Local model not available, using API"
        
        # Generate with selected model
        try:
            if model_choice == "local" and self.local:
                response = self.local.generate(messages, stream=stream, **kwargs)
                self.stats["local_calls"] += 1
                return response, "gemma-2-9b (local)"
            else:
                response = self.api.generate(messages, stream=stream, **kwargs)
                self.stats["api_calls"] += 1
                model_name = f"{self.api_name}-{self.api.model}"
                return response, model_name
                
        except Exception as e:
            # Fallback
            print(f"⚠️  Primary model failed: {e}")
            
            if model_choice == "local" and self.api:
                print(f"   Falling back to {self.api_name}")
                response = self.api.generate(messages, stream=stream, **kwargs)
                return response, f"{self.api_name} (fallback)"
            else:
                raise RuntimeError(f"All models failed: {e}")
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        total_calls = self.stats["local_calls"] + self.stats["api_calls"]
        if total_calls == 0:
            return {"message": "No calls made yet"}
        
        local_pct = (self.stats["local_calls"] / total_calls) * 100
        api_pct = (self.stats["api_calls"] / total_calls) * 100
        
        return {
            "total_calls": total_calls,
            "local_calls": self.stats["local_calls"],
            "api_calls": self.stats["api_calls"],
            "local_percentage": f"{local_pct:.1f}%",
            "api_percentage": f"{api_pct:.1f}%",
            "api_provider": self.api_name
        }
