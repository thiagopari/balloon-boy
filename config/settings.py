"""
Configuration management for Balloon Boy Hybrid AI System
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Optional

# Load environment variables
load_dotenv()

@dataclass
class ModelConfig:
    """LLM model configuration"""
    # Local model (Ollama)
    local_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    local_model: str = os.getenv("OLLAMA_MODEL", "gemma2:9b-instruct-q4_K_M")
    local_timeout: int = 60
    
    # OpenAI API
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # or gpt-4o, gpt-3.5-turbo
    
    # Claude API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 4096
    
    # Routing configuration
    complexity_threshold: float = float(os.getenv("COMPLEXITY_THRESHOLD", "3.0"))
    max_local_tokens: int = int(os.getenv("MAX_LOCAL_TOKENS", "8000"))

@dataclass
class MemoryConfig:
    """Memory system configuration"""
    chroma_dir: Path = field(default_factory=lambda: Path(os.getenv("CHROMA_PERSIST_DIR", "./data/memories")))
    sqlite_path: Path = field(default_factory=lambda: Path(os.getenv("SQLITE_DB_PATH", "./data/user_profile.db")))
    max_context_messages: int = 10
    embedding_model: str = "all-MiniLM-L6-v2"

@dataclass
class VoiceConfig:
    """Voice interface configuration"""
    whisper_model: str = "base"  # base, small, medium, large
    tts_engine: str = "pyttsx3"
    tts_rate: int = 175  # Words per minute
    wake_word: str = "hey balloon boy"
    
    # Audio settings
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1

@dataclass
class Settings:
    """Main configuration container"""
    # Use default_factory for mutable defaults
    model: ModelConfig = field(default_factory=ModelConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    
    # Project paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    
    def __post_init__(self):
        """Ensure directories exist"""
        self.data_dir.mkdir(exist_ok=True)
        self.memory.chroma_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate API key (need at least one)
        if not self.model.anthropic_api_key and not self.model.openai_api_key:
            raise ValueError(
                "No API key found. Please set either OPENAI_API_KEY or "
                "ANTHROPIC_API_KEY in config/.env"
            )

# Global settings instance
settings = Settings()
