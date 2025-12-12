# Kuhn Poker: LLM Agents with Opponent Modeling

An experimental framework testing whether **Theory of Mind (opponent modeling)** beats pure optimization against boundedly rational players, using LLM-based poker agents playing Kuhn Poker.

## Project Overview

This project implements three distinct poker agents to test cognitive science hypotheses:

1. **GTO Agent**: Pure game theory optimal strategy (baseline)
2. **Human-Like Agent**: Simulates human cognitive biases (loss aversion, pattern seeking, overconfidence)
3. **Exploitative Agent**: Uses opponent modeling with episodic memory (CoALA-inspired architecture)

### Research Question

**Does Theory of Mind (opponent modeling) beat pure optimization against boundedly rational agents?**

## What is Kuhn Poker?

Kuhn Poker is the simplest non-trivial poker game:

- **2 players**, **3 cards** (K, Q, J)
- Each player antes **1 chip**
- Each player gets **1 card** face down
- **One betting round** (Player 0 acts first)
  - Actions: **CHECK** or **BET** (1 chip)
  - If CHECK → CHECK: Showdown
  - If CHECK → BET: CALL or FOLD
  - If BET: CALL or FOLD
- **Highest card wins** at showdown

### Why Kuhn Poker?

- ✅ Optimal (GTO) strategy is mathematically known
- ✅ Small state space (~12 decision points)
- ✅ Still exhibits bluffing, value betting, and exploitability
- ✅ Perfect testbed for cognitive strategies

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd TigerbotAgentic

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Option 1: With LLM Agents (Requires API Key)

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"  # Linux/Mac
# or
set ANTHROPIC_API_KEY=your-api-key-here  # Windows

# Run full experiment (1000 hands each)
python main.py --hands 1000 --verbose

# Run specific matchup
python main.py --matchup exploit_vs_human --hands 500 --verbose --plot
```

### Option 2: Without API (Rule-Based Agents)

```bash
# Run without LLM (uses rule-based fallback logic)
python main.py --hands 1000 --no-api --verbose
```

## Project Structure

```
kuhn-poker-coala/
├── kuhn_poker/              # Core game engine
│   ├── game.py              # Kuhn Poker rules implementation
│   ├── state.py             # Game state representation
│   └── gto_strategy.py      # Optimal strategy
├── agents/                  # Agent implementations
│   ├── base_agent.py        # Abstract agent class
│   ├── gto_agent.py         # Game theory optimal agent
│   ├── human_like_agent.py  # Human biases agent
│   └── exploitative_agent.py # Opponent modeling agent
├── experiment/              # Experiment infrastructure
│   ├── tournament.py        # Tournament runner
│   ├── logger.py            # Data logging
│   └── analyzer.py          # Statistical analysis
├── prompts/                 # LLM prompts
├── results/                 # Output directory (created at runtime)
├── tests/                   # Unit tests
├── main.py                  # Main entry point
└── requirements.txt
```

## Agents

### 1. GTO Agent (Baseline)

Pure algorithmic implementation of Nash equilibrium strategy:

- **Jack**: Check/fold, bluff 1/3 when checked to
- **Queen**: Check/call, never bet
- **King**: Always bet, always call

**Exploitability**: Zero (unexploitable in expectation)

### 2. Human-Like Agent (Bounded Rationality)

Simulates human cognitive biases:

- **Loss Aversion**: Over-folds to avoid losing chips
- **Pattern Seeking**: Adjusts to recent opponent behavior
- **Overconfidence**: Makes hero calls/bluffs
- **Probability Errors**: Misestimates hand strength

**Implementation**: Claude API with temperature=1.0 for variance

### 3. Exploitative Agent (Opponent Modeling)

CoALA-inspired cognitive architecture:

- **Working Memory**: Current game state
- **Episodic Memory**: Opponent action history (last 100 actions)
- **Procedural Knowledge**: Exploitation rules

**Strategies**:
- If opponent folds >60% → Bluff more with Jack
- If opponent bets >40% → Call lighter with Queen
- If opponent calls >70% → Only bet for value
- Default to GTO if insufficient data

**Implementation**: Claude API with temperature=0.7

## Usage Examples

### Run Single Matchup

```bash
python main.py --matchup gto_vs_human --hands 500 --verbose
```

### Run All Matchups with Plots

```bash
python main.py --hands 1000 --plot --verbose
```

### Custom API Key

```bash
python main.py --api-key sk-ant-xxxxx --hands 100
```

## Output

Results are saved to `results/` directory:

- **JSON logs**: Full hand history with actions and reasoning
- **Summary stats**: Win rates, action frequencies, confidence intervals
- **Plots** (if --plot enabled):
  - Cumulative profit over time
  - Action frequency comparison
  - Profit distribution
  - Win rate by card

## Example Output

```
======================================================================
TOURNAMENT SUMMARY: Exploitative_vs_HumanLike
======================================================================

Total Hands: 1000

RESULTS:
  Exploitative: +145 chips (+14.50 per 100 hands)
  HumanLike: -145 chips (-14.50 per 100 hands)

CONFIDENCE INTERVALS (95%):
  Exploitative: [0.11, 0.18] per hand
  HumanLike: [-0.18, -0.11] per hand

ACTION FREQUENCIES:
  Exploitative:
    CHECK: 425 (42.5%)
    BET: 312 (31.2%)
    CALL: 163 (16.3%)
    FOLD: 100 (10.0%)
```

## Hypotheses & Expected Results

### H1: Exploitative > GTO vs Human-Like
**Expected**: Exploitative agent outperforms GTO by **+50 to +100 chips/100 hands**

### H2: GTO ≈ Exploitative (vs each other)
**Expected**: Near-zero profit (both play optimally)

### H3: GTO > Human-Like
**Expected**: GTO exploits biases passively (**+20 to +50 chips/100 hands**)

## Research Implications

### Cognitive Science Connection

This experiment tests:

1. **CoALA Framework**: Do cognitive architectures (memory, reasoning) improve strategic AI?
2. **Theory of Mind**: Is opponent modeling more valuable than pure optimization?
3. **Bounded Rationality**: How do human biases create exploitable patterns?
4. **Adaptive Intelligence**: When does human-like cognition outperform optimization?

### Paper Framing

**"Theory of Mind vs Optimization: When Does Opponent Modeling Improve Strategic Play?"**

- First direct comparison of GTO vs ToM in controlled poker setting
- Quantifies value of human-like cognition in strategic games
- Tests evolutionary adaptiveness of cognitive architecture

## Cost Estimates

**API Usage** (1000 hands × 3 matchups):
- ~3000 hands × 2 LLM calls/hand × 500 tokens/call = ~3M tokens
- Cost: **$30-50** using Claude 3.5 Sonnet

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black .

# Type checking
mypy kuhn_poker/ agents/ experiment/
```

## Future Extensions

- [ ] Human validation UI (web interface)
- [ ] Ablation study (remove episodic memory)
- [ ] Sensitivity analysis (vary bias strength)
- [ ] Meta-learning (pre-train on specific opponents)
- [ ] Extended game variants (Leduc Poker, Limit Hold'em)

## Citation

If you use this code in research, please cite:

```bibtex
@software{kuhn_poker_tom,
  title = {Kuhn Poker: LLM Agents with Opponent Modeling},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/kuhn-poker-coala}
}
```

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Based on Kuhn (1950) poker game theory
- Inspired by Sumers et al. (2023) CoALA cognitive architecture
- Uses Anthropic's Claude API for LLM agents

## References

- Kuhn, H. W. (1950). "Simplified two-person poker." Contributions to the Theory of Games.
- Sumers et al. (2023). "Cognitive Architectures for Language Agents (CoALA)."
- Kahneman & Tversky (1979). "Prospect Theory: An Analysis of Decision under Risk."

---

**Questions?** Open an issue or contact [your-email@example.com]