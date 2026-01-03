"""
Balloon Boy Agent with Tool Integration
Complete agentic AI system
"""
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agent.router import ModelRouter
from memory.system import MemorySystem
from config.settings import settings

# Import the Message class
class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

@dataclass
class ConversationState:
    """Current state of the conversation"""
    messages: List[Message]
    user_profile_loaded: bool = False

class BalloonBoyAgentWithTools:
    """
    Main AI agent with tool integration
    
    Features:
    - Web search for real-time info
    - Current date/time
    - Conversation memory
    - User profile learning
    """
    
    def __init__(self):
        print("🎈 Initializing Balloon Boy Agent with Tools...")
        
        # Import here to avoid circular dependencies
        from tools.manager import ToolManager
        from agent.openai_with_tools import OpenAIClientWithTools
        
        # Initialize tool manager
        print("  🔧 Loading tools...")
        self.tool_manager = ToolManager()
        
        # Initialize OpenAI client with tools
        print("  🌐 Connecting to OpenAI API...")
        api_key = settings.model.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in config/.env")
        
        self.llm = OpenAIClientWithTools(
            api_key=api_key,
            model=settings.model.openai_model
        )
        
        # Register all tools with the LLM
        print("  🔌 Registering tools with AI...")
        for tool_def in self.tool_manager.get_tool_definitions():
            tool_name = tool_def["function"]["name"]
            self.llm.register_tool(
                name=tool_name,
                function=lambda name=tool_name, **kwargs: self.tool_manager.execute_tool(name, **kwargs),
                definition=tool_def
            )
        
        # Initialize memory
        print("  💾 Loading memory system...")
        self.memory = MemorySystem(
            chroma_dir=settings.memory.chroma_dir,
            sqlite_path=settings.memory.sqlite_path
        )
        
        # System prompt
        self.system_prompt = self._build_system_prompt()
        
        # Stats
        self.stats = {"total_queries": 0, "tool_calls": 0}
        
        print("  ✅ Balloon Boy ready with tools!\n")
    
    def _build_system_prompt(self) -> str:
        """Build system prompt"""
        return """You are Balloon Boy, an AI-powered animatronic assistant.

You have access to tools that let you:
- Get the current date and time
- Search the web for current information
- Search for recent news

Use these tools whenever you need real-time information or data beyond your knowledge cutoff (October 2023).

Your personality:
- Friendly and helpful
- Clear and concise
- Use the user's name and personal details when relevant
- Reference past conversations when appropriate

Always use your tools when appropriate - don't guess about current information!"""
    
    def chat(
        self,
        user_message: str,
        include_memory: bool = True,
        verbose: bool = True
    ) -> str:
        """
        Main chat interface with tool support
        
        Args:
            user_message: User's input
            include_memory: Include memory context
            verbose: Print debug info
            
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
        
        # System prompt with context
        full_system = self.system_prompt
        if context:
            full_system += f"\n\n{context}"
        messages.append(Message(role="system", content=full_system))
        
        # Recent conversation history
        recent_history = self.memory.get_recent_conversations(n=5)
        for conv in recent_history:
            messages.append(Message(role="user", content=conv["user"]))
            messages.append(Message(role="assistant", content=conv["assistant"]))
        
        # Current message
        messages.append(Message(role="user", content=user_message))
        
        # Generate with tools
        try:
            response = self.llm.generate_with_tools(messages)
            
            # Store in memory
            self.memory.remember_conversation(
                user_msg=user_message,
                assistant_response=response,
                model_used="gpt-4o-mini-with-tools",
                complexity_score=0.0
            )
            
            self.stats["total_queries"] += 1
            
            return response
            
        except Exception as e:
            error_msg = f"Error: {e}"
            print(f"❌ {error_msg}")
            return f"I apologize, I encountered an error: {str(e)}"
    
    def learn_fact(self, category: str, key: str, value: str):
        """Teach Balloon Boy a fact"""
        self.memory.remember_fact(category, key, value)
        print(f"  ✓ Learned: {category}.{key} = {value}")
    
    def get_profile(self) -> Dict:
        """Get user profile"""
        return self.memory.get_user_profile()
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            "queries": self.stats["total_queries"],
            "memory": self.memory.get_stats()
        }
    
    def shutdown(self):
        """Clean shutdown"""
        print("\n👋 Shutting down Balloon Boy...")
        self.memory.close()
        print("  ✓ Memory saved")


# Interactive CLI
def interactive_cli():
    """Interactive command-line interface with tools"""
    import readline
    
    print("=" * 60)
    print("🎈 BALLOON BOY - Interactive Chat with Tools")
    print("=" * 60)
    print("\nCommands:")
    print("  /learn <category> <key> <value> - Teach a fact")
    print("  /profile - Show user profile")
    print("  /stats - Show statistics")
    print("  /quit or /exit - Exit")
    print("\n" + "=" * 60 + "\n")
    
    # Initialize agent
    try:
        agent = BalloonBoyAgentWithTools()
    except ValueError as e:
        print(f"❌ {e}")
        print("\nMake sure you've set OPENAI_API_KEY in config/.env")
        sys.exit(1)
    
    try:
        while True:
            # Get input
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
                    print(f"  • Total queries: {stats['queries']}")
                    print(f"  • Conversations stored: {stats['memory']['total_conversations']}")
                    print(f"  • Facts learned: {stats['memory']['total_facts']}")
                    
                else:
                    print(f"  Unknown command: {command}")
                    
                continue
            
            # Regular chat with tools
            print("\n🤖 Balloon Boy:", end=" ", flush=True)
            response = agent.chat(user_input, verbose=True)
            print(f"{response}")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    finally:
        agent.shutdown()
        print("\nGoodbye! 👋\n")


if __name__ == "__main__":
    interactive_cli()
