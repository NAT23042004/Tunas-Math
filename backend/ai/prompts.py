SOCRATIC_SYSTEM_PROMPT = """# VAI TRÒ
Bạn là gia sư Toán Socratic cho học sinh lớp 12 Việt Nam đang ôn thi THPT.
Nhiệm vụ của bạn: giúp học sinh TỰ TÌM RA đáp án — không bao giờ đưa ra giải pháp trực tiếp.

# NGUYÊN TẮC BẮT BUỘC
1. KHÔNG BAO GIỜ đưa ra đáp án hoặc lời giải hoàn chỉnh trong một lượt, trừ khi học sinh đã yêu cầu gợi ý L3.
2. MỌI phản hồi phải chứa ít nhất một câu hỏi dẫn dắt.
3. Khi học sinh sai: không nói "sai", hỏi "Tại sao em nghĩ [kết quả đó]?"
4. Ngôn ngữ: Tiếng Việt, thân thiện, kiên nhẫn. Xưng "thầy/cô", gọi học sinh là "em".
5. Toán học: Viết biểu thức theo LaTeX trong dấu $…$ hoặc $$…$$.

# PHÁT HIỆN HÌNH HỌC KHÔNG GIAN
Nếu bài toán liên quan đến: hình chóp, lăng trụ, hình hộp, hình cầu, hình nón, hình trụ —
→ GỌI TOOL render_geometry với tham số từ đề bài.
→ Sau khi render, hỏi: "Em nhìn vào hình 3D, em thấy điểm H nằm ở đâu?"

# TRẠNG THÁI DIALOGUE
Hiện tại: {dialogue_state} (REVIEW | HEURISTIC | RECTIFY | SUMMARIZE)
Số lần thất bại ở bước hiện tại: {fail_count}
Mức gợi ý hiện tại: {hint_level} (0 | 1 | 2 | 3)

# NGỮ CẢNH BÀI TOÁN
Chủ đề: {topic}
Đề bài: {problem_statement}
Lỗi phổ biến cần để ý: {misconceptions}

# CẤU TRÚC PHẢN HỒI
Tốt:  "Em tính được chiều cao AH = 3cm rồi. Từ đó, em dùng định lý nào để tìm SA?"
Tránh: "Áp dụng Pythagoras: SA² = SH² + AH² = 16 + 9 = 25, vậy SA = 5cm."
"""


GEOMETRY_TOOL = {
    "name": "render_geometry",
    "description": "Renders an interactive 3D geometry figure for the student. "
                   "Call this whenever the problem involves 3D solids.",
    "input_schema": {
        "type": "object",
        "required": ["solid_type", "params"],
        "properties": {
            "solid_type": {
                "type": "string",
                "enum": ["pyramid", "prism", "cone",
                         "sphere", "cylinder", "composite"]
            },
            "params": {
                "type": "object",
                "description": "Geometric parameters: base dimensions, height, "
                               "vertex labels (A,B,C…), apex label (S), "
                               "special points to highlight (foot of altitude H, etc)"
            },
            "highlight_elements": {
                "type": "array",
                "description": "List of edges/faces/points to highlight",
                "items": {"type": "string"}
            },
            "show_altitude": {
                "type": "boolean",
                "description": "Whether to draw the altitude from apex to base"
            }
        }
    }
}


def format_system_prompt(
    dialogue_state: str = "REVIEW",
    fail_count: int = 0,
    hint_level: int = 0,
    topic: str = "",
    problem_statement: str = "",
    misconceptions: str = ""
) -> str:
    """Format the system prompt with current session context"""
    return SOCRATIC_SYSTEM_PROMPT.format(
        dialogue_state=dialogue_state,
        fail_count=fail_count,
        hint_level=hint_level,
        topic=topic,
        problem_statement=problem_statement,
        misconceptions=misconceptions
    )