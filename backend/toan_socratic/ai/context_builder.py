from typing import Dict, Any, List, Optional
from datetime import datetime


class SessionContextBuilder:
    """Builds context for Socratic dialogue sessions"""

    def __init__(self):
        self.misconceptions_catalog = self._load_misconceptions_catalog()

    def _load_misconceptions_catalog(self) -> Dict[str, List[str]]:
        """Load common misconceptions by topic"""
        return {
            "hinh-hoc.hinh-chop": [
                "Sai khi cho rằng đường cao luôn đi qua tâm đáy",
                "Nhầm lẫn giữa diện tích xung quanh và diện tích toàn phần",
                "Quên hệ thức giữa thể tích và diện tích đáy",
                "Sai khi tính góc giữa đường thẳng và mặt phẳng"
            ],
            "hinh-hoc.lang-tru": [
                "Nhầm lẫn diện tích các mặt bên",
                "Sai khi tính thể tích với diện tích đáy sai",
                "Quên hệ thức giữa diện tích và thể tích",
                "Sai khi xác định các đường chéo"
            ],
            "giai-tich.dao-ham": [
                "Nhầm lẫn các quy tắc đạo hàm",
                "Quên chain rule cho hàm hợp",
                "Sai khi đạo hàm hàm mũ và logarithm",
                "Quên đạo hàm hàm lượng giác"
            ],
            "giai-tich.nguyen-ham": [
                "Nhầm lẫn nguyên hàm và đạo hàm",
                "Quên hằng số tích phân",
                "Sai khi áp dụng phương pháp đổi biến",
                "Quên công thức tích phân từng phần"
            ],
            "giai-tich.tich-phan": [
                "Nhầm lẫn tích phân xác định và không xác định",
                "Quên giới hạn tích phân",
                "Sai khi tính diện tích dưới đường cong",
                "Quên định lý Newton-Leibniz"
            ],
            "xac-suat": [
                "Nhầm lẫn xác suất và thống kê",
                "Sai khi tính xác suất của sự kiện đối",
                "Quên công thức xác suất có điều kiện",
                "Sai khi áp dụng định lý Bayes"
            ]
        }

    def build_context(
        self,
        topic_id: str,
        problem_statement: str,
        dialogue_state: str,
        fail_count: int,
        hint_level: int,
        conversation_history: List[Dict[str, Any]],
        problem_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build complete context for Socratic dialogue

        Args:
            topic_id: Current topic identifier
            problem_statement: Current problem statement
            dialogue_state: Current dialogue state
            fail_count: Number of failures at current step
            hint_level: Current hint level
            conversation_history: Previous conversation turns
            problem_context: Additional problem-specific context

        Returns:
            Complete context dictionary
        """
        # Get misconceptions for current topic
        misconceptions = self.misconceptions_catalog.get(
            topic_id,
            ["Hãy chú ý đến các bước cơ bản", "Kiểm tra lại kết quả"]
        )

        # Build recent conversation summary
        recent_history = self._summarize_recent_history(conversation_history)

        # Build context
        context = {
            "topic": topic_id,
            "problem_statement": problem_statement,
            "dialogue_state": dialogue_state,
            "fail_count": fail_count,
            "hint_level": hint_level,
            "misconceptions": "; ".join(misconceptions),
            "recent_history": recent_history,
            "problem_context": problem_context or {}
        }

        return context

    def _summarize_recent_history(
        self,
        conversation_history: List[Dict[str, Any]],
        max_turns: int = 3
    ) -> str:
        """Summarize recent conversation history

        Args:
            conversation_history: Full conversation history
            max_turns: Maximum number of recent turns to include

        Returns:
            Summary of recent conversation
        """
        if not conversation_history:
            return "Chưa có cuộc trò chuyện nào."

        recent_turns = conversation_history[-max_turns:]
        summary_parts = []

        for turn in recent_turns:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")

            if role == "user":
                summary_parts.append(f"Học sinh: {content[:100]}...")
            elif role == "assistant":
                summary_parts.append(f"Gia sư: {content[:100]}...")

        return " | ".join(summary_parts)

    def get_hint_guidance(self, hint_level: int, topic_id: str) -> str:
        """Get guidance text based on hint level

        Args:
            hint_level: Current hint level (0-3)
            topic_id: Current topic

        Returns:
            Guidance text for the AI
        """
        guidance_map = {
            0: "Chỉ đặt câu hỏi dẫn dắt, không đưa ra thông tin trực tiếp.",
            1: "Có thể gợi ý công cụ hoặc định lý cần dùng, nhưng vẫn phải đặt câu hỏi.",
            2: "Có thể đưa ra bước đầu tiên, nhưng học sinh phải hoàn thành phần còn lại.",
            3: "Có thể đưa ra giải pháp hoàn chỉnh, sau đó đưa ra bài tập tương tự."
        }

        base_guidance = guidance_map.get(hint_level, guidance_map[0])

        # Add topic-specific guidance
        topic_misconceptions = self.misconceptions_catalog.get(topic_id, [])
        if topic_misconceptions and hint_level > 0:
            base_guidance += f" Cần chú ý đến các lỗi thường gặp: {', '.join(topic_misconceptions[:2])}."

        return base_guidance

    def detect_geometry_problem(self, problem_statement: str) -> bool:
        """Detect if problem involves 3D geometry

        Args:
            problem_statement: Problem text

        Returns:
            True if geometry problem detected
        """
        geometry_keywords = [
            "hình chóp", "lăng trụ", "hình hộp", "hình cầu",
            "hình nón", "hình trụ", "thể tích", "diện tích xung quanh",
            "chiều cao", "đáy", "đỉnh", "mặt phẳng"
        ]

        problem_lower = problem_statement.lower()
        return any(keyword in problem_lower for keyword in geometry_keywords)