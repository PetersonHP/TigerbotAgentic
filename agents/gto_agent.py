"""GTO (Game Theory Optimal) agent implementation."""

import random
from typing import List
from .base_agent import BaseAgent
from kuhn_poker.state import GameState
from kuhn_poker.gto_strategy import GTOStrategy


class GTOAgent(BaseAgent):
    """Agent that plays the Game Theory Optimal (Nash equilibrium) strategy.

    This agent uses the mathematically optimal Kuhn Poker strategy.
    It cannot be exploited in expectation - any deviation by opponents
    will result in them losing money.
    """

    def __init__(self, name: str = "GTO"):
        """Initialize the GTO agent.

        Args:
            name: Agent name
        """
        super().__init__(name)
        self.gto_strategy = GTOStrategy()

    def choose_action(self, state: GameState, legal_actions: List[str], player_position: int) -> str:
        """Choose action according to GTO strategy.

        Args:
            state: Current game state
            legal_actions: List of legal actions
            player_position: This agent's position (0 or 1)

        Returns:
            Action sampled from GTO probability distribution
        """
        # Get information set for this player
        info_set = state.get_info_set(player_position)

        # Get GTO strategy (probability distribution over actions)
        strategy = self.gto_strategy.get_strategy(info_set)

        # Sample action according to probabilities
        actions = list(strategy.keys())
        probabilities = list(strategy.values())

        # Filter to only legal actions (safety check)
        legal_strategy = {a: p for a, p in strategy.items() if a in legal_actions}

        if not legal_strategy:
            # Fallback: choose randomly from legal actions
            return random.choice(legal_actions)

        # Normalize probabilities
        total_prob = sum(legal_strategy.values())
        normalized_probs = [p / total_prob for p in legal_strategy.values()]

        # Sample action
        action = random.choices(list(legal_strategy.keys()), weights=normalized_probs, k=1)[0]

        return action
