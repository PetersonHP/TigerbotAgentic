# Kuhn Poker - Quick Start Guide

## ✅ Project Complete!

All components are implemented, tested, and ready to use.

## Test Results
```
56/56 tests PASSED ✓
- Game engine: 22 tests
- GTO strategy: 16 tests
- Agents: 18 tests
```

## Run Demo (No API Required)

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Run demo
python demo.py
```

## Run Experiments

### 1. Quick Test (100 hands, no API)
```bash
python main.py --hands 100 --no-api --verbose
```

### 2. Full Experiment (1000 hands, with Claude API)
```bash
# Set your API key
export ANTHROPIC_API_KEY=your-key-here  # Linux/Mac
set ANTHROPIC_API_KEY=your-key-here     # Windows

# Run all matchups
python main.py --hands 1000 --verbose --plot
```

### 3. Single Matchup
```bash
python main.py --matchup exploit_vs_human --hands 500 --verbose
```

## What's Built

### Core Components
- ✅ Kuhn Poker game engine (fully functional)
- ✅ GTO strategy (Nash equilibrium)
- ✅ 3 agents (GTO, Human-like, Exploitative)
- ✅ Tournament infrastructure
- ✅ Statistical analysis
- ✅ Visualization pipeline

### Agent Capabilities

**GTO Agent**
- Pure optimal play
- Unexploitable strategy
- Baseline for comparison

**Human-Like Agent**
- Loss aversion (over-folds)
- Pattern seeking
- Overconfidence
- Works with/without API

**Exploitative Agent**
- Episodic memory (tracks opponent)
- Statistical analysis
- Adaptive exploitation
- Falls back to GTO when uncertain

### Files Created

```
TigerbotAgentic/
├── kuhn_poker/          # Game engine (3 files)
├── agents/              # Agents (4 files)
├── experiment/          # Infrastructure (3 files)
├── tests/               # Tests (4 files)
├── prompts/             # LLM prompts (3 files)
├── notebooks/           # Analysis (1 file)
├── main.py              # CLI interface
├── demo.py              # Quick demo
├── requirements.txt     # Dependencies
├── README.md            # Full documentation
└── .gitignore           # Git config
```

## Research Hypotheses to Test

### H1: Exploitative > GTO vs Human-Like
Expected: +50 to +100 chips per 100 hands

### H2: GTO ≈ Exploitative (vs each other)
Expected: Near-zero profit

### H3: GTO > Human-Like
Expected: +20 to +50 chips per 100 hands

## Next Steps

1. **Test locally** (5 min)
   ```bash
   python demo.py
   python main.py --hands 100 --no-api --verbose
   ```

2. **Run small experiment** (30 min)
   ```bash
   python main.py --hands 500 --no-api --verbose
   ```

3. **Full experiment with API** (6-8 hours)
   ```bash
   python main.py --hands 1000 --api-key YOUR_KEY --verbose --plot
   ```

4. **Analyze results**
   - Open `results/` folder
   - View JSON logs
   - Check plots
   - Open Jupyter notebook

## Cost Breakdown

- **No API mode**: $0
- **100 hands**: ~$1-2
- **1000 hands (3 matchups)**: ~$30-50
- **Extended (10k hands)**: ~$300-500

## Support

- Run tests: `pytest tests/ -v`
- Check code: `black . && mypy .`
- View docs: Open README.md

---

**Status: READY TO RUN** ✓

All code is production-quality with type hints, docstrings, and comprehensive tests!
