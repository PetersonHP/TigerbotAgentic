"""Unit tests for Kuhn Poker game engine."""

import pytest
from kuhn_poker.game import KuhnPokerGame
from kuhn_poker.state import GameState


class TestKuhnPokerGame:
    """Test cases for the Kuhn Poker game engine."""

    def test_deal_cards(self):
        """Test that cards are dealt correctly."""
        game = KuhnPokerGame(seed=42)
        cards = game.deal_cards()

        assert len(cards) == 2
        assert 0 in cards and 1 in cards
        assert cards[0] in ['J', 'Q', 'K']
        assert cards[1] in ['J', 'Q', 'K']
        assert cards[0] != cards[1]  # Different cards

    def test_start_new_hand(self):
        """Test starting a new hand."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        assert isinstance(state, GameState)
        assert len(state.cards) == 2
        assert state.pot == 2  # Both players ante
        assert state.current_player == 0
        assert not state.is_terminal
        assert len(state.betting_history) == 0

    def test_legal_actions_first_action(self):
        """Test legal actions for first action."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        legal = game.get_legal_actions(state)
        assert set(legal) == {'CHECK', 'BET'}

    def test_legal_actions_after_check(self):
        """Test legal actions after opponent checks."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # Player 0 checks
        state = game.apply_action(state, 'CHECK')
        legal = game.get_legal_actions(state)
        assert set(legal) == {'CHECK', 'BET'}

    def test_legal_actions_after_bet(self):
        """Test legal actions after opponent bets."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # Player 0 bets
        state = game.apply_action(state, 'BET')
        legal = game.get_legal_actions(state)
        assert set(legal) == {'CALL', 'FOLD'}

    def test_check_check_showdown(self):
        """Test check-check leads to showdown."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # Both players check
        state = game.apply_action(state, 'CHECK')
        state = game.apply_action(state, 'CHECK')

        assert state.is_terminal
        assert state.pot == 2
        assert state.payoffs is not None

    def test_bet_fold(self):
        """Test bet-fold sequence."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # Player 0 bets, Player 1 folds
        state = game.apply_action(state, 'BET')
        state = game.apply_action(state, 'FOLD')

        assert state.is_terminal
        assert state.pot == 3  # 2 antes + 1 bet
        # Player 0 should win
        assert state.payoffs[0] > 0
        assert state.payoffs[1] < 0

    def test_bet_call_showdown(self):
        """Test bet-call leads to showdown."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # Player 0 bets, Player 1 calls
        state = game.apply_action(state, 'BET')
        state = game.apply_action(state, 'CALL')

        assert state.is_terminal
        assert state.pot == 4  # 2 antes + 2 bets
        assert state.payoffs is not None

    def test_check_bet_fold(self):
        """Test check-bet-fold sequence."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # Player 0 checks, Player 1 bets, Player 0 folds
        state = game.apply_action(state, 'CHECK')
        state = game.apply_action(state, 'BET')
        state = game.apply_action(state, 'FOLD')

        assert state.is_terminal
        # Player 1 should win
        assert state.payoffs[0] < 0
        assert state.payoffs[1] > 0

    def test_check_bet_call(self):
        """Test check-bet-call sequence."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # Player 0 checks, Player 1 bets, Player 0 calls
        state = game.apply_action(state, 'CHECK')
        state = game.apply_action(state, 'BET')
        state = game.apply_action(state, 'CALL')

        assert state.is_terminal
        assert state.pot == 4
        assert state.payoffs is not None

    def test_showdown_winner(self):
        """Test that highest card wins at showdown."""
        game = KuhnPokerGame()

        # Manually create state with known cards
        state = GameState(
            cards={0: 'K', 1: 'J'},
            betting_history=[],
            pot=2,
            current_player=0
        )

        # Both check - K should win
        state = game.apply_action(state, 'CHECK')
        state = game.apply_action(state, 'CHECK')

        assert state.is_terminal
        assert state.payoffs[0] > 0  # King wins
        assert state.payoffs[1] < 0

    def test_payoffs_sum_to_zero(self):
        """Test that payoffs are zero-sum."""
        game = KuhnPokerGame(seed=42)

        for _ in range(10):
            state = game.start_new_hand()

            # Play random game
            while not state.is_terminal:
                legal = game.get_legal_actions(state)
                action = legal[0]  # Just take first action
                state = game.apply_action(state, action)

            # Check zero-sum
            assert state.payoffs[0] + state.payoffs[1] == 0

    def test_invalid_action_raises_error(self):
        """Test that invalid actions raise errors."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # CALL is not legal as first action
        with pytest.raises(ValueError):
            game.apply_action(state, 'CALL')

        # FOLD is not legal as first action
        with pytest.raises(ValueError):
            game.apply_action(state, 'FOLD')

    def test_player_alternation(self):
        """Test that players alternate correctly."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        assert state.current_player == 0

        state = game.apply_action(state, 'CHECK')
        if not state.is_terminal:
            assert state.current_player == 1

    def test_pot_updates(self):
        """Test that pot is updated correctly."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        assert state.pot == 2  # Initial antes

        state = game.apply_action(state, 'BET')
        assert state.pot == 3  # 2 antes + 1 bet

        state = game.apply_action(state, 'CALL')
        assert state.pot == 4  # 2 antes + 2 bets

    def test_get_payoff(self):
        """Test getting payoff from terminal state."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        # Play to terminal
        state = game.apply_action(state, 'CHECK')
        state = game.apply_action(state, 'CHECK')

        payoff_0 = game.get_payoff(state, 0)
        payoff_1 = game.get_payoff(state, 1)

        assert isinstance(payoff_0, int)
        assert isinstance(payoff_1, int)
        assert payoff_0 + payoff_1 == 0

    def test_get_payoff_non_terminal_raises_error(self):
        """Test that getting payoff from non-terminal state raises error."""
        game = KuhnPokerGame(seed=42)
        state = game.start_new_hand()

        with pytest.raises(ValueError):
            game.get_payoff(state, 0)

    def test_reproducibility_with_seed(self):
        """Test that games are reproducible with same seed."""
        game1 = KuhnPokerGame(seed=123)
        game2 = KuhnPokerGame(seed=123)

        state1 = game1.start_new_hand()
        state2 = game2.start_new_hand()

        assert state1.cards == state2.cards

    def test_different_seeds_produce_different_games(self):
        """Test that different seeds produce different games."""
        game1 = KuhnPokerGame(seed=123)
        game2 = KuhnPokerGame(seed=456)

        cards1 = [game1.deal_cards() for _ in range(10)]
        cards2 = [game2.deal_cards() for _ in range(10)]

        # Highly unlikely to be identical
        assert cards1 != cards2


class TestGameState:
    """Test cases for GameState class."""

    def test_game_state_creation(self):
        """Test creating a game state."""
        state = GameState(
            cards={0: 'K', 1: 'Q'},
            betting_history=['CHECK', 'BET'],
            pot=3,
            current_player=0
        )

        assert state.cards == {0: 'K', 1: 'Q'}
        assert state.betting_history == ['CHECK', 'BET']
        assert state.pot == 3
        assert state.current_player == 0
        assert not state.is_terminal

    def test_get_betting_string(self):
        """Test getting betting history as string."""
        state = GameState(
            cards={0: 'K', 1: 'Q'},
            betting_history=['CHECK', 'BET', 'CALL'],
            pot=4,
            current_player=0
        )

        assert state.get_betting_string() == 'CHECKBETCALL'

    def test_get_info_set(self):
        """Test getting information set string."""
        state = GameState(
            cards={0: 'K', 1: 'Q'},
            betting_history=['BET'],
            pot=3,
            current_player=1
        )

        # Player 0 has K facing empty history (already acted)
        assert state.get_info_set(0) == 'K.BET'

        # Player 1 has Q facing BET
        assert state.get_info_set(1) == 'Q.BET'

    def test_str_representation(self):
        """Test string representation."""
        state = GameState(
            cards={0: 'K', 1: 'Q'},
            betting_history=['CHECK'],
            pot=2,
            current_player=1
        )

        str_repr = str(state)
        assert 'pot=2' in str_repr
        assert 'CHECK' in str_repr
        assert 'player=1' in str_repr
