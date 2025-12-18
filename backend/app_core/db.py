import os
from contextlib import contextmanager
from typing import Any, List, Optional, cast

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

# Load .env sitting at repository root
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(ENV_PATH)


class Database:
    """Connection pool helper for openGauss/PostgreSQL."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        dbname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.host = host or os.getenv('OG_HOST', 'localhost')
        self.port = port or int(os.getenv('OG_PORT') or 26000)
        self.dbname = dbname or os.getenv('OG_DBNAME', 'student_db')
        self.user = user or os.getenv('OG_USER')
        self.password = password or os.getenv('OG_PASSWORD')

        # SSH tunneling config (optional)
        self.use_ssh = os.getenv('OG_SSH_TUNNEL', 'false').lower() == 'true'
        self.tunnel: Optional[SSHTunnelForwarder] = None
        if self.use_ssh:
            ssh_host = os.getenv('OG_SSH_HOST', self.host)
            ssh_port = int(os.getenv('OG_SSH_PORT') or 22)
            ssh_user = os.getenv('OG_SSH_USER')
            ssh_password = os.getenv('OG_SSH_PASSWORD')
            ssh_pkey = os.getenv('OG_SSH_PKEY')  # path to private key
            remote_bind_host = self.host
            remote_bind_port = self.port

            if not ssh_user:
                raise ValueError('OG_SSH_USER is required when OG_SSH_TUNNEL=true')

            # Create SSH tunnel: local bind -> remote db host:port
            self.tunnel = SSHTunnelForwarder(
                (ssh_host, ssh_port),
                ssh_username=ssh_user,
                ssh_password=ssh_password,
                ssh_pkey=ssh_pkey,
                remote_bind_address=(remote_bind_host, remote_bind_port),
                local_bind_address=('127.0.0.1', 0),  # auto-pick free local port
            )
            self.tunnel.start()
            active_tunnel = cast(SSHTunnelForwarder, self.tunnel)
            assert active_tunnel.local_bind_port is not None
            self.host = '127.0.0.1'
            self.port = int(active_tunnel.local_bind_port)

        if not self.user or not self.password:
            raise ValueError('Please set OG_USER and OG_PASSWORD in .env for openGauss access')

        self.pool: pool.SimpleConnectionPool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

    @contextmanager
    def get_cursor(self, autocommit: bool = False):
        conn = self.pool.getconn()
        if autocommit:
            conn.autocommit = True
        cur = conn.cursor(cursor_factory=RealDictCursor)
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
            self.pool.putconn(conn)

    def init_schema(self) -> None:
        """Create base tables if they do not exist."""
        statements = [
            """
            CREATE TABLE IF NOT EXISTS teachers (
                id SERIAL PRIMARY KEY,
                teacher_no VARCHAR(32) UNIQUE NOT NULL,
                name VARCHAR(64) NOT NULL,
                department VARCHAR(128) DEFAULT ''
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                student_no VARCHAR(32) UNIQUE NOT NULL,
                name VARCHAR(64) NOT NULL,
                major VARCHAR(128) DEFAULT ''
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                course_code VARCHAR(32) UNIQUE NOT NULL,
                name VARCHAR(128) NOT NULL,
                credit NUMERIC(3,1) DEFAULT 0,
                capacity INT DEFAULT 50,
                teacher_id INT REFERENCES teachers(id) ON DELETE SET NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                id SERIAL PRIMARY KEY,
                student_id INT REFERENCES students(id) ON DELETE CASCADE,
                course_id INT REFERENCES courses(id) ON DELETE CASCADE,
                status VARCHAR(32) DEFAULT 'enrolled',
                grade NUMERIC(4,1),
                enrolled_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(student_id, course_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(64) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                role VARCHAR(32) NOT NULL,
                ref_id INT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS major_plans (
                id SERIAL PRIMARY KEY,
                major_name VARCHAR(128) NOT NULL,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(major_name)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS major_plan_courses (
                id SERIAL PRIMARY KEY,
                plan_id INT REFERENCES major_plans(id) ON DELETE CASCADE,
                course_id INT REFERENCES courses(id) ON DELETE CASCADE,
                semester INT NOT NULL,
                is_required BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(plan_id, course_id, semester)
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            """,
        ]

        with self.get_cursor(autocommit=True) as cur:
            for stmt in statements:
                cur.execute(stmt)

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
            row = cur.fetchone()
            if row:
                return list(row.values())[0]
            return None


db = Database()
db.init_schema()


def shutdown():
    """Cleanly close pool and SSH tunnel (if any)."""
    db.pool.closeall()
    if isinstance(getattr(db, 'tunnel', None), SSHTunnelForwarder):
        active_tunnel = cast(SSHTunnelForwarder, db.tunnel)
        active_tunnel.stop()
