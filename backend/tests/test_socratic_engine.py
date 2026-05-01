"""
Simple test script for Socratic dialogue engine
Tests the core functionality without requiring full API setup
"""

import asyncio
from datetime import datetime, timezone

from ai.dialogue import DialogueStateMachine, DialogueState, HintLevel
from ai.context_builder import SessionContextBuilder
from ai.prompts import format_system_prompt, GEOMETRY_TOOL
from data.sample_problems import SAMPLE_PROBLEMS


class MockClaudeClient:
    """Mock Claude client for testing without API calls"""

    async def get_response(self, messages, system_prompt, tools=None, max_tokens=1024):
        """Mock response that simulates Socratic behavior"""
        last_message = messages[-1]["content"] if messages else ""

        # Simple mock responses based on dialogue state
        if "tính thể tích" in last_message.lower():
            return "Em hãy bắt đầu bằng cách xác định diện tích đáy của hình chóp. Đáy ABCD là hình vuông cạnh 6cm, vậy diện tích đáy là bao nhiêu?"
        elif "diện tích đáy" in last_message.lower():
            return "Đúng rồi! Diện tích đáy là 36cm². Bây giờ em hãy nhớ công thức thể tích hình chóp: V = (1/3) × S_đáy × h. Em đã biết chiều cao SO chưa?"
        elif "chiều cao" in last_message.lower():
            return "Chính xác! Chiều cao SO = 4cm. Bây giờ em hãy áp dụng công thức thể tích để tính kết quả cuối cùng."
        else:
            return "Em hãy bắt đầu bằng cách xác định các thông số đã biết từ đề bài."

    async def get_response_with_tools(self, messages, system_prompt, tools, max_tokens=1024):
        """Mock response with tool use"""
        text = await self.get_response(messages, system_prompt, tools, max_tokens)
        return {"text": text, "tool_calls": []}


async def test_dialogue_state_machine():
    """Test dialogue state machine transitions"""
    print("Testing Dialogue State Machine...")

    dsm = DialogueStateMachine()

    # Test initial state
    assert dsm.get_state() == DialogueState.REVIEW
    assert dsm.get_hint_level() == HintLevel.L0
    print("✓ Initial state correct")

    # Test transition to heuristic
    dsm.transition_to_heuristic()
    assert dsm.get_state() == DialogueState.HEURISTIC
    print("✓ Transition to HEURISTIC successful")

    # Test transition to rectify
    dsm.transition_to_rectify()
    assert dsm.get_state() == DialogueState.RECTIFY
    assert dsm.get_fail_count() == 1
    print("✓ Transition to RECTIFY successful")

    # Test hint escalation
    dsm.transition_to_rectify()
    dsm.transition_to_rectify()
    assert dsm.get_fail_count() == 3
    assert dsm.should_escalate_hint()
    print("✓ Hint escalation condition met")

    # Test escalate hint
    new_level = dsm.escalate_hint()
    assert new_level == HintLevel.L1
    print("✓ Hint escalated to L1")

    # Test transition to summarize
    dsm.transition_to_summarize()
    assert dsm.get_state() == DialogueState.SUMMARIZE
    assert dsm.is_complete()
    print("✓ Transition to SUMMARIZE successful")

    # Test reset
    dsm.reset_to_review()
    assert dsm.get_state() == DialogueState.REVIEW
    assert dsm.get_hint_level() == HintLevel.L0
    assert dsm.get_fail_count() == 0
    print("✓ Reset successful")

    print("✓ Dialogue State Machine tests passed!\n")


async def test_context_builder():
    """Test session context builder"""
    print("Testing Context Builder...")

    builder = SessionContextBuilder()

    # Test geometry detection
    geometry_problem = SAMPLE_PROBLEMS[0]
    is_geometry = builder.detect_geometry_problem(geometry_problem["statement_latex"])
    assert is_geometry == True
    print("✓ Geometry problem detected")

    non_geometry_problem = SAMPLE_PROBLEMS[2]
    is_geometry = builder.detect_geometry_problem(non_geometry_problem["statement_latex"])
    assert is_geometry == False
    print("✓ Non-geometry problem correctly identified")

    # Test context building
    context = builder.build_context(
        topic_id="hinh-hoc.hinh-chop",
        problem_statement=geometry_problem["statement_latex"],
        dialogue_state="REVIEW",
        fail_count=0,
        hint_level=0,
        conversation_history=[],
        problem_context=None
    )

    assert context["topic"] == "hinh-hoc.hinh-chop"
    assert context["dialogue_state"] == "REVIEW"
    assert context["fail_count"] == 0
    assert context["hint_level"] == 0
    print("✓ Context building successful")

    # Test hint guidance
    guidance = builder.get_hint_guidance(0, "hinh-hoc.hinh-chop")
    assert "Chỉ đặt câu hỏi" in guidance
    print("✓ Hint guidance for L0 correct")

    guidance = builder.get_hint_guidance(2, "hinh-hoc.hinh-chop")
    assert "đưa ra bước đầu tiên" in guidance
    print("✓ Hint guidance for L2 correct")

    print("✓ Context Builder tests passed!\n")


async def test_system_prompt():
    """Test system prompt formatting"""
    print("Testing System Prompt...")

    # Test basic formatting
    prompt = format_system_prompt(
        dialogue_state="HEURISTIC",
        fail_count=1,
        hint_level=0,
        topic="hinh-hoc.hinh-chop",
        problem_statement="Tính thể tích hình chóp",
        misconceptions="Sai khi cho rằng đường cao luôn đi qua tâm đáy"
    )

    assert "HEURISTIC" in prompt
    assert "1" in prompt  # fail_count value
    assert "0" in prompt  # hint_level value
    assert "hinh-hoc.hinh-chop" in prompt
    print("✓ System prompt formatting successful")

    # Test geometry tool spec
    assert GEOMETRY_TOOL["name"] == "render_geometry"
    assert "pyramid" in GEOMETRY_TOOL["input_schema"]["properties"]["solid_type"]["enum"]
    print("✓ Geometry tool spec correct")

    print("✓ System Prompt tests passed!\n")


async def test_sample_socratic_dialogue():
    """Test a sample Socratic dialogue"""
    print("Testing Sample Socratic Dialogue...")

    # Initialize components
    dsm = DialogueStateMachine()
    builder = SessionContextBuilder()
    mock_client = MockClaudeClient()

    # Get sample problem
    problem = SAMPLE_PROBLEMS[0]

    # Simulate dialogue
    conversation = []

    # Student asks question
    student_message = "Tính thể tích hình chóp S.ABCD"
    conversation.append({"role": "user", "content": student_message})

    # Build context
    context = builder.build_context(
        topic_id=problem["topic_id"],
        problem_statement=problem["statement_latex"],
        dialogue_state=dsm.get_state().value,
        fail_count=dsm.get_fail_count(),
        hint_level=dsm.get_hint_level().value,
        conversation_history=conversation,
        problem_context={"statement": problem["statement_latex"]}
    )

    # Get AI response
    system_prompt = format_system_prompt(
        dialogue_state=context["dialogue_state"],
        fail_count=context["fail_count"],
        hint_level=context["hint_level"],
        topic=context["topic"],
        problem_statement=context["problem_statement"],
        misconceptions=context["misconceptions"]
    )

    ai_response = await mock_client.get_response(
        messages=conversation,
        system_prompt=system_prompt
    )

    conversation.append({"role": "assistant", "content": ai_response})

    # Verify response is Socratic (asks question, doesn't give answer)
    assert "?" in ai_response
    assert "48" not in ai_response  # Should not contain the answer
    print("✓ AI response is Socratic (asks question)")

    # Student responds
    student_message = "Diện tích đáy là 36cm²"
    conversation.append({"role": "user", "content": student_message})

    # Get next AI response
    ai_response = await mock_client.get_response(
        messages=conversation,
        system_prompt=system_prompt
    )

    conversation.append({"role": "assistant", "content": ai_response})

    # Verify response continues to guide
    assert "?" in ai_response
    print("✓ AI continues to guide student")

    print("✓ Sample Socratic Dialogue test passed!\n")


async def main():
    """Run all tests"""
    print("=" * 50)
    print("Toán Socratic - Socratic Engine Tests")
    print("=" * 50)
    print()

    try:
        await test_dialogue_state_machine()
        await test_context_builder()
        await test_system_prompt()
        await test_sample_socratic_dialogue()

        print("=" * 50)
        print("✓ All tests passed successfully!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n✗ Test failed: {str(e)}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())