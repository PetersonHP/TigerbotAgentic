"""Human-like agent with cognitive biases."""

import json
import os
import re
from typing import List, Optional
from dotenv import load_dotenv
from anthropic import Anthropic
from .base_agent import BaseAgent
from .llm_logger import LLMLogger
from kuhn_poker.state import GameState

# Load environment variables from .env file
load_dotenv()


class HumanLikeAgent(BaseAgent):
    """Agent that simulates human cognitive biases in poker play.

    This agent exhibits:
    1. Loss aversion: Fears losing chips, over-folds
    2. Pattern seeking: Sees patterns in randomness
    3. Overconfidence: Makes hero calls/bluffs
    4. Probability misestimation: Misjudges hand strength

    Uses Claude API to generate decisions with human-like reasoning.
    """

    def __init__(self, name: str = "HumanLike", api_key: Optional[str] = None):
        """Initialize the human-like agent.

        Args:
            name: Agent name
            api_key: Anthropic API key (if not provided, loads from ANTHROPIC_API_KEY env var)
        """
        super().__init__(name)
        self.recent_history = []  # Track recent hands for pattern seeking

        # Initialize LLM logger
        self.logger = LLMLogger(agent_name=name)

        # Get API key from parameter or environment variable
        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "API key required. Provide via api_key parameter or set ANTHROPIC_API_KEY environment variable."
            )
        self.client = Anthropic(api_key=api_key)

    def choose_action(self, state: GameState, legal_actions: List[str], player_position: int) -> str:
        """Choose action with human-like biases using Claude API.

        Args:
            state: Current game state
            legal_actions: List of legal actions
            player_position: This agent's position (0 or 1)

        Returns:
            Action chosen with cognitive biases
        """
        return self._choose_action_with_llm(state, legal_actions, player_position)

    def _choose_action_with_llm(self, state: GameState, legal_actions: List[str], player_position: int) -> str:
        """Choose action using Claude API.

        Args:
            state: Current game state
            legal_actions: List of legal actions
            player_position: This agent's position

        Returns:
            Action chosen by LLM
        """
        card = state.cards[player_position]
        history = state.get_betting_string()
        recent_pattern = self._format_recent_history()

        prompt = f"""You are playing Kuhn Poker with realistic human cognitive biases.

COGNITIVE BIASES TO SIMULATE:
1. Loss aversion: Fear of losing chips → fold too often
2. Pattern seeking: See patterns in randomness → adjust to recent hands
3. Overconfidence: Think you read opponent → make hero calls/bluffs
4. Probability errors: Misestimate hand strength

RULES REMINDER:
- With Jack (J): Worst card - usually check/fold, sometimes bluff if "feeling aggressive"
- With Queen (Q): Middle card - usually check/call, sometimes fold if "feeling cautious"
- With King (K): Best card - usually bet for value, sometimes trap-check if "being tricky"

CURRENT SITUATION:
- Your card: {card}
- Betting history this hand: {history if history else "You act first"}
- Legal actions: {legal_actions}
- Pot size: {state.pot} chips

RECENT OPPONENT BEHAVIOR:
{recent_pattern}

Think like a human player with biases. Choose your action and explain your reasoning.

Output ONLY valid JSON (no other text):
{{"action": "CHECK", "reasoning": "My Queen is strong but I'm scared to build a big pot", "bias_active": "loss_aversion"}}

Your response:"""

        try:
            model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
            response = self.client.messages.create(
                model=model,
                max_tokens=150,
                temperature=1.0,  # High temperature for human-like variance
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()

            # Log the conversation
            self.logger.log_conversation(
                prompt=prompt,
                response=response_text,
                model=model,
                metadata={
                    "card": card,
                    "history": history,
                    "legal_actions": legal_actions,
                    "pot": state.pot,
                    "recent_pattern": recent_pattern,
                    "temperature": 1.0,
                    "max_tokens": 150
                }
            )

            # Try to parse JSON - search for JSON object pattern
            try:
                # Find JSON object in response (handles markdown fences, extra text, etc.)
                match = re.search(r'\{.*?\}', response_text, re.DOTALL)
                if match:
                    result = json.loads(match.group(0))
                    action = result.get('action', '').upper()

                    # Validate action
                    if action in legal_actions:
                        return action
            except (json.JSONDecodeError, AttributeError):
                pass

            # Fallback to first legal action if parsing fails
            print(f"Warning: Could not parse LLM response, using first legal action")
            return legal_actions[0]

        except Exception as e:
            # Log the error
            self.logger.log_error(
                error=e,
                prompt=prompt,
                metadata={
                    "card": card,
                    "history": history,
                    "legal_actions": legal_actions
                }
            )
            print(f"Warning: LLM call failed ({e}), using first legal action")
            return legal_actions[0]

    def _format_recent_history(self) -> str:
        """Format recent hand history for pattern seeking.

        Returns:
            String describing recent opponent behavior
        """
        if not self.recent_history:
            return "No previous hands to analyze."

        # Analyze last 5 hands
        recent = self.recent_history[-5:]
        bet_count = sum(1 for h in recent if 'BET' in h)

        if bet_count >= 3:
            return f"Opponent has been aggressive (bet {bet_count}/5 recent hands)"
        elif bet_count <= 1:
            return f"Opponent has been passive (only bet {bet_count}/5 recent hands)"
        else:
            return "Opponent showing balanced play recently"

    def observe_opponent_action(self, state: GameState, action: str, player_position: int) -> None:
        """Track opponent actions for pattern seeking.

        Args:
            state: State when opponent acted
            action: Opponent's action
            player_position: This agent's position
        """
        self.recent_history.append(action)
        # Keep only last 20 actions
        if len(self.recent_history) > 20:
            self.recent_history.pop(0)

    def reset(self) -> None:
        """Reset agent history."""
        self.recent_history = []
