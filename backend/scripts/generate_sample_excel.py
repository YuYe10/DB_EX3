"""Generate a sample Excel workbook for course import.

Usage:
    python generate_sample_excel.py

It creates sample_import.xlsx in the current directory with sheets:
- courses     (course_code, name, credit, capacity, teacher_no, teacher_name)
- students    (student_no, name, major)
- enrollments (course_code, student_no, grade, status)
"""
from pathlib import Path
import pandas as pd

SAMPLE_PATH = Path(__file__).resolve().parent / "sample_import.xlsx"


def main():
    courses = pd.DataFrame([
        {
            "course_code": "C001",
            "name": "数据库原理",
            "credit": 3,
            "capacity": 60,
            "teacher_no": "T001",
            "teacher_name": "张老师",
        },
        {
            "course_code": "C002",
            "name": "操作系统",
            "credit": 4,
            "capacity": 50,
            "teacher_no": "T002",
            "teacher_name": "李老师",
        },
    ])

    students = pd.DataFrame([
        {"student_no": "S001", "name": "王同学", "major": "计算机"},
        {"student_no": "S002", "name": "李同学", "major": "软件工程"},
        {"student_no": "S003", "name": "赵同学", "major": "人工智能"},
    ])

    enrollments = pd.DataFrame([
        {"course_code": "C001", "student_no": "S001", "grade": 92, "status": "enrolled"},
        {"course_code": "C001", "student_no": "S002", "grade": None, "status": "enrolled"},
        {"course_code": "C002", "student_no": "S003", "grade": 88, "status": "enrolled"},
    ])

    with pd.ExcelWriter(SAMPLE_PATH, engine="openpyxl") as writer:
        courses.to_excel(writer, sheet_name="courses", index=False)
        students.to_excel(writer, sheet_name="students", index=False)
        enrollments.to_excel(writer, sheet_name="enrollments", index=False)

    print(f"Sample workbook generated at: {SAMPLE_PATH}")


if __name__ == "__main__":
    main()
