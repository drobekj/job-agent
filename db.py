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


def get_job_by_url(conn, url: str):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            url,
            verdict,
            status,
            markdown_report
        FROM job_evaluations
        WHERE url = ?
        LIMIT 1
    """, (url,))

    row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "url": row[1],
        "verdict": row[2],
        "status": row[3],
        "markdown_report": row[4],
    }


def has_ai_evaluation(conn, url: str) -> bool:
    job = get_job_by_url(conn, url)

    if job is None:
        return False

    verdict = job.get("verdict") or ""
    status = job.get("status") or ""
    markdown_report = job.get("markdown_report") or ""

    if verdict.strip() == "":
        return False

    if verdict.strip() == "":
        return False
    
    return True


def mark_job_as_repeated(conn, url: str) -> None:
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE job_evaluations
        SET status = 'repeated'
        WHERE url = ?
    """, (url,))

    conn.commit()


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
    markdown_report: str,
):
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM job_evaluations
        WHERE url = ?
        AND markdown_report = '# MOCK OUTPUT'
    """, (url + "mock_app",))

    cursor.execute("""
        INSERT INTO job_evaluations (
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
        ON CONFLICT(url) DO UPDATE SET
            processed_at = datetime('now'),
            source_file = excluded.source_file,
            title = excluded.title,
            company = excluded.company,
            location = excluded.location,
            final_score = excluded.final_score,
            verdict = excluded.verdict,
            salary_estimate_czk = excluded.salary_estimate_czk,
            is_shortlisted = excluded.is_shortlisted,
            status = excluded.status,
            private_note = excluded.private_note,
            markdown_report = excluded.markdown_report
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
        markdown_report,
    ))

    conn.commit()