"""Quick demo script to test the Kuhn Poker implementation."""

from kuhn_poker.game import KuhnPokerGame
from agents.gto_agent import GTOAgent
from agents.human_like_agent import HumanLikeAgent
from experiment.tournament import play_hand


def main():
    print("="*70)
    print("KUHN POKER DEMO")
    print("="*70)

    # Initialize game and agents
    game = KuhnPokerGame(seed=42)
    gto_agent = GTOAgent(name="GTO")
    human_agent = HumanLikeAgent(name="Human")

    agents = {0: gto_agent, 1: human_agent}

    print("\nPlaying 5 demo hands...\n")

    total_profits = {0: 0, 1: 0}

    for i in range(5):
        print(f"\n{'-'*70}")
        print(f"Hand {i+1}")
        print(f"{'-'*70}")

        result = play_hand(game, agents, i, verbose=True)

        for pos, payoff in result['payoffs'].items():
            total_profits[pos] += payoff

    print(f"\n{'='*70}")
    print("DEMO COMPLETE")
    print(f"{'='*70}")
    print(f"\nTotal Results:")
    print(f"  {gto_agent.name}: {total_profits[0]:+d} chips")
    print(f"  {human_agent.name}: {total_profits[1]:+d} chips")
    print()


if __name__ == '__main__':
    main()
