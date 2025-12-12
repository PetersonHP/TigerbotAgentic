"""Game state representation for Kuhn Poker."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GameState:
    """Represents the current state of a Kuhn Poker game.

    Attributes:
        cards: Dictionary mapping player positions (0, 1) to their cards ('J', 'Q', 'K')
        betting_history: List of actions taken (e.g., ['CHECK', 'BET', 'CALL'])
        pot: Total chips in the pot
        current_player: Index of player to act (0 or 1)
        is_terminal: Whether the game has ended
        payoffs: Dictionary of final payoffs (only set when terminal)
    """
    cards: dict[int, str]
    betting_history: List[str]
    pot: int
    current_player: int
    is_terminal: bool = False
    payoffs: Optional[dict[int, int]] = None

    def __str__(self) -> str:
        """String representation for logging."""
        history_str = '->'.join(self.betting_history) if self.betting_history else 'START'
        return f"GameState(pot={self.pot}, history={history_str}, player={self.current_player})"

    def get_betting_string(self) -> str:
        """Get betting history as a compact string."""
        return ''.join(self.betting_history)

    def get_info_set(self, player: int) -> str:
        """Get information set string for a player (card + betting history).

        This is used by agents to identify the current decision point.

        Args:
            player: Player index (0 or 1)

        Returns:
            String like "K.BET" (King facing a bet) or "Q." (Queen, first to act)
        """
        card = self.cards[player]

        # Determine what the player sees based on betting history
        history = self.betting_history

        if not history:
            # First to act
            return f"{card}."

        elif len(history) == 1:
            if history[0] == 'CHECK':
                # Opponent checked, now we act
                return f"{card}.CHECK"
            else:  # BET
                # Opponent bet, we must respond
                return f"{card}.BET"

        elif len(history) == 2:
            if history == ['CHECK', 'CHECK']:
                # Shouldn't happen (terminal)
                return f"{card}.CHECKCHECK"
            elif history == ['CHECK', 'BET']:
                # We checked, opponent bet, now we respond
                return f"{card}.BET"
            elif history == ['BET', 'CALL']:
                # Shouldn't happen (terminal)
                return f"{card}.BETCALL"
            elif history == ['BET', 'FOLD']:
                # Shouldn't happen (terminal)
                return f"{card}.BETFOLD"

        # Fallback: use full history
        return f"{card}.{self.get_betting_string()}"
