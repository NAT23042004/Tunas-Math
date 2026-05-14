"""
Sample problems for testing the Socratic dialogue engine
"""

SAMPLE_PROBLEMS = [
    {
        "topic_id": "hinh-hoc.hinh-chop",
        "statement_latex": "Cho hình chóp S.ABCD có đáy ABCD là hình vuông cạnh $a = 6$ cm. Đỉnh S nằm trên đường thẳng qua tâm O của đáy và vuông góc với mặt đáy. Biết SO = 4 cm. Tính thể tích của hình chóp.",
        "difficulty": "easy",
        "answer": "V = 48 cm³",
        "is_geometry": True,
        "geometry_params": {
            "solid_type": "pyramid",
            "params": {
                "base_shape": "square",
                "base_side": 6,
                "height": 4,
                "apex_label": "S",
                "base_labels": ["A", "B", "C", "D"],
                "show_altitude": True,
                "altitude_foot_label": "O"
            },
            "labels": {
                "apex": "S",
                "base": ["A", "B", "C", "D"],
                "center": "O"
            }
        },
        "source": "THPT 2023",
        "misconceptions": [
            "Sai khi cho rằng đường cao luôn đi qua tâm đáy",
            "Nhầm lẫn giữa diện tích xung quanh và diện tích toàn phần"
        ]
    },
    {
        "topic_id": "hinh-hoc.lang-tru",
        "statement_latex": "Cho lăng trụ đứng ABC.A'B'C' có đáy ABC là tam giác đều cạnh $a = 4$ cm. Chiều cao của lăng trụ là $h = 6$ cm. Tính thể tích của lăng trụ.",
        "difficulty": "easy",
        "answer": "V = 24√3 cm³",
        "is_geometry": True,
        "geometry_params": {
            "solid_type": "prism",
            "params": {
                "base_shape": "triangle",
                "base_side": 4,
                "height": 6,
                "top_labels": ["A'", "B'", "C'"],
                "bottom_labels": ["A", "B", "C"]
            },
            "labels": {
                "top": ["A'", "B'", "C'"],
                "bottom": ["A", "B", "C"]
            }
        },
        "source": "THPT 2022",
        "misconceptions": [
            "Nhầm lẫn diện tích các mặt bên",
            "Sai khi tính thể tích với diện tích đáy sai"
        ]
    },
    {
        "topic_id": "giai-tich.dao-ham",
        "statement_latex": "Tính đạo hàm của hàm số $f(x) = x^3 - 2x^2 + 3x - 1$.",
        "difficulty": "easy",
        "answer": "f'(x) = 3x² - 4x + 3",
        "is_geometry": False,
        "geometry_params": None,
        "source": "Sách giáo khoa",
        "misconceptions": [
            "Nhầm lẫn các quy tắc đạo hàm",
            "Quên công thức đạo hàm của hàm mũ"
        ]
    },
    {
        "topic_id": "giai-tich.nguyen-ham",
        "statement_latex": "Tìm nguyên hàm của hàm số $f(x) = 2x + 3$.",
        "difficulty": "easy",
        "answer": "∫f(x)dx = x² + 3x + C",
        "is_geometry": False,
        "geometry_params": None,
        "source": "Sách giáo khoa",
        "misconceptions": [
            "Nhầm lẫn nguyên hàm và đạo hàm",
            "Quên hằng số tích phân"
        ]
    },
    {
        "topic_id": "hinh-hoc.hinh-chop",
        "statement_latex": "Cho hình chóp S.ABCD có đáy ABCD là hình chữ nhật với AB = 8 cm, AD = 6 cm. Đỉnh S nằm trên đường thẳng qua tâm O của đáy và vuông góc với mặt đáy. Biết SO = 5 cm. Tính thể tích của hình chóp.",
        "difficulty": "medium",
        "answer": "V = 80 cm³",
        "is_geometry": True,
        "geometry_params": {
            "solid_type": "pyramid",
            "params": {
                "base_shape": "rect",
                "base_width": 8,
                "base_depth": 6,
                "height": 5,
                "apex_label": "S",
                "base_labels": ["A", "B", "C", "D"],
                "show_altitude": True,
                "altitude_foot_label": "O"
            },
            "labels": {
                "apex": "S",
                "base": ["A", "B", "C", "D"],
                "center": "O"
            }
        },
        "source": "THPT 2024",
        "misconceptions": [
            "Sai khi tính diện tích đáy hình chữ nhật",
            "Quên hệ thức giữa thể tích và diện tích đáy"
        ]
    }
]


def get_sample_problems():
    """Get sample problems for testing"""
    return SAMPLE_PROBLEMS


def get_problem_by_topic(topic_id: str):
    """Get sample problems by topic"""
    return [p for p in SAMPLE_PROBLEMS if p["topic_id"] == topic_id]


def get_geometry_problems():
    """Get geometry problems only"""
    return [p for p in SAMPLE_PROBLEMS if p["is_geometry"]]