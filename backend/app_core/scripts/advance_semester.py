"""Advance student semesters if six months have passed since last update.

Usage:
    python advance_semester.py

Intended to be scheduled (e.g., cron) to run daily/weekly. It only updates
students whose `semester_updated_at` is at least 6 months old and whose
`current_semester` is below the maximum (default 8).
"""

import os
import sys
from datetime import datetime

from app_core import db

MAX_SEMESTER = int(os.getenv("MAX_SEMESTER", "8"))
MONTHS_INTERVAL = os.getenv("SEMESTER_INTERVAL_MONTHS", "6")


def advance_semesters():
    """Increment current_semester for eligible students."""
    interval_expr = f"INTERVAL '{MONTHS_INTERVAL} months'"
    result = db.fetch_one(
        f"""
        WITH bumped AS (
            UPDATE students
            SET current_semester = LEAST(current_semester + 1, %s),
                semester_updated_at = NOW()
            WHERE current_semester < %s
              AND (semester_updated_at IS NULL OR semester_updated_at <= NOW() - {interval_expr})
            RETURNING id
        )
        SELECT COUNT(*) AS updated FROM bumped;
        """,
        [MAX_SEMESTER, MAX_SEMESTER],
    )
    count = result.get("updated", 0) if result else 0
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] advanced semesters for {count} students")
    return count


def main():
    try:
        advance_semesters()
    except Exception as exc:  # pragma: no cover - script entry point
        print(f"Failed to advance semesters: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
