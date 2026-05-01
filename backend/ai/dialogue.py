from enum import Enum
from typing import Optional


class DialogueState(str, Enum):
    REVIEW = "review"
    HEURISTIC = "heuristic"
    RECTIFY = "rectify"
    SUMMARIZE = "summarize"


class HintLevel(int, Enum):
    L0 = 0  # Pure Socratic
    L1 = 1  # Guided Hint
    L2 = 2  # Scaffolded Hint
    L3 = 3  # Full Worked Example


class DialogueStateMachine:
    """Manages Socratic dialogue state transitions"""

    def __init__(self):
        self.current_state = DialogueState.REVIEW
        self.fail_count = 0
        self.hint_level = HintLevel.L0
        self.max_failures = 3
        self.max_rectify_loops = 3

    def transition_to_heuristic(self) -> None:
        """Transition from REVIEW to HEURISTIC state"""
        if self.current_state == DialogueState.REVIEW:
            self.current_state = DialogueState.HEURISTIC
            self.fail_count = 0

    def transition_to_rectify(self) -> None:
        """Transition to RECTIFY state when student makes an error"""
        if self.current_state in [DialogueState.HEURISTIC, DialogueState.REVIEW]:
            self.current_state = DialogueState.RECTIFY
            self.fail_count += 1
        elif self.current_state == DialogueState.RECTIFY:
            # Already in rectify, just increment failure count
            self.fail_count += 1

    def transition_to_summarize(self) -> None:
        """Transition to SUMMARIZE state when student solves the problem"""
        self.current_state = DialogueState.SUMMARIZE
        self.fail_count = 0

    def transition_back_to_heuristic(self) -> None:
        """Transition back to HEURISTIC after rectification"""
        if self.current_state == DialogueState.RECTIFY:
            self.current_state = DialogueState.HEURISTIC

    def should_escalate_hint(self) -> bool:
        """Check if hint level should be escalated"""
        return (
            self.fail_count >= 2 and
            self.hint_level < HintLevel.L3 and
            self.current_state == DialogueState.RECTIFY
        )

    def escalate_hint(self) -> HintLevel:
        """Escalate hint level"""
        if self.hint_level < HintLevel.L3:
            self.hint_level = HintLevel(self.hint_level.value + 1)
        return self.hint_level

    def reset_to_review(self) -> None:
        """Reset state machine to initial REVIEW state"""
        self.current_state = DialogueState.REVIEW
        self.fail_count = 0
        self.hint_level = HintLevel.L0

    def get_state(self) -> DialogueState:
        """Get current dialogue state"""
        return self.current_state

    def get_hint_level(self) -> HintLevel:
        """Get current hint level"""
        return self.hint_level

    def get_fail_count(self) -> int:
        """Get current failure count"""
        return self.fail_count

    def is_complete(self) -> bool:
        """Check if dialogue is complete"""
        return self.current_state == DialogueState.SUMMARIZE

    def can_continue(self) -> bool:
        """Check if dialogue can continue (not stuck)"""
        return (
            self.fail_count < self.max_failures or
            self.hint_level >= HintLevel.L3
        )