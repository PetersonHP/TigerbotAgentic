"""Main entry point for Kuhn Poker experiments.

Usage:
    python main.py --hands 1000
    python main.py --hands 100 --verbose

Set your API key in .env file or ANTHROPIC_API_KEY environment variable.
"""

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from experiment.tournament import run_matchup
from experiment.analyzer import analyze_results, plot_results, ResultsAnalyzer

# Load environment variables from .env file
load_dotenv()


def main():
    parser = argparse.ArgumentParser(description='Run Kuhn Poker agent tournaments')

    parser.add_argument('--hands', type=int, default=1000,
                       help='Number of hands per matchup (default: 1000)')

    parser.add_argument('--api-key', type=str, default=None,
                       help='Anthropic API key (optional if set in .env or ANTHROPIC_API_KEY env var)')

    parser.add_argument('--verbose', action='store_true',
                       help='Show progress bars and detailed output')

    parser.add_argument('--matchup', type=str, default='all',
                       choices=['all', 'gto_vs_human', 'exploit_vs_human', 'gto_vs_exploit'],
                       help='Which matchup to run (default: all)')

    parser.add_argument('--plot', action='store_true',
                       help='Generate plots (requires matplotlib)')

    parser.add_argument('--output-dir', type=str, default='results',
                       help='Output directory for results (default: results)')

    args = parser.parse_args()

    # Get API key from arguments, environment, or .env file
    api_key = args.api_key or os.environ.get('ANTHROPIC_API_KEY')

    if not api_key:
        print("\n⚠️  Error: No API key provided.")
        print("   Please set ANTHROPIC_API_KEY in your .env file or environment variable.")
        print("   Or provide --api-key argument.\n")
        return

    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("KUHN POKER AGENT TOURNAMENT")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Hands per matchup: {args.hands}")
    print(f"  API: Enabled (using Claude API)")
    print(f"  Output directory: {args.output_dir}")
    print(f"  Matchup: {args.matchup}")
    print()

    # Define matchups
    all_matchups = {
        'gto_vs_human': ('gto', 'human_like'),
        'exploit_vs_human': ('exploitative', 'human_like'),
        'gto_vs_exploit': ('gto', 'exploitative')
    }

    # Select matchups to run
    if args.matchup == 'all':
        matchups_to_run = all_matchups
    else:
        matchups_to_run = {args.matchup: all_matchups[args.matchup]}

    # Run tournaments
    results = {}
    for matchup_name, (agent1_type, agent2_type) in matchups_to_run.items():
        print(f"\n{'='*70}")
        print(f"Running: {matchup_name}")
        print(f"{'='*70}\n")

        try:
            result = run_matchup(
                agent1_type=agent1_type,
                agent2_type=agent2_type,
                num_hands=args.hands,
                api_key=api_key,
                verbose=args.verbose
            )
            results[matchup_name] = result

        except Exception as e:
            print(f"Error running {matchup_name}: {e}")
            import traceback
            traceback.print_exc()

    # Analyze results
    if results:
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)

        analyze_results(results, output_dir=args.output_dir)

        # Generate plots if requested
        if args.plot:
            print("\nGenerating plots...")
            analyzer = ResultsAnalyzer(args.output_dir)

            for matchup_name, result in results.items():
                try:
                    # Reconstruct tournament data for analysis
                    tournament_data = {
                        'matchup': matchup_name,
                        'hands': result['logger'].get_hands(),
                        'profits': result['profits'],
                        'total_hands': result['total_hands']
                    }

                    stats = analyzer.analyze_tournament(tournament_data)

                    plot_path = Path(args.output_dir) / f"{matchup_name}_plot.png"
                    plot_results(stats, output_path=str(plot_path))

                except Exception as e:
                    print(f"Warning: Could not generate plot for {matchup_name}: {e}")

    print("\n" + "="*70)
    print("EXPERIMENT COMPLETE")
    print("="*70)
    print(f"\nResults saved to: {args.output_dir}/")
    print()


if __name__ == '__main__':
    main()
