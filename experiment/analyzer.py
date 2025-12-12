"""Statistical analysis and visualization for tournament results."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
from collections import defaultdict


class ResultsAnalyzer:
    """Analyzes tournament results and generates statistics."""

    def __init__(self, results_dir: str = "results"):
        """Initialize the analyzer.

        Args:
            results_dir: Directory containing result JSON files
        """
        self.results_dir = Path(results_dir)

    def analyze_tournament(self, tournament_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single tournament.

        Args:
            tournament_data: Tournament data dictionary

        Returns:
            Dictionary of analysis results
        """
        hands = tournament_data.get('hands', [])
        profits = tournament_data.get('profits', {})
        total_hands = tournament_data.get('total_hands', len(hands))

        # Calculate basic statistics
        agent_names = list(profits.keys())
        agent1, agent2 = agent_names[0], agent_names[1]

        stats = {
            'matchup': tournament_data.get('matchup', 'Unknown'),
            'total_hands': total_hands,
            'agent1': agent1,
            'agent2': agent2,
            'agent1_profit': profits.get(agent1, 0),
            'agent2_profit': profits.get(agent2, 0),
            'agent1_profit_per_100': (profits.get(agent1, 0) / total_hands * 100) if total_hands > 0 else 0,
            'agent2_profit_per_100': (profits.get(agent2, 0) / total_hands * 100) if total_hands > 0 else 0,
        }

        # Calculate action frequencies
        action_freq = self._calculate_action_frequencies(hands)
        stats['action_frequencies'] = action_freq

        # Calculate win rates by card
        card_stats = self._calculate_card_statistics(hands)
        stats['card_statistics'] = card_stats

        # Calculate confidence intervals
        if hands:
            ci = self._calculate_confidence_intervals(hands, agent1, agent2)
            stats['confidence_intervals'] = ci

        # Calculate cumulative profit over time
        cumulative = self._calculate_cumulative_profit(hands, agent1, agent2)
        stats['cumulative_profit'] = cumulative

        return stats

    def _calculate_action_frequencies(self, hands: List[Dict]) -> Dict[str, Dict[str, int]]:
        """Calculate action frequencies for each agent.

        Args:
            hands: List of hand dictionaries

        Returns:
            Dictionary of action frequencies by agent
        """
        frequencies = defaultdict(lambda: {'CHECK': 0, 'BET': 0, 'CALL': 0, 'FOLD': 0})

        for hand in hands:
            for action_data in hand.get('actions', []):
                agent = action_data.get('agent')
                action = action_data.get('action')
                if agent and action:
                    frequencies[agent][action] += 1

        return dict(frequencies)

    def _calculate_card_statistics(self, hands: List[Dict]) -> Dict[str, Dict]:
        """Calculate statistics by card.

        Args:
            hands: List of hand dictionaries

        Returns:
            Dictionary of statistics by card
        """
        card_stats = defaultdict(lambda: {'hands': 0, 'won': 0, 'profit': 0})

        for hand in hands:
            cards = hand.get('cards', {})
            payoffs = hand.get('payoffs', {})

            for pos, card in cards.items():
                pos_int = int(pos) if isinstance(pos, str) else pos
                card_stats[card]['hands'] += 1

                payoff = payoffs.get(pos_int, 0)
                if payoff > 0:
                    card_stats[card]['won'] += 1
                card_stats[card]['profit'] += payoff

        # Calculate win rates
        for card, stats in card_stats.items():
            if stats['hands'] > 0:
                stats['win_rate'] = stats['won'] / stats['hands']
                stats['avg_profit'] = stats['profit'] / stats['hands']

        return dict(card_stats)

    def _calculate_confidence_intervals(self, hands: List[Dict],
                                       agent1: str, agent2: str,
                                       confidence: float = 0.95) -> Dict:
        """Calculate confidence intervals for profit.

        Args:
            hands: List of hand dictionaries
            agent1: Name of first agent
            agent2: Name of second agent
            confidence: Confidence level (default 95%)

        Returns:
            Dictionary with confidence intervals
        """
        # Extract profits for each agent per hand
        agent1_profits = []
        agent2_profits = []

        for hand in hands:
            payoffs = hand.get('payoffs', {})
            actions = hand.get('actions', [])

            # Determine which position each agent was in
            agent_positions = {}
            for action_data in actions:
                agent = action_data.get('agent')
                pos = action_data.get('position')
                if agent and pos is not None:
                    agent_positions[agent] = pos
                    break

            # Get profits
            if agent1 in agent_positions:
                pos = agent_positions[agent1]
                agent1_profits.append(payoffs.get(pos, 0))

            if agent2 in agent_positions:
                pos = agent_positions[agent2]
                agent2_profits.append(payoffs.get(pos, 0))

        # Calculate confidence intervals
        def calc_ci(profits):
            if not profits:
                return {'mean': 0, 'std': 0, 'ci_lower': 0, 'ci_upper': 0}

            mean = np.mean(profits)
            std = np.std(profits, ddof=1) if len(profits) > 1 else 0
            n = len(profits)

            # Use t-distribution for small samples
            from scipy import stats
            t_critical = stats.t.ppf((1 + confidence) / 2, n - 1) if n > 1 else 1.96

            margin = t_critical * (std / np.sqrt(n)) if n > 0 else 0

            return {
                'mean': float(mean),
                'std': float(std),
                'ci_lower': float(mean - margin),
                'ci_upper': float(mean + margin),
                'n': n
            }

        return {
            agent1: calc_ci(agent1_profits),
            agent2: calc_ci(agent2_profits)
        }

    def _calculate_cumulative_profit(self, hands: List[Dict],
                                    agent1: str, agent2: str) -> Dict[str, List[float]]:
        """Calculate cumulative profit over time.

        Args:
            hands: List of hand dictionaries
            agent1: Name of first agent
            agent2: Name of second agent

        Returns:
            Dictionary with cumulative profit lists
        """
        cumulative = {agent1: [0], agent2: [0]}

        for hand in hands:
            payoffs = hand.get('payoffs', {})
            actions = hand.get('actions', [])

            # Determine agent positions
            agent_positions = {}
            for action_data in actions:
                agent = action_data.get('agent')
                pos = action_data.get('position')
                if agent and pos is not None:
                    agent_positions[agent] = pos

            # Update cumulative
            for agent in [agent1, agent2]:
                if agent in agent_positions:
                    pos = agent_positions[agent]
                    profit = payoffs.get(pos, 0)
                    cumulative[agent].append(cumulative[agent][-1] + profit)
                else:
                    cumulative[agent].append(cumulative[agent][-1])

        return cumulative

    def generate_summary_report(self, stats: Dict[str, Any]) -> str:
        """Generate a text summary report.

        Args:
            stats: Statistics dictionary from analyze_tournament

        Returns:
            Formatted summary string
        """
        report = []
        report.append(f"\n{'='*60}")
        report.append(f"TOURNAMENT SUMMARY: {stats['matchup']}")
        report.append(f"{'='*60}\n")

        report.append(f"Total Hands: {stats['total_hands']}")
        report.append(f"\nRESULTS:")
        report.append(f"  {stats['agent1']}: {stats['agent1_profit']:+d} chips ({stats['agent1_profit_per_100']:+.2f} per 100 hands)")
        report.append(f"  {stats['agent2']}: {stats['agent2_profit']:+d} chips ({stats['agent2_profit_per_100']:+.2f} per 100 hands)")

        # Confidence intervals
        if 'confidence_intervals' in stats:
            report.append(f"\nCONFIDENCE INTERVALS (95%):")
            for agent, ci in stats['confidence_intervals'].items():
                report.append(f"  {agent}: [{ci['ci_lower']:.2f}, {ci['ci_upper']:.2f}] per hand")

        # Action frequencies
        if 'action_frequencies' in stats:
            report.append(f"\nACTION FREQUENCIES:")
            for agent, freq in stats['action_frequencies'].items():
                total = sum(freq.values())
                if total > 0:
                    report.append(f"  {agent}:")
                    for action, count in freq.items():
                        pct = (count / total * 100) if total > 0 else 0
                        report.append(f"    {action}: {count} ({pct:.1f}%)")

        # Card statistics
        if 'card_statistics' in stats:
            report.append(f"\nCARD STATISTICS:")
            for card in ['K', 'Q', 'J']:
                if card in stats['card_statistics']:
                    cs = stats['card_statistics'][card]
                    report.append(f"  {card}: Win rate={cs.get('win_rate', 0)*100:.1f}%, Avg profit={cs.get('avg_profit', 0):.2f}")

        report.append(f"\n{'='*60}\n")

        return '\n'.join(report)


def analyze_results(results: Dict[str, Any], output_dir: str = "results") -> None:
    """Analyze tournament results and generate reports.

    Args:
        results: Dictionary of tournament results
        output_dir: Directory to save analysis output
    """
    analyzer = ResultsAnalyzer(output_dir)

    for matchup_name, tournament_data in results.items():
        print(f"\nAnalyzing {matchup_name}...")

        # Analyze
        stats = analyzer.analyze_tournament(tournament_data)

        # Generate and print summary
        summary = analyzer.generate_summary_report(stats)
        print(summary)

        # Save summary
        logger = tournament_data.get('logger')
        if logger:
            logger.save_summary(matchup_name, stats)


def plot_results(stats: Dict[str, Any], output_path: Optional[str] = None) -> None:
    """Generate plots for tournament results.

    Args:
        stats: Statistics dictionary
        output_path: Optional path to save plot
    """
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        sns.set_style("whitegrid")

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. Cumulative profit over time
        ax1 = axes[0, 0]
        cumulative = stats.get('cumulative_profit', {})
        for agent, profits in cumulative.items():
            ax1.plot(profits, label=agent, linewidth=2)
        ax1.set_xlabel('Hand Number')
        ax1.set_ylabel('Cumulative Profit (chips)')
        ax1.set_title('Cumulative Profit Over Time')
        ax1.legend()
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        ax1.grid(True, alpha=0.3)

        # 2. Action frequency comparison
        ax2 = axes[0, 1]
        action_freq = stats.get('action_frequencies', {})
        if action_freq:
            agents = list(action_freq.keys())
            actions = ['CHECK', 'BET', 'CALL', 'FOLD']

            x = np.arange(len(actions))
            width = 0.35

            for i, agent in enumerate(agents):
                freq = action_freq[agent]
                total = sum(freq.values())
                percentages = [freq.get(a, 0) / total * 100 if total > 0 else 0 for a in actions]
                ax2.bar(x + i * width, percentages, width, label=agent)

            ax2.set_xlabel('Action')
            ax2.set_ylabel('Frequency (%)')
            ax2.set_title('Action Frequency Comparison')
            ax2.set_xticks(x + width / 2)
            ax2.set_xticklabels(actions)
            ax2.legend()
            ax2.grid(True, alpha=0.3, axis='y')

        # 3. Profit distribution (box plot)
        ax3 = axes[1, 0]
        if 'confidence_intervals' in stats:
            ci_data = stats['confidence_intervals']
            agents = list(ci_data.keys())
            means = [ci_data[a]['mean'] for a in agents]
            stds = [ci_data[a]['std'] for a in agents]

            ax3.bar(agents, means, yerr=stds, capsize=5, alpha=0.7)
            ax3.set_ylabel('Mean Profit per Hand')
            ax3.set_title('Profit per Hand (with std dev)')
            ax3.axhline(y=0, color='black', linestyle='--', alpha=0.3)
            ax3.grid(True, alpha=0.3, axis='y')

        # 4. Win rate by card
        ax4 = axes[1, 1]
        card_stats = stats.get('card_statistics', {})
        if card_stats:
            cards = ['K', 'Q', 'J']
            win_rates = [card_stats.get(c, {}).get('win_rate', 0) * 100 for c in cards]

            ax4.bar(cards, win_rates, color=['gold', 'silver', 'brown'], alpha=0.7)
            ax4.set_ylabel('Win Rate (%)')
            ax4.set_title('Win Rate by Card')
            ax4.set_ylim(0, 100)
            ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {output_path}")
        else:
            plt.show()

    except ImportError:
        print("Warning: matplotlib/seaborn not available for plotting")
