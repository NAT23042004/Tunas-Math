import pytest

from toan_socratic.ai.turn_assessment import TurnAssessment, assess_student_turn


class TestTurnAssessment:
    @pytest.mark.unit
    def test_assess_stuck_message(self):
        assert assess_student_turn("Em không biết bắt đầu") == TurnAssessment.STUCK

    @pytest.mark.unit
    def test_assess_progressing_message(self):
        assert assess_student_turn("Em biết diện tích đáy là 36 cm2") == TurnAssessment.PROGRESSING

    @pytest.mark.unit
    def test_does_not_mark_binh_phuong_as_stuck_without_accents(self):
        assert assess_student_turn("binh phuong") != TurnAssessment.STUCK

    @pytest.mark.unit
    def test_does_not_mark_binh_phuong_as_stuck_with_accents(self):
        assert assess_student_turn("bình phương") != TurnAssessment.STUCK

    @pytest.mark.unit
    def test_assess_incorrect_assertion(self):
        assert assess_student_turn("V = 50 cm3", expected_answer="V = 48 cm³") == TurnAssessment.INCORRECT

    @pytest.mark.unit
    def test_assess_matching_answer(self):
        assert assess_student_turn("V = 48 cm3", expected_answer="V = 48 cm³") == TurnAssessment.SOLVED
