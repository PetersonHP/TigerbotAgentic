"""Logging system for tournament games."""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class GameLogger:
    """Logs game data for analysis."""

    def __init__(self, output_dir: str = "results"):
        """Initialize the logger.

        Args:
            output_dir: Directory to save log files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.hands: List[Dict[str, Any]] = []

    def log_hand(self, hand_data: Dict[str, Any]) -> None:
        """Log data from a single hand.

        Args:
            hand_data: Dictionary containing hand information
        """
        self.hands.append(hand_data)

    def save_tournament(self, matchup_name: str, agent_names: Dict[int, str],
                       total_hands: int, profits: Dict[int, int]) -> str:
        """Save tournament results to JSON file.

        Args:
            matchup_name: Name of the matchup (e.g., "GTO_vs_HumanLike")
            agent_names: Dictionary mapping positions to agent names
            total_hands: Total number of hands played
            profits: Dictionary mapping positions to total profit

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{matchup_name}_{timestamp}.json"
        filepath = self.output_dir / filename

        data = {
            "matchup": matchup_name,
            "timestamp": timestamp,
            "agents": agent_names,
            "total_hands": total_hands,
            "profits": profits,
            "profit_per_100": {
                pos: (profit / total_hands * 100) for pos, profit in profits.items()
            },
            "hands": self.hands
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Tournament results saved to: {filepath}")
        return str(filepath)

    def save_summary(self, matchup_name: str, summary_stats: Dict[str, Any]) -> str:
        """Save summary statistics.

        Args:
            matchup_name: Name of the matchup
            summary_stats: Dictionary of summary statistics

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{matchup_name}_summary_{timestamp}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(summary_stats, f, indent=2)

        return str(filepath)

    def clear(self) -> None:
        """Clear logged hands."""
        self.hands = []

    def get_hands(self) -> List[Dict[str, Any]]:
        """Get all logged hands.

        Returns:
            List of hand dictionaries
        """
        return self.hands
