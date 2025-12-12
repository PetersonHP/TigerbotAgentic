"""Game Theory Optimal (GTO) strategy for Kuhn Poker.

Based on the Nash equilibrium solution for Kuhn Poker.

Strategy summary:
- Jack: Always check/fold, bluff bet 1/3 when opponent checks
- Queen: Always check/call, never bet
- King: Bet 3x (always bet for value), always call, bet when checked to
"""

from typing import Dict


class GTOStrategy:
    """Implements the optimal (GTO) strategy for Kuhn Poker."""

    @staticmethod
    def get_strategy(info_set: str) -> Dict[str, float]:
        """Get GTO strategy for an information set.

        Args:
            info_set: Information set string (e.g., "K.BET", "J.", "Q.CHECK")

        Returns:
            Dictionary mapping actions to probabilities
        """
        card, history = info_set.split('.')

        # Player 1 (first to act)
        if history == '':
            return GTOStrategy._get_p1_strategy(card)

        # Player 2 facing a bet
        elif history == 'BET':
            return GTOStrategy._get_p2_facing_bet(card)

        # Player 2 after opponent checks
        elif history == 'CHECK':
            return GTOStrategy._get_p2_after_check(card)

        else:
            raise ValueError(f"Unknown information set: {info_set}")

    @staticmethod
    def _get_p1_strategy(card: str) -> Dict[str, float]:
        """Get Player 1 (first to act) strategy.

        Args:
            card: Player's card ('J', 'Q', 'K')

        Returns:
            Action probability distribution
        """
        if card == 'J':
            # Jack: Always check (will bluff later if opponent checks)
            return {'CHECK': 1.0, 'BET': 0.0}

        elif card == 'Q':
            # Queen: Always check (medium strength)
            return {'CHECK': 1.0, 'BET': 0.0}

        elif card == 'K':
            # King: Always bet for value (best hand)
            # In optimal play, King bets with probability 3 * alpha
            # where alpha = 1/3 (Jack's bluffing frequency)
            # This simplifies to: always bet (probability 1.0)
            return {'CHECK': 0.0, 'BET': 1.0}

        else:
            raise ValueError(f"Invalid card: {card}")

    @staticmethod
    def _get_p2_facing_bet(card: str) -> Dict[str, float]:
        """Get Player 2 strategy when facing a bet.

        Args:
            card: Player's card ('J', 'Q', 'K')

        Returns:
            Action probability distribution
        """
        if card == 'J':
            # Jack: Always fold (worst hand)
            return {'CALL': 0.0, 'FOLD': 1.0}

        elif card == 'Q':
            # Queen: Always call (need to catch bluffs)
            # Calling frequency must match opponent's bluff:value ratio
            return {'CALL': 1.0, 'FOLD': 0.0}

        elif card == 'K':
            # King: Always call (best hand)
            return {'CALL': 1.0, 'FOLD': 0.0}

        else:
            raise ValueError(f"Invalid card: {card}")

    @staticmethod
    def _get_p2_after_check(card: str) -> Dict[str, float]:
        """Get Player 2 strategy after opponent checks.

        Args:
            card: Player's card ('J', 'Q', 'K')

        Returns:
            Action probability distribution
        """
        if card == 'J':
            # Jack: Bluff bet 1/3 of the time
            # This is the optimal bluffing frequency
            return {'CHECK': 2/3, 'BET': 1/3}

        elif card == 'Q':
            # Queen: Always check (medium strength, don't want to blow up pot)
            return {'CHECK': 1.0, 'BET': 0.0}

        elif card == 'K':
            # King: Always bet for value when checked to
            return {'CHECK': 0.0, 'BET': 1.0}

        else:
            raise ValueError(f"Invalid card: {card}")

    @staticmethod
    def get_expected_value(info_set: str) -> float:
        """Get expected value for an information set under GTO play.

        This is useful for analysis and verification.

        Args:
            info_set: Information set string

        Returns:
            Expected value in chips
        """
        # Expected values under GTO play (from game theory literature)
        # These are approximate values for reference
        ev_map = {
            'J.': -1/18,
            'Q.': -1/18,
            'K.': 1/9,
            'J.BET': -1,
            'Q.BET': 0,
            'K.BET': 1,
            'J.CHECK': -1/6,
            'Q.CHECK': 0,
            'K.CHECK': 1/6,
        }

        return ev_map.get(info_set, 0.0)
