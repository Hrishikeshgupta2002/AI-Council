"""
Configuration module for the Agentic Council System.
Handles environment variables and default settings.
"""

import os
from typing import Dict, Any


class Config:
    """Application configuration."""
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Model Configuration
    USE_WEIGHTED_MODEL: bool = os.getenv("USE_WEIGHTED_MODEL", "true").lower() == "true"
    
    # Agent Configuration
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "60"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    DEBATE_ROUNDS: int = int(os.getenv("DEBATE_ROUNDS", "2"))
    MAX_DEBATE_EXCHANGES: int = int(os.getenv("MAX_DEBATE_EXCHANGES", "3"))
    
    # Debug Configuration
    DEBUG: bool = os.getenv("DEBUG", "").lower() == "true"
    
    # Agent Name Mappings
    AGENT_NAME_MAPPING: Dict[str, str] = {
        "Visionary": "Elon",
        "Strategist": "Sam",
        "Operator": "Sheryl",
        "Risk Analyst": "Ray"
    }
    
    # Agent Weights (for weighted decision model)
    AGENT_WEIGHTS: Dict[str, float] = {
        "Visionary": 0.35,
        "Strategist": 0.30,
        "Operator": 0.20,
        "Risk Analyst": 0.15,
    }
    
    # Agent Models
    AGENT_MODELS: Dict[str, str] = {
        "Visionary": "gpt-oss:120b-cloud",
        "Strategist": "glm-4.6:cloud",
        "Operator": "kimi-k2-thinking:cloud",
        "Risk Analyst": "deepseek-v3.1:671b-cloud",
    }
    
    # Synthesis Model
    SYNTHESIS_MODEL: str = "gpt-oss:120b-cloud"
    SYNTHESIS_TEMPERATURE: float = 0.6
    
    @classmethod
    def get_reverse_agent_mapping(cls) -> Dict[str, str]:
        """Get reverse mapping from short names to full names."""
        return {v: k for k, v in cls.AGENT_NAME_MAPPING.items()}
    
    @classmethod
    def get_all_config(cls) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        return {
            "ollama_base_url": cls.OLLAMA_BASE_URL,
            "use_weighted_model": cls.USE_WEIGHTED_MODEL,
            "agent_timeout": cls.AGENT_TIMEOUT,
            "max_workers": cls.MAX_WORKERS,
            "debate_rounds": cls.DEBATE_ROUNDS,
            "max_debate_exchanges": cls.MAX_DEBATE_EXCHANGES,
            "debug": cls.DEBUG,
            "agent_weights": cls.AGENT_WEIGHTS,
        }

