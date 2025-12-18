"""Generate a sample Excel workbook for teacher course roster import.

Usage:
    python generate_teacher_roster.py

It creates teacher_roster_sample.xlsx in the current directory with sheets:
- course    (course_code, name, credit, capacity)
- students  (student_no, name, major)
"""
from pathlib import Path
import pandas as pd

SAMPLE_PATH = Path(__file__).resolve().parent / "teacher_roster_sample.xlsx"


def main():
    course = pd.DataFrame([
        {
            "course_code": "C900",
            "name": "算法设计",
            "credit": 3,
            "capacity": 80,
        }
    ])

    students = pd.DataFrame([
        {"student_no": "S1001", "name": "张同学", "major": "计算机"},
        {"student_no": "S1002", "name": "李同学", "major": "软件工程"},
        {"student_no": "S1003", "name": "王同学", "major": "人工智能"},
    ])

    with pd.ExcelWriter(SAMPLE_PATH, engine="openpyxl") as writer:
        course.to_excel(writer, sheet_name="course", index=False)
        students.to_excel(writer, sheet_name="students", index=False)

    print(f"Teacher roster sample generated at: {SAMPLE_PATH}")


if __name__ == "__main__":
    main()
