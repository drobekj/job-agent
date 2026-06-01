import sqlite3
from config import DATABASE_PATH


def init_db(DATABASE_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processed_at TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            source_file TEXT,
            title TEXT,
            company TEXT,
            location TEXT,
            final_score INTEGER NOT NULL,
            verdict TEXT,
            salary_estimate_czk INTEGER,
            is_shortlisted INTEGER,
            status TEXT,
            private_note TEXT DEFAULT '',
            markdown_report TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(job_evaluations)")
    columns = [row[1] for row in cursor.fetchall()]

    if "source_file" not in columns:
        cursor.execute("""
            ALTER TABLE job_evaluations
            ADD COLUMN source_file TEXT
        """)

    if "private_note" not in columns:
        cursor.execute("""
            ALTER TABLE job_evaluations
            ADD COLUMN private_note TEXT DEFAULT ''
        """)

    conn.commit()
    return conn


def job_exists(conn, url: str) -> bool:
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1
        FROM job_evaluations
        WHERE url = ?
        LIMIT 1
    """, (url,))

    return cursor.fetchone() is not None


def save_evaluation(
    conn,
    url: str,
    source_file: str,
    title: str,
    company: str,
    location: str,
    final_score: int,
    verdict: str,
    salary_estimate_czk: int,
    is_shortlisted: int,
    status: str,
    private_note: str,
    markdown_report: str
):
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM job_evaluations
        WHERE url LIKE ?
        AND markdown_report = '# MOCK OUTPUT'
    """, (f"%{url}%",))

    cursor.execute("""
        INSERT OR IGNORE INTO job_evaluations (
            processed_at,
            url,
            source_file,
            title,
            company,
            location,
            final_score,
            verdict,
            salary_estimate_czk,
            is_shortlisted,
            status,
            private_note,
            markdown_report
        )
        VALUES (
            datetime('now'),
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        url,
        source_file,
        title,
        company,
        location,
        final_score,
        verdict,
        salary_estimate_czk,
        is_shortlisted,
        status,
        private_note,
        markdown_report
    ))

    conn.commit()