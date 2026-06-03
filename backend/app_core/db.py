import os
from contextlib import contextmanager
from typing import Any, List, Optional

import pymysql
from dbutils.pooled_db import PooledDB
from dotenv import load_dotenv

# Load .env sitting at repository root
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(ENV_PATH)


class Database:
    """Connection pool helper for MySQL."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        dbname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.host = host or os.getenv('MYSQL_HOST', '127.0.0.1')
        self.port = port or int(os.getenv('MYSQL_PORT', '3306'))
        self.dbname = dbname or os.getenv('MYSQL_DBNAME', 'student_db')
        self.user = user or os.getenv('MYSQL_USER')
        self.password = password or os.getenv('MYSQL_PASSWORD')

        if not self.user or not self.password:
            raise ValueError('Please set MYSQL_USER and MYSQL_PASSWORD in .env for MySQL access')

        self.pool: PooledDB = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=1,
            maxcached=5,
            blocking=True,
            host=self.host,
            port=self.port,
            database=self.dbname,
            user=self.user,
            password=self.password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
        )

    @contextmanager
    def get_cursor(self, autocommit: bool = False):
        conn = self.pool.connection()
        if autocommit:
            conn.autocommit = True
        cur = conn.cursor()
        try:
            yield cur
            if not autocommit:
                conn.commit()
        except Exception:
            if not autocommit:
                conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()  # PooledDB returns connection to pool on close()

    # ── schema helpers ──────────────────────────────────────────────

    def _index_exists(self, table: str, index_name: str) -> bool:
        """Check whether an index exists on a table."""
        row = self.fetch_one(
            """SELECT COUNT(*) AS cnt FROM information_schema.STATISTICS
               WHERE table_schema = DATABASE()
                 AND table_name = %s
                 AND index_name = %s""",
            [table, index_name],
        )
        return row is not None and row['cnt'] > 0

    def _column_exists(self, table: str, column: str) -> bool:
        """Check whether a column exists in a table."""
        row = self.fetch_one(
            """SELECT COUNT(*) AS cnt FROM information_schema.COLUMNS
               WHERE table_schema = DATABASE()
                 AND table_name = %s
                 AND column_name = %s""",
            [table, column],
        )
        return row is not None and row['cnt'] > 0

    def _constraint_exists(self, table: str, constraint_name: str) -> bool:
        """Check whether a constraint exists on a table."""
        row = self.fetch_one(
            """SELECT COUNT(*) AS cnt FROM information_schema.TABLE_CONSTRAINTS
               WHERE table_schema = DATABASE()
                 AND table_name = %s
                 AND constraint_name = %s""",
            [table, constraint_name],
        )
        return row is not None and row['cnt'] > 0

    def _add_column_if_not_exists(self, table: str, column: str, column_def: str) -> None:
        """Add a column to a table if it doesn't already exist."""
        if not self._column_exists(table, column):
            self.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_def}")

    def _add_constraint_if_not_exists(self, table: str, constraint_name: str, clause: str) -> None:
        """Add a constraint to a table if it doesn't already exist."""
        if not self._constraint_exists(table, constraint_name):
            self.execute(f"ALTER TABLE {table} ADD CONSTRAINT {constraint_name} {clause}")

    def init_schema(self) -> None:
        """Create base tables if they do not exist."""

        # ── tables ──────────────────────────────────────────────────
        table_statements = [
            """
            CREATE TABLE IF NOT EXISTS teachers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_no VARCHAR(32) UNIQUE NOT NULL,
                name VARCHAR(64) NOT NULL,
                department VARCHAR(128) DEFAULT ''
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_no VARCHAR(32) UNIQUE NOT NULL,
                name VARCHAR(64) NOT NULL,
                major VARCHAR(128) DEFAULT '',
                current_semester INT DEFAULT 1,
                semester_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_code VARCHAR(32) UNIQUE NOT NULL,
                name VARCHAR(128) NOT NULL,
                credit DECIMAL(3,1) DEFAULT 0,
                capacity INT DEFAULT 50,
                teacher_id INT,
                pass_rate DECIMAL(5,2),
                excellent_rate DECIMAL(5,2),
                ordinary_weight DECIMAL(3,2) DEFAULT 0.5,
                final_weight DECIMAL(3,2) DEFAULT 0.5,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT NOT NULL,
                status VARCHAR(32) DEFAULT 'enrolled',
                grade DECIMAL(4,1),
                ordinary_score DECIMAL(4,1),
                final_score DECIMAL(4,1),
                final_grade DECIMAL(4,1),
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(64) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                role VARCHAR(32) NOT NULL,
                ref_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS major_plans (
                id INT AUTO_INCREMENT PRIMARY KEY,
                major_name VARCHAR(128) NOT NULL,
                description VARCHAR(1024) DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(major_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            """
            CREATE TABLE IF NOT EXISTS major_plan_courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                plan_id INT NOT NULL,
                course_id INT NOT NULL,
                semester INT NOT NULL,
                is_required TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(plan_id, course_id, semester),
                FOREIGN KEY (plan_id) REFERENCES major_plans(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
        ]

        with self.get_cursor(autocommit=True) as cur:
            for stmt in table_statements:
                cur.execute(stmt)

        # ── indexes ─────────────────────────────────────────────────
        indexes = [
            ('idx_enrollments_course', 'enrollments', 'course_id'),
            ('idx_enrollments_student', 'enrollments', 'student_id'),
            ('idx_users_username', 'users', 'username'),
        ]
        for idx_name, tbl, col in indexes:
            if not self._index_exists(tbl, idx_name):
                self.execute(f"CREATE INDEX {idx_name} ON {tbl}({col})")

        # ── conditional columns (migration-safe) ────────────────────
        self._add_column_if_not_exists('students', 'semester_updated_at',
                                       "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        self._add_column_if_not_exists('courses', 'pass_rate', 'DECIMAL(5,2)')
        self._add_column_if_not_exists('courses', 'excellent_rate', 'DECIMAL(5,2)')
        self._add_column_if_not_exists('courses', 'ordinary_weight', "DECIMAL(3,2) DEFAULT 0.5")
        self._add_column_if_not_exists('courses', 'final_weight', "DECIMAL(3,2) DEFAULT 0.5")
        self._add_column_if_not_exists('enrollments', 'ordinary_score', 'DECIMAL(4,1)')
        self._add_column_if_not_exists('enrollments', 'final_score', 'DECIMAL(4,1)')
        self._add_column_if_not_exists('enrollments', 'final_grade', 'DECIMAL(4,1)')

        # ── conditional constraints (migration-safe) ────────────────
        constraints = [
            ('courses_credit_nonneg', 'courses', 'CHECK (credit >= 0)'),
            ('courses_capacity_positive', 'courses', 'CHECK (capacity > 0)'),
            ('enrollments_status_valid', 'enrollments',
             "CHECK (status IN ('enrolled', 'dropped', 'completed'))"),
            ('enrollments_grade_range', 'enrollments',
             'CHECK (grade IS NULL OR (grade >= 0 AND grade <= 100))'),
            ('enrollments_ordinary_score_range', 'enrollments',
             'CHECK (ordinary_score IS NULL OR (ordinary_score >= 0 AND ordinary_score <= 100))'),
            ('enrollments_final_score_range', 'enrollments',
             'CHECK (final_score IS NULL OR (final_score >= 0 AND final_score <= 100))'),
            ('enrollments_final_grade_range', 'enrollments',
             'CHECK (final_grade IS NULL OR (final_grade >= 0 AND final_grade <= 100))'),
            ('major_plan_courses_semester_range', 'major_plan_courses',
             'CHECK (semester BETWEEN 1 AND 12)'),
            ('users_role_valid', 'users',
             "CHECK (role IN ('admin', 'student', 'teacher'))"),
        ]
        for cname, tbl, clause in constraints:
            self._add_constraint_if_not_exists(tbl, cname, clause)

    # ── query helpers ───────────────────────────────────────────────

    def fetch_all(self, sql: str, params: Optional[List[Any]] = None):
        with self.get_cursor() as cur:
            cur.execute(sql, params or [])
            return list(cur.fetchall())

    def fetch_one(self, sql: str, params: Optional[List[Any]] = None):
        with self.get_cursor() as cur:
            cur.execute(sql, params or [])
            row = cur.fetchone()
            return dict(row) if row else None

    def execute(self, sql: str, params: Optional[List[Any]] = None) -> None:
        with self.get_cursor() as cur:
            cur.execute(sql, params or [])

    def execute_returning(self, sql: str, params: Optional[List[Any]] = None):
        with self.get_cursor() as cur:
            cur.execute(sql, params or [])
            return cur.lastrowid


db = Database()
db.init_schema()


def shutdown():
    """Cleanly close pool."""
    db.pool.close()
