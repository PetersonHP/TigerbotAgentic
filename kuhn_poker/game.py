"""Core Kuhn Poker game engine."""

import random
from typing import List, Tuple, Optional
from .state import GameState


class KuhnPokerGame:
    """Kuhn Poker game engine.

    Implements the rules of Kuhn Poker:
    - 2 players, 3 cards (J, Q, K)
    - Each player antes 1 chip
    - Each player gets 1 card
    - One round of betting (Player 0 acts first)
    - Actions: CHECK or BET (1 chip)
    - Winner: Highest card at showdown
    """

    CARDS = ['J', 'Q', 'K']
    CARD_VALUES = {'J': 1, 'Q': 2, 'K': 3}
    ANTE = 1
    BET_SIZE = 1

    def __init__(self, seed: Optional[int] = None):
        """Initialize the game.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        self.state: Optional[GameState] = None

    def deal_cards(self) -> dict[int, str]:
        """Deal cards randomly to both players.

        Returns:
            Dictionary mapping player index to card
        """
        deck = self.CARDS.copy()
        random.shuffle(deck)
        return {0: deck[0], 1: deck[1]}

    def start_new_hand(self) -> GameState:
        """Start a new hand.

        Returns:
            Initial game state
        """
        cards = self.deal_cards()
        self.state = GameState(
            cards=cards,
            betting_history=[],
            pot=2 * self.ANTE,  # Both players ante
            current_player=0,   # Player 0 acts first
            is_terminal=False
        )
        return self.state

    def get_legal_actions(self, state: GameState) -> List[str]:
        """Get legal actions for the current player.

        Args:
            state: Current game state

        Returns:
            List of legal actions ('CHECK', 'BET', 'CALL', 'FOLD')
        """
        if state.is_terminal:
            return []

        history = state.betting_history

        # First action: CHECK or BET
        if len(history) == 0:
            return ['CHECK', 'BET']

        # After CHECK: CHECK (showdown) or BET
        if len(history) == 1 and history[0] == 'CHECK':
            return ['CHECK', 'BET']

        # After BET: CALL or FOLD
        if (len(history) == 1 and history[0] == 'BET') or \
           (len(history) == 2 and history[1] == 'BET'):
            return ['CALL', 'FOLD']

        # Should not reach here
        raise ValueError(f"Invalid betting history: {history}")

    def apply_action(self, state: GameState, action: str) -> GameState:
        """Apply an action and return the new state.

        Args:
            state: Current game state
            action: Action to apply

        Returns:
            New game state after action
        """
        if action not in self.get_legal_actions(state):
            raise ValueError(f"Illegal action {action} for state {state}")

        # Create new state with updated history
        new_history = state.betting_history + [action]
        new_pot = state.pot
        new_player = 1 - state.current_player  # Switch player
        is_terminal = False
        payoffs = None

        # Update pot if betting
        if action == 'BET':
            new_pot += self.BET_SIZE
        elif action == 'CALL':
            new_pot += self.BET_SIZE

        # Check for terminal states
        if action == 'FOLD':
            # Current player folds, opponent wins pot
            is_terminal = True
            payoffs = self._calculate_fold_payoffs(state.current_player, new_pot)

        elif len(new_history) == 2 and new_history == ['CHECK', 'CHECK']:
            # Both players check, showdown
            is_terminal = True
            payoffs = self._calculate_showdown_payoffs(state.cards, new_pot)

        elif action == 'CALL':
            # Call leads to showdown
            is_terminal = True
            payoffs = self._calculate_showdown_payoffs(state.cards, new_pot)

        new_state = GameState(
            cards=state.cards,
            betting_history=new_history,
            pot=new_pot,
            current_player=new_player if not is_terminal else state.current_player,
            is_terminal=is_terminal,
            payoffs=payoffs
        )

        return new_state

    def _calculate_fold_payoffs(self, folding_player: int, pot: int) -> dict[int, int]:
        """Calculate payoffs when a player folds.

        Args:
            folding_player: Player who folded
            pot: Total pot size

        Returns:
            Dictionary of payoffs (relative to antes)
        """
        winning_player = 1 - folding_player
        # Winner gets pot, loser loses ante + any bets
        # Payoffs are relative to starting stack (after ante)
        payoffs = {
            winning_player: pot // 2,     # Wins half the pot (their ante returned + opponent's chips)
            folding_player: -(pot // 2)   # Loses their contribution
        }
        return payoffs

    def _calculate_showdown_payoffs(self, cards: dict[int, str], pot: int) -> dict[int, int]:
        """Calculate payoffs at showdown.

        Args:
            cards: Dictionary of player cards
            pot: Total pot size

        Returns:
            Dictionary of payoffs
        """
        winner = self._get_showdown_winner(cards)
        payoffs = {
            winner: pot // 2,
            1 - winner: -(pot // 2)
        }
        return payoffs

    def _get_showdown_winner(self, cards: dict[int, str]) -> int:
        """Determine winner at showdown.

        Args:
            cards: Dictionary of player cards

        Returns:
            Winning player index
        """
        if self.CARD_VALUES[cards[0]] > self.CARD_VALUES[cards[1]]:
            return 0
        else:
            return 1

    def is_terminal(self, state: GameState) -> bool:
        """Check if the game state is terminal.

        Args:
            state: Game state to check

        Returns:
            True if game has ended
        """
        return state.is_terminal

    def get_payoff(self, state: GameState, player: int) -> int:
        """Get payoff for a player in a terminal state.

        Args:
            state: Terminal game state
            player: Player index

        Returns:
            Payoff (chips won/lost)
        """
        if not state.is_terminal:
            raise ValueError("Cannot get payoff from non-terminal state")
        return state.payoffs[player]
