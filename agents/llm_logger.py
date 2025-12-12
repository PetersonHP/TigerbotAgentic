"""LLM conversation logging utility."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class LLMLogger:
    """Logger for LLM conversations.

    Logs all prompts and responses to structured JSON files in the logs directory.
    Each agent gets its own log file.
    """

    def __init__(self, agent_name: str, logs_dir: str = "logs"):
        """Initialize the LLM logger.

        Args:
            agent_name: Name of the agent (used for log filename)
            logs_dir: Directory to store log files
        """
        self.agent_name = agent_name
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)

        # Create a log file for this agent with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"{agent_name}_{timestamp}.jsonl"

    def log_conversation(
        self,
        prompt: str,
        response: str,
        model: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an LLM conversation.

        Args:
            prompt: The prompt sent to the LLM
            response: The response from the LLM
            model: The model name used
            metadata: Additional metadata to log (e.g., temperature, max_tokens, game state)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "model": model,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }

        # Append to JSONL file (one JSON object per line)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def log_error(
        self,
        error: Exception,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an LLM error.

        Args:
            error: The exception that occurred
            prompt: The prompt that caused the error
            metadata: Additional metadata to log
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "error": str(error),
            "error_type": type(error).__name__,
            "prompt": prompt,
            "metadata": metadata or {}
        }

        # Append to JSONL file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
