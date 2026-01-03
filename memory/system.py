"""
Memory System: Episodic (ChromaDB) + Semantic (SQLite) Memory
"""
import chromadb
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json

class MemorySystem:
    """
    Dual memory system:
    - Episodic: ChromaDB vector store for conversation history
    - Semantic: SQLite for structured facts about user
    """
    
    def __init__(self, chroma_dir: Path, sqlite_path: Path):
        # Vector storage for conversations
        self.chroma_client = chromadb.PersistentClient(path=str(chroma_dir))
        self.conversations = self.chroma_client.get_or_create_collection(
            name="conversations",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Structured storage for facts
        self.db_path = sqlite_path
        self.db = sqlite3.connect(str(sqlite_path))
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite schema"""
        cursor = self.db.cursor()
        
        # User facts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_facts (
                category TEXT,
                key TEXT,
                value TEXT,
                updated_at TIMESTAMP,
                PRIMARY KEY (category, key)
            )
        """)
        
        # Conversation metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                user_message TEXT,
                assistant_response TEXT,
                model_used TEXT,
                complexity_score REAL
            )
        """)
        
        self.db.commit()
    
    def remember_conversation(
        self,
        user_msg: str,
        assistant_response: str,
        model_used: str,
        complexity_score: float = 0.0
    ):
        """
        Store conversation in both episodic memory and conversation log
        """
        timestamp = datetime.now().isoformat()
        
        # Store in vector DB for semantic search
        conversation_text = f"User: {user_msg}\nAssistant: {assistant_response}"
        self.conversations.add(
            documents=[conversation_text],
            metadatas=[{
                "timestamp": timestamp,
                "model": model_used,
                "complexity": complexity_score
            }],
            ids=[f"conv_{timestamp}"]
        )
        
        # Store in SQL for logging
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO conversation_log 
            (timestamp, user_message, assistant_response, model_used, complexity_score)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, user_msg, assistant_response, model_used, complexity_score))
        self.db.commit()
    
    def remember_fact(self, category: str, key: str, value: str):
        """
        Store structured fact about user
        
        Examples:
            remember_fact("profile", "name", "Thiago")
            remember_fact("preferences", "favorite_food", "pizza")
            remember_fact("work", "university", "Northeastern")
        """
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_facts 
            (category, key, value, updated_at)
            VALUES (?, ?, ?, ?)
        """, (category, key, value, datetime.now()))
        self.db.commit()
    
    def recall_conversations(self, query: str, n_results: int = 5) -> List[str]:
        """
        Semantic search through past conversations
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant conversation excerpts
        """
        try:
            results = self.conversations.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                return results['documents'][0]
            return []
        except Exception as e:
            print(f"⚠️  Memory recall failed: {e}")
            return []
    
    def get_user_profile(self) -> Dict[str, Dict[str, str]]:
        """
        Get all known facts about user, organized by category
        
        Returns:
            {
                "profile": {"name": "Thiago", ...},
                "preferences": {...},
                "work": {...}
            }
        """
        cursor = self.db.cursor()
        cursor.execute("SELECT category, key, value FROM user_facts")
        
        profile = {}
        for category, key, value in cursor.fetchall():
            if category not in profile:
                profile[category] = {}
            profile[category][key] = value
            
        return profile
    
    def get_fact(self, category: str, key: str) -> Optional[str]:
        """Get a specific fact"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT value FROM user_facts WHERE category = ? AND key = ?",
            (category, key)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def get_recent_conversations(self, n: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT timestamp, user_message, assistant_response, model_used, complexity_score
            FROM conversation_log
            ORDER BY timestamp DESC
            LIMIT ?
        """, (n,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "timestamp": row[0],
                "user": row[1],
                "assistant": row[2],
                "model": row[3],
                "complexity": row[4]
            })
        
        return list(reversed(conversations))  # Chronological order
    
    def build_context_prompt(
        self,
        current_query: str,
        include_profile: bool = True,
        include_relevant_memories: bool = True,
        n_memories: int = 3
    ) -> str:
        """
        Build context string for LLM from memory
        
        This gets prepended to the conversation to give the model context
        """
        context_parts = []
        
        # User profile
        if include_profile:
            profile = self.get_user_profile()
            if profile:
                context_parts.append("## About the User")
                for category, facts in profile.items():
                    context_parts.append(f"\n**{category.title()}:**")
                    for key, value in facts.items():
                        context_parts.append(f"- {key}: {value}")
        
        # Relevant past conversations
        if include_relevant_memories:
            memories = self.recall_conversations(current_query, n_results=n_memories)
            if memories:
                context_parts.append("\n## Relevant Past Conversations")
                for i, memory in enumerate(memories, 1):
                    # Truncate long memories
                    memory_excerpt = memory[:200] + "..." if len(memory) > 200 else memory
                    context_parts.append(f"\n{i}. {memory_excerpt}")
        
        if context_parts:
            return "\n".join(context_parts) + "\n\n---\n"
        return ""
    
    def get_stats(self) -> Dict:
        """Get memory system statistics"""
        cursor = self.db.cursor()
        
        # Count conversations
        cursor.execute("SELECT COUNT(*) FROM conversation_log")
        total_conversations = cursor.fetchone()[0]
        
        # Count facts
        cursor.execute("SELECT COUNT(*) FROM user_facts")
        total_facts = cursor.fetchone()[0]
        
        # Model usage
        cursor.execute("""
            SELECT model_used, COUNT(*) 
            FROM conversation_log 
            GROUP BY model_used
        """)
        model_usage = dict(cursor.fetchall())
        
        return {
            "total_conversations": total_conversations,
            "total_facts": total_facts,
            "model_usage": model_usage,
            "vector_embeddings": self.conversations.count()
        }
    
    def close(self):
        """Close database connections"""
        self.db.close()


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    
    # Initialize memory system
    memory = MemorySystem(
        chroma_dir=Path("./data/memories_test"),
        sqlite_path=Path("./data/test_profile.db")
    )
    
    # Store some facts
    memory.remember_fact("profile", "name", "Thiago")
    memory.remember_fact("profile", "university", "Northeastern")
    memory.remember_fact("work", "field", "Robotics")
    memory.remember_fact("preferences", "favorite_language", "Python")
    
    # Store conversations
    memory.remember_conversation(
        "What's my name?",
        "Your name is Thiago!",
        "gemma-2-9b",
        complexity_score=1.0
    )
    
    memory.remember_conversation(
        "Explain reinforcement learning",
        "Reinforcement learning is a type of machine learning...",
        "claude-sonnet-4.5",
        complexity_score=5.5
    )
    
    # Retrieve
    print("📊 User Profile:")
    print(json.dumps(memory.get_user_profile(), indent=2))
    
    print("\n🔍 Relevant memories for 'robotics':")
    memories = memory.recall_conversations("robotics", n_results=2)
    for mem in memories:
        print(f"  - {mem[:100]}...")
    
    print("\n💾 Memory Stats:")
    print(json.dumps(memory.get_stats(), indent=2))
    
    memory.close()
