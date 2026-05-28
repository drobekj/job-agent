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
            title TEXT,
            company TEXT,
            location TEXT,
            final_score INTEGER NOT NULL,
            verdict TEXT,
            salary_estimate_czk INTEGER,
            is_shortlisted INTEGER,
            status TEXT,
            markdown_report TEXT
        )
    """)

    conn.commit()
    return conn

def job_exists(
    conn,
    url: str
) -> bool:

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
    title: str,
    company: str,
    location: str,
    final_score: int,
    verdict: str,
    salary_estimate_czk: int,
    is_shortlisted: int,
    status: str,
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
            title,
            company,
            location,
            final_score,
            verdict,
            salary_estimate_czk,
            is_shortlisted,
            status,
            markdown_report
        )
        VALUES (
            datetime('now'),
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        url,
        title,
        company,
        location,
        final_score,
        verdict,
        salary_estimate_czk,
        is_shortlisted,
        status,
        markdown_report
    ))

    conn.commit()