"""Abstract base class for poker agents."""

from abc import ABC, abstractmethod
from typing import List
from kuhn_poker.state import GameState


class BaseAgent(ABC):
    """Abstract base class for all poker agents.

    All agents must implement choose_action() to select an action
    given the current game state and legal actions.
    """

    def __init__(self, name: str):
        """Initialize the agent.

        Args:
            name: Agent name for identification
        """
        self.name = name

    @abstractmethod
    def choose_action(self, state: GameState, legal_actions: List[str], player_position: int) -> str:
        """Choose an action given the current game state.

        Args:
            state: Current game state
            legal_actions: List of legal actions
            player_position: This agent's position (0 or 1)

        Returns:
            Chosen action (must be in legal_actions)
        """
        pass

    def observe_result(self, state: GameState, action: str, result_state: GameState, player_position: int) -> None:
        """Observe the result of an action (for learning agents).

        Optional method that agents can override to learn from outcomes.

        Args:
            state: State before action
            action: Action taken
            result_state: State after action
            player_position: This agent's position
        """
        pass

    def observe_opponent_action(self, state: GameState, action: str, player_position: int) -> None:
        """Observe an opponent's action (for opponent modeling).

        Optional method that agents can override to track opponent behavior.

        Args:
            state: State when opponent acted
            action: Opponent's action
            player_position: This agent's position
        """
        pass

    def reset(self) -> None:
        """Reset agent state between sessions.

        Optional method for agents that maintain state.
        """
        pass

    def __str__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}({self.name})"
