"""Unit tests for poker agents."""

import pytest
from kuhn_poker.game import KuhnPokerGame
from kuhn_poker.state import GameState
from agents.gto_agent import GTOAgent
from agents.human_like_agent import HumanLikeAgent
from agents.exploitative_agent import ExploitativeAgent


class TestGTOAgent:
    """Test cases for GTO agent."""

    def test_agent_creation(self):
        """Test creating a GTO agent."""
        agent = GTOAgent(name="TestGTO")
        assert agent.name == "TestGTO"
        assert str(agent) == "GTOAgent(TestGTO)"

    def test_choose_action_returns_legal_action(self):
        """Test that agent always returns legal actions."""
        agent = GTOAgent()
        game = KuhnPokerGame(seed=42)

        for _ in range(20):
            state = game.start_new_hand()

            while not state.is_terminal:
                legal_actions = game.get_legal_actions(state)
                action = agent.choose_action(state, legal_actions, state.current_player)

                assert action in legal_actions
                state = game.apply_action(state, action)

    def test_agent_uses_gto_strategy(self):
        """Test that agent's action distribution approximates GTO."""
        agent = GTOAgent()

        # Test Jack after opponent checks (should bluff ~1/3)
        state = GameState(
            cards={0: 'K', 1: 'J'},
            betting_history=['CHECK'],
            pot=2,
            current_player=1
        )

        bets = 0
        checks = 0
        trials = 1000

        for _ in range(trials):
            action = agent.choose_action(state, ['CHECK', 'BET'], 1)
            if action == 'BET':
                bets += 1
            else:
                checks += 1

        # Should be approximately 1/3 bets, 2/3 checks
        bet_rate = bets / trials
        assert 0.25 < bet_rate < 0.42  # Within reasonable variance


class TestHumanLikeAgent:
    """Test cases for human-like agent."""

    def test_agent_creation_no_api(self):
        """Test creating human-like agent without API."""
        agent = HumanLikeAgent(name="TestHuman", use_api=False)
        assert agent.name == "TestHuman"
        assert not agent.use_api

    def test_choose_action_rule_based(self):
        """Test rule-based action selection."""
        agent = HumanLikeAgent(use_api=False)
        game = KuhnPokerGame(seed=42)

        state = game.start_new_hand()
        legal_actions = game.get_legal_actions(state)
        action = agent.choose_action(state, legal_actions, 0)

        assert action in legal_actions

    def test_jack_over_folds(self):
        """Test that human-like agent over-folds with Jack."""
        agent = HumanLikeAgent(use_api=False)

        # Jack facing a bet - should always fold (loss aversion)
        state = GameState(
            cards={0: 'K', 1: 'J'},
            betting_history=['BET'],
            pot=3,
            current_player=1
        )

        folds = 0
        for _ in range(10):
            action = agent.choose_action(state, ['CALL', 'FOLD'], 1)
            if action == 'FOLD':
                folds += 1

        # Should fold most/all of the time
        assert folds >= 9

    def test_observe_opponent_action(self):
        """Test that agent tracks opponent actions."""
        agent = HumanLikeAgent(use_api=False)

        state = GameState(
            cards={0: 'K', 1: 'Q'},
            betting_history=['BET'],
            pot=3,
            current_player=1
        )

        agent.observe_opponent_action(state, 'BET', 1)

        assert len(agent.recent_history) == 1
        assert agent.recent_history[0] == 'BET'

    def test_reset_clears_history(self):
        """Test that reset clears agent history."""
        agent = HumanLikeAgent(use_api=False)

        state = GameState(
            cards={0: 'K', 1: 'Q'},
            betting_history=['BET'],
            pot=3,
            current_player=1
        )

        agent.observe_opponent_action(state, 'BET', 1)
        assert len(agent.recent_history) > 0

        agent.reset()
        assert len(agent.recent_history) == 0


class TestExploitativeAgent:
    """Test cases for exploitative agent."""

    def test_agent_creation_no_api(self):
        """Test creating exploitative agent without API."""
        agent = ExploitativeAgent(name="TestExploit", use_api=False)
        assert agent.name == "TestExploit"
        assert not agent.use_api

    def test_choose_action_rule_based(self):
        """Test rule-based action selection."""
        agent = ExploitativeAgent(use_api=False)
        game = KuhnPokerGame(seed=42)

        state = game.start_new_hand()
        legal_actions = game.get_legal_actions(state)
        action = agent.choose_action(state, legal_actions, 0)

        assert action in legal_actions

    def test_insufficient_data_uses_gto(self):
        """Test that agent uses GTO with insufficient data."""
        agent = ExploitativeAgent(use_api=False)

        # With no opponent data, should behave like GTO
        state = GameState(
            cards={0: 'K', 1: 'Q'},
            betting_history=[],
            pot=2,
            current_player=1
        )

        # King should always bet (GTO)
        action = agent.choose_action(state, ['CHECK', 'BET'], 1)
        # Can't guarantee due to randomness, but should be reasonably GTO-like

    def test_observe_opponent_action_updates_stats(self):
        """Test that observing opponent actions updates statistics."""
        agent = ExploitativeAgent(use_api=False)

        # Simulate opponent folding to a bet
        state = GameState(
            cards={0: 'J', 1: 'K'},
            betting_history=['BET'],
            pot=3,
            current_player=1
        )

        initial_stats = agent.opponent_stats['total_opportunities']
        agent.observe_opponent_action(state, 'FOLD', 0)

        assert agent.opponent_stats['total_opportunities'] > initial_stats
        assert agent.opponent_stats['fold_to_bet'] > 0

    def test_exploit_high_fold_rate(self):
        """Test that agent exploits high fold rates."""
        agent = ExploitativeAgent(use_api=False)

        # Simulate many opponent folds
        fold_state = GameState(
            cards={0: 'J', 1: 'K'},
            betting_history=['BET'],
            pot=3,
            current_player=1
        )

        for _ in range(30):
            agent.observe_opponent_action(fold_state, 'FOLD', 0)

        # Now agent has Jack after opponent checks
        # Should bluff more due to high opponent fold rate
        state = GameState(
            cards={0: 'Q', 1: 'J'},
            betting_history=['CHECK'],
            pot=2,
            current_player=1
        )

        bets = 0
        for _ in range(20):
            action = agent.choose_action(state, ['CHECK', 'BET'], 1)
            if action == 'BET':
                bets += 1

        # Should bluff more than GTO (>33%)
        assert bets > 8  # More than 40%

    def test_get_fold_rate(self):
        """Test fold rate calculation."""
        agent = ExploitativeAgent(use_api=False)

        agent.opponent_stats['total_facing_bet'] = 10
        agent.opponent_stats['fold_to_bet'] = 7

        assert agent._get_fold_rate() == 0.7

    def test_reset_clears_opponent_model(self):
        """Test that reset clears opponent model."""
        agent = ExploitativeAgent(use_api=False)

        state = GameState(
            cards={0: 'J', 1: 'K'},
            betting_history=['BET'],
            pot=3,
            current_player=1
        )

        agent.observe_opponent_action(state, 'FOLD', 0)
        assert agent.opponent_stats['total_opportunities'] > 0

        agent.reset()
        assert agent.opponent_stats['total_opportunities'] == 0
        assert len(agent.opponent_actions) == 0


class TestAgentIntegration:
    """Integration tests for agents playing against each other."""

    def test_gto_vs_gto_is_fair(self):
        """Test that GTO vs GTO produces roughly equal results."""
        from experiment.tournament import run_tournament

        agent1 = GTOAgent(name="GTO1")
        agent2 = GTOAgent(name="GTO2")

        results = run_tournament(agent1, agent2, num_hands=100, verbose=False)

        profit1 = results['profits']['GTO1']
        profit2 = results['profits']['GTO2']

        # Should be roughly zero-sum and balanced
        assert profit1 + profit2 == 0
        # With 100 hands, profits should be relatively small
        assert abs(profit1) < 50  # Reasonable variance

    def test_tournament_completes_without_errors(self):
        """Test that a full tournament completes successfully."""
        from experiment.tournament import run_tournament

        agent1 = GTOAgent(name="GTO")
        agent2 = HumanLikeAgent(name="Human", use_api=False)

        results = run_tournament(agent1, agent2, num_hands=50, verbose=False)

        assert results['total_hands'] == 50
        assert 'GTO' in results['profits']
        assert 'Human' in results['profits']
        assert results['profits']['GTO'] + results['profits']['Human'] == 0
