"""Unit tests for GTO strategy."""

import pytest
from kuhn_poker.gto_strategy import GTOStrategy


class TestGTOStrategy:
    """Test cases for GTO strategy implementation."""

    def test_jack_first_to_act(self):
        """Test Jack strategy when first to act."""
        strategy = GTOStrategy.get_strategy('J.')

        assert 'CHECK' in strategy
        assert 'BET' in strategy
        assert strategy['CHECK'] == 1.0  # Always check with Jack
        assert strategy['BET'] == 0.0

    def test_queen_first_to_act(self):
        """Test Queen strategy when first to act."""
        strategy = GTOStrategy.get_strategy('Q.')

        assert strategy['CHECK'] == 1.0  # Always check with Queen
        assert strategy['BET'] == 0.0

    def test_king_first_to_act(self):
        """Test King strategy when first to act."""
        strategy = GTOStrategy.get_strategy('K.')

        assert strategy['BET'] == 1.0  # Always bet with King
        assert strategy['CHECK'] == 0.0

    def test_jack_facing_bet(self):
        """Test Jack strategy when facing a bet."""
        strategy = GTOStrategy.get_strategy('J.BET')

        assert strategy['FOLD'] == 1.0  # Always fold Jack
        assert strategy['CALL'] == 0.0

    def test_queen_facing_bet(self):
        """Test Queen strategy when facing a bet."""
        strategy = GTOStrategy.get_strategy('Q.BET')

        assert strategy['CALL'] == 1.0  # Always call with Queen
        assert strategy['FOLD'] == 0.0

    def test_king_facing_bet(self):
        """Test King strategy when facing a bet."""
        strategy = GTOStrategy.get_strategy('K.BET')

        assert strategy['CALL'] == 1.0  # Always call with King
        assert strategy['FOLD'] == 0.0

    def test_jack_after_opponent_checks(self):
        """Test Jack strategy after opponent checks."""
        strategy = GTOStrategy.get_strategy('J.CHECK')

        assert 'CHECK' in strategy
        assert 'BET' in strategy
        # Jack bluffs 1/3 of the time
        assert abs(strategy['BET'] - 1/3) < 0.01
        assert abs(strategy['CHECK'] - 2/3) < 0.01

    def test_queen_after_opponent_checks(self):
        """Test Queen strategy after opponent checks."""
        strategy = GTOStrategy.get_strategy('Q.CHECK')

        assert strategy['CHECK'] == 1.0  # Always check with Queen
        assert strategy['BET'] == 0.0

    def test_king_after_opponent_checks(self):
        """Test King strategy after opponent checks."""
        strategy = GTOStrategy.get_strategy('K.CHECK')

        assert strategy['BET'] == 1.0  # Always bet King for value
        assert strategy['CHECK'] == 0.0

    def test_probabilities_sum_to_one(self):
        """Test that all strategies sum to 1.0."""
        info_sets = [
            'J.', 'Q.', 'K.',
            'J.BET', 'Q.BET', 'K.BET',
            'J.CHECK', 'Q.CHECK', 'K.CHECK'
        ]

        for info_set in info_sets:
            strategy = GTOStrategy.get_strategy(info_set)
            total_prob = sum(strategy.values())
            assert abs(total_prob - 1.0) < 0.0001, f"Strategy for {info_set} doesn't sum to 1.0"

    def test_invalid_info_set_raises_error(self):
        """Test that invalid info sets raise errors."""
        with pytest.raises(ValueError):
            GTOStrategy.get_strategy('J.INVALID')

        with pytest.raises(ValueError):
            GTOStrategy.get_strategy('X.')

    def test_expected_values_exist(self):
        """Test that expected values are defined."""
        info_sets = ['J.', 'Q.', 'K.', 'J.BET', 'Q.BET', 'K.BET']

        for info_set in info_sets:
            ev = GTOStrategy.get_expected_value(info_set)
            assert isinstance(ev, (int, float))  # Accept both int and float

    def test_king_has_positive_ev(self):
        """Test that King has positive expected value."""
        ev = GTOStrategy.get_expected_value('K.')
        assert ev > 0  # King should have positive EV

    def test_jack_has_negative_ev(self):
        """Test that Jack has negative expected value."""
        ev = GTOStrategy.get_expected_value('J.')
        assert ev < 0  # Jack should have negative EV

    def test_strategy_returns_dict(self):
        """Test that get_strategy returns a dictionary."""
        strategy = GTOStrategy.get_strategy('K.')
        assert isinstance(strategy, dict)
        assert len(strategy) > 0

    def test_strategy_values_are_probabilities(self):
        """Test that all strategy values are valid probabilities."""
        info_sets = [
            'J.', 'Q.', 'K.',
            'J.BET', 'Q.BET', 'K.BET',
            'J.CHECK', 'Q.CHECK', 'K.CHECK'
        ]

        for info_set in info_sets:
            strategy = GTOStrategy.get_strategy(info_set)
            for action, prob in strategy.items():
                assert 0.0 <= prob <= 1.0, f"Invalid probability {prob} for {action} in {info_set}"
