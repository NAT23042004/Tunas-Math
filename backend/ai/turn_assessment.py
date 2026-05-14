import re
import unicodedata
from enum import Enum


class TurnAssessment(str, Enum):
    PROGRESSING = "progressing"
    INCORRECT = "incorrect"
    STUCK = "stuck"
    SOLVED = "solved"
    UNKNOWN = "unknown"


_STUCK_PHRASES = (
    "khong biet",
    "khong hieu",
    "em khong biet",
    "em khong hieu",
    "bi roi",
    "chiu",
    "khong lam duoc",
    "khong nho",
    "goi y",
    "giup em",
)

_ASSERTION_MARKERS = (
    "=",
    "dap an",
    "ket qua",
)


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_text(value: str) -> str:
    lowered = _strip_accents(value).lower()
    lowered = lowered.replace("đ", "d")
    lowered = re.sub(r"\$+", " ", lowered)
    lowered = re.sub(r"\\[a-zA-Z]+", " ", lowered)
    lowered = re.sub(r"[^a-z0-9=+\-*/^√ ]+", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def _extract_math_tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z]+|\d+", value))


def _looks_stuck(normalized_message: str) -> bool:
    if not normalized_message:
        return True
    return any(
        re.search(rf"(^| ){re.escape(phrase)}( |$)", normalized_message)
        for phrase in _STUCK_PHRASES
    )


def _looks_like_assertion(normalized_message: str) -> bool:
    return any(marker in normalized_message for marker in _ASSERTION_MARKERS)


def _matches_answer(normalized_message: str, normalized_answer: str) -> bool:
    if not normalized_answer:
        return False
    if normalized_answer in normalized_message:
        return True

    answer_tokens = _extract_math_tokens(normalized_answer)
    if not answer_tokens:
        return False

    message_tokens = _extract_math_tokens(normalized_message)
    overlap = len(answer_tokens & message_tokens)
    return overlap == len(answer_tokens)


def assess_student_turn(
    message: str,
    expected_answer: str | None = None,
) -> TurnAssessment:
    normalized_message = normalize_text(message)
    normalized_answer = normalize_text(expected_answer or "")

    if _looks_stuck(normalized_message):
        return TurnAssessment.STUCK

    if normalized_answer and _matches_answer(normalized_message, normalized_answer):
        return TurnAssessment.SOLVED

    if normalized_answer and _looks_like_assertion(normalized_message):
        answer_tokens = _extract_math_tokens(normalized_answer)
        message_tokens = _extract_math_tokens(normalized_message)
        if answer_tokens & message_tokens:
            return TurnAssessment.INCORRECT

    if len(normalized_message) >= 8:
        return TurnAssessment.PROGRESSING

    return TurnAssessment.UNKNOWN
