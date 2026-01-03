"""
Balloon Boy Agent: Main orchestrator with OpenAI/Claude support
"""
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agent.router import ModelRouter, ModelChoice
from agent.llm_clients import OllamaClient, ClaudeClient, OpenAIClient, HybridLLM, Message
from memory.system import MemorySystem
from config.settings import settings

@dataclass
class ConversationState:
    """Current state of the conversation"""
    messages: List[Message]
    user_profile_loaded: bool = False
    context_injected: bool = False

class BalloonBoyAgent:
    """
    Main AI agent for Balloon Boy
    
    Supports:
    - Local: Ollama (Gemma 2 9B) when on x86_64 with GPU
    - API: OpenAI (GPT) or Claude (your choice)
    """
    
    def __init__(self, api_provider: str = "openai"):
        """
        Args:
            api_provider: "openai" or "claude"
        """
        print("🎈 Initializing Balloon Boy Agent...")
        print(f"  🤖 API Provider: {api_provider.upper()}")
        
        # Initialize local LLM (may not be available on ARM64)
        print("  📡 Checking for local model (Ollama)...")
        try:
            self.ollama = OllamaClient(
                model=settings.model.local_model,
                host=settings.model.local_host
            )
            
            if self.ollama.is_available():
                print("    ✅ Gemma 2 9B available locally")
                local_available = True
            else:
                print("    ⚠️  Local model not available (will use API only)")
                self.ollama = None
                local_available = False
        except Exception as e:
            print(f"    ⚠️  Ollama not available: {e}")
            self.ollama = None
            local_available = False
        
        # Initialize API client based on provider
        print(f"  🌐 Connecting to {api_provider.upper()} API...")
        
        if api_provider == "openai":
            api_key = settings.model.openai_api_key
            if not api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found in environment. "
                    "Please set it in config/.env"
                )
            
            self.api_client = OpenAIClient(
                api_key=api_key,
                model=settings.model.openai_model
            )
            api_name = "openai"
            
        else:  # claude
            api_key = settings.model.anthropic_api_key
            if not api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found in environment. "
                    "Please set it in config/.env"
                )
            
            self.api_client = ClaudeClient(
                api_key=api_key,
                model=settings.model.claude_model
            )
            api_name = "claude"
        
        # Initialize router
        print("  🧠 Setting up model router...")
        self.router = ModelRouter(
            complexity_threshold=settings.model.complexity_threshold
        )
        
        # Create hybrid LLM
        self.llm = HybridLLM(
            self.ollama, 
            self.api_client, 
            self.router,
            api_name=api_name
        )
        
        # Initialize memory
        print("  💾 Loading memory system...")
        self.memory = MemorySystem(
            chroma_dir=settings.memory.chroma_dir,
            sqlite_path=settings.memory.sqlite_path
        )
        
        # Conversation state
        self.state = ConversationState(messages=[])
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        if not local_available:
            print(f"\n  ℹ️  Running in API-only mode ({api_name.upper()})")
            print("    Install Ollama + GPU for local inference\n")
        else:
            print("  ✅ Balloon Boy ready!\n")
    
    def _build_system_prompt(self) -> str:
    """Build system prompt with personality and guidelines"""
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return f"""You are Balloon Boy, an AI-powered animatronic assistant.

IMPORTANT: Today's date is {current_date}.

You are:
- Friendly and helpful
- Clear and concise in your responses
- Knowledgeable about your user's preferences and history
- Able to remember past conversations
- Professional but personable

When answering:
- Be direct and helpful
- Use the user's name and personal details when relevant
- Reference past conversations when appropriate
- Keep responses focused and avoid unnecessary verbosity
- If you don't know something, say so honestly

You have access to the user's profile and past conversations to provide personalized assistance."""
    
    def chat(
        self,
        user_message: str,
        force_model: Optional[str] = None,
        include_memory: bool = True,
        verbose: bool = True
    ) -> str:
        """
        Main chat interface
        
        Args:
            user_message: User's input
            force_model: Force specific model ("local" or "api")
            include_memory: Whether to include memory context
            verbose: Print routing decisions
            
        Returns:
            Assistant's response
        """
        # Build context from memory
        context = ""
        if include_memory:
            context = self.memory.build_context_prompt(
                current_query=user_message,
                include_profile=True,
                include_relevant_memories=True,
                n_memories=3
            )
        
        # Prepare messages
        messages = []
        
        # Add system prompt with context
        if context or self.system_prompt:
            full_system = self.system_prompt
            if context:
                full_system += f"\n\n{context}"
            messages.append(Message(role="system", content=full_system))
        
        # Add conversation history (recent messages)
        recent_history = self.memory.get_recent_conversations(n=5)
        for conv in recent_history:
            messages.append(Message(role="user", content=conv["user"]))
            messages.append(Message(role="assistant", content=conv["assistant"]))
        
        # Add current message
        messages.append(Message(role="user", content=user_message))
        
        # Get routing decision
        if not force_model and verbose and self.ollama:
            decision = self.router.route(user_message, messages)
            print(f"  {self.router.explain_decision(decision)}")
        
        # Generate response
        try:
            response, model_used = self.llm.generate(
                messages=messages,
                force_model=force_model
            )
            
            # Store in memory
            complexity = self.router.route(user_message).complexity_score if self.ollama else 5.0
            self.memory.remember_conversation(
                user_msg=user_message,
                assistant_response=response,
                model_used=model_used,
                complexity_score=complexity
            )
            
            return response
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"❌ {error_msg}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def learn_fact(self, category: str, key: str, value: str):
        """Teach Balloon Boy a fact about the user"""
        self.memory.remember_fact(category, key, value)
        print(f"  ✓ Learned: {category}.{key} = {value}")
    
    def get_profile(self) -> Dict:
        """Get user profile"""
        return self.memory.get_user_profile()
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
        return {
            "llm_stats": self.llm.get_stats(),
            "memory_stats": self.memory.get_stats()
        }
    
    def reset_conversation(self):
        """Clear conversation history (but keep learned facts)"""
        self.state = ConversationState(messages=[])
        print("  🔄 Conversation reset")
    
    def shutdown(self):
        """Clean shutdown"""
        print("\n👋 Shutting down Balloon Boy...")
        self.memory.close()
        print("  ✓ Memory saved")


# Interactive CLI
def interactive_cli():
    """Interactive command-line interface"""
    import readline
    import sys
    
    print("=" * 60)
    print("🎈 BALLOON BOY - Interactive Chat")
    print("=" * 60)
    
    # Choose API provider
    print("\nWhich API would you like to use?")
    print("  1. OpenAI (GPT-4o-mini) - Uses your ChatGPT credits")
    print("  2. Claude (Sonnet 4.5) - Requires Anthropic API key")
    print("  3. Auto-detect from .env file")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        api_provider = "openai"
    elif choice == "2":
        api_provider = "claude"
    else:
        # Auto-detect based on which key is set
        if settings.model.openai_api_key:
            api_provider = "openai"
            print("  → Auto-detected: OpenAI API key found")
        elif settings.model.anthropic_api_key:
            api_provider = "claude"
            print("  → Auto-detected: Claude API key found")
        else:
            print("  ❌ No API key found in .env file")
            sys.exit(1)
    
    print("\nCommands:")
    print("  /learn <category> <key> <value> - Teach a fact")
    print("  /profile - Show user profile")
    print("  /stats - Show usage statistics")
    print("  /local - Force local model for next query")
    print("  /api - Force API model for next query")
    print("  /reset - Reset conversation")
    print("  /quit or /exit - Exit")
    print("\n" + "=" * 60 + "\n")
    
    # Initialize agent
    try:
        agent = BalloonBoyAgent(api_provider=api_provider)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    force_model = None
    
    try:
        while True:
            # Get user input
            try:
                user_input = input("\n💬 You: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=3)
                command = parts[0].lower()
                
                if command in ["/quit", "/exit"]:
                    break
                    
                elif command == "/learn":
                    if len(parts) == 4:
                        _, category, key, value = parts
                        agent.learn_fact(category, key, value)
                    else:
                        print("  Usage: /learn <category> <key> <value>")
                        
                elif command == "/profile":
                    profile = agent.get_profile()
                    print("\n📋 User Profile:")
                    for category, facts in profile.items():
                        print(f"\n  {category.title()}:")
                        for key, value in facts.items():
                            print(f"    • {key}: {value}")
                            
                elif command == "/stats":
                    stats = agent.get_stats()
                    print("\n📊 Statistics:")
                    print(f"\n  LLM Usage:")
                    for key, value in stats["llm_stats"].items():
                        print(f"    • {key}: {value}")
                    print(f"\n  Memory:")
                    for key, value in stats["memory_stats"].items():
                        print(f"    • {key}: {value}")
                        
                elif command == "/local":
                    force_model = "local"
                    print("  → Next query will use local model")
                    
                elif command == "/api":
                    force_model = "api"
                    print(f"  → Next query will use {api_provider.upper()} API")
                    
                elif command == "/reset":
                    agent.reset_conversation()
                    
                else:
                    print(f"  Unknown command: {command}")
                    
                continue
            
            # Regular chat message
            print("\n🤖 Balloon Boy:", end=" ", flush=True)
            response = agent.chat(
                user_input,
                force_model=force_model,
                verbose=True
            )
            print(f"{response}")
            
            # Reset force_model after use
            force_model = None
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        agent.shutdown()
        print("\nGoodbye! 👋\n")


if __name__ == "__main__":
    interactive_cli()
