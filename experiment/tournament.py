"""Tournament runner for agent matchups."""

from typing import Dict, Tuple, Optional
from tqdm import tqdm
from kuhn_poker.game import KuhnPokerGame
from agents.base_agent import BaseAgent
from .logger import GameLogger


def run_tournament(agent1: BaseAgent, agent2: BaseAgent, num_hands: int,
                   verbose: bool = False, logger: Optional[GameLogger] = None) -> Dict:
    """Run a tournament between two agents.

    Agents alternate positions (P0/P1) to ensure fairness.

    Args:
        agent1: First agent
        agent2: Second agent
        num_hands: Number of hands to play
        verbose: Whether to print progress
        logger: Optional game logger

    Returns:
        Dictionary with tournament results
    """
    game = KuhnPokerGame()

    # Track profits for each agent (not position)
    profits = {agent1.name: 0, agent2.name: 0}

    # Track action frequencies
    action_counts = {
        agent1.name: {'CHECK': 0, 'BET': 0, 'CALL': 0, 'FOLD': 0},
        agent2.name: {'CHECK': 0, 'BET': 0, 'CALL': 0, 'FOLD': 0}
    }

    if logger is None:
        logger = GameLogger()

    # Progress bar
    iterator = tqdm(range(num_hands), desc=f"{agent1.name} vs {agent2.name}") if verbose else range(num_hands)

    for hand_num in iterator:
        # Alternate positions
        if hand_num % 2 == 0:
            agents = {0: agent1, 1: agent2}
        else:
            agents = {0: agent2, 1: agent1}

        # Play one hand
        hand_result = play_hand(game, agents, hand_num, verbose=False)

        # Update profits (map from position to agent name)
        for pos, payoff in hand_result['payoffs'].items():
            agent_name = agents[pos].name
            profits[agent_name] += payoff

        # Update action counts
        for action_data in hand_result['actions']:
            agent_name = action_data['agent']
            action = action_data['action']
            action_counts[agent_name][action] += 1

        # Log hand
        logger.log_hand(hand_result)

    # Calculate statistics
    results = {
        'matchup': f"{agent1.name}_vs_{agent2.name}",
        'total_hands': num_hands,
        'profits': profits,
        'profit_per_100': {
            name: (profit / num_hands * 100) for name, profit in profits.items()
        },
        'action_frequencies': action_counts,
        'logger': logger
    }

    return results


def play_hand(game: KuhnPokerGame, agents: Dict[int, BaseAgent],
              hand_num: int, verbose: bool = False) -> Dict:
    """Play a single hand of Kuhn Poker.

    Args:
        game: Kuhn poker game instance
        agents: Dictionary mapping positions to agents
        hand_num: Hand number (for logging)
        verbose: Whether to print game progress

    Returns:
        Dictionary with hand results
    """
    # Start new hand
    state = game.start_new_hand()

    if verbose:
        print(f"\n=== Hand {hand_num} ===")
        print(f"Cards: P0={state.cards[0]}, P1={state.cards[1]}")

    actions_taken = []

    # Play until terminal
    while not game.is_terminal(state):
        current_player = state.current_player
        agent = agents[current_player]

        # Get legal actions
        legal_actions = game.get_legal_actions(state)

        # Agent chooses action
        action = agent.choose_action(state, legal_actions, current_player)

        if verbose:
            print(f"P{current_player} ({agent.name}): {action}")

        # Record action
        actions_taken.append({
            'position': current_player,
            'agent': agent.name,
            'action': action,
            'card': state.cards[current_player]
        })

        # Notify opponent of action (for learning agents)
        opponent_pos = 1 - current_player
        agents[opponent_pos].observe_opponent_action(state, action, opponent_pos)

        # Apply action
        new_state = game.apply_action(state, action)

        # Notify agent of result
        agent.observe_result(state, action, new_state, current_player)

        state = new_state

    # Get payoffs
    payoffs = {0: game.get_payoff(state, 0), 1: game.get_payoff(state, 1)}

    if verbose:
        print(f"Result: P0={payoffs[0]:+d}, P1={payoffs[1]:+d}")

    # Return hand data
    return {
        'hand_id': hand_num,
        'cards': state.cards,
        'actions': actions_taken,
        'betting_history': state.betting_history,
        'payoffs': payoffs,
        'final_pot': state.pot
    }


def run_matchup(agent1_type: str, agent2_type: str, num_hands: int,
                api_key: Optional[str] = None, verbose: bool = True) -> Dict:
    """Run a matchup between two agent types.

    Args:
        agent1_type: Type of first agent ('gto', 'human_like', 'exploitative')
        agent2_type: Type of second agent
        num_hands: Number of hands to play
        api_key: Anthropic API key (for LLM agents, optional if set in .env)
        verbose: Whether to show progress

    Returns:
        Tournament results dictionary
    """
    # Import here to avoid circular imports
    from agents.gto_agent import GTOAgent
    from agents.human_like_agent import HumanLikeAgent
    from agents.exploitative_agent import ExploitativeAgent

    # Create agents
    agent_map = {
        'gto': lambda: GTOAgent(name="GTO"),
        'human_like': lambda: HumanLikeAgent(name="HumanLike", api_key=api_key),
        'exploitative': lambda: ExploitativeAgent(name="Exploitative", api_key=api_key)
    }

    if agent1_type not in agent_map:
        raise ValueError(f"Unknown agent type: {agent1_type}")
    if agent2_type not in agent_map:
        raise ValueError(f"Unknown agent type: {agent2_type}")

    agent1 = agent_map[agent1_type]()
    agent2 = agent_map[agent2_type]()

    # Create logger
    logger = GameLogger()

    # Run tournament
    results = run_tournament(agent1, agent2, num_hands, verbose=verbose, logger=logger)

    # Save results
    matchup_name = f"{agent1.name}_vs_{agent2.name}"
    agent_names = {0: agent1.name, 1: agent2.name}
    profits_by_pos = {
        0: results['profits'].get(agent1.name, 0),
        1: results['profits'].get(agent2.name, 0)
    }

    logger.save_tournament(matchup_name, agent_names, num_hands, profits_by_pos)

    return results
