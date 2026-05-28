import sqlite3

from config import DATABASE_PATH


conn = sqlite3.connect(DATABASE_PATH)

cursor = conn.cursor()

cursor.execute("""
    SELECT
        id,
        processed_at,
        title,
        company,
        location,
        final_score,
        verdict,
        salary_estimate_czk,
        is_shortlisted,
        status,
        url
    FROM job_evaluations
    ORDER BY id DESC
    LIMIT 10
""")

rows = cursor.fetchall()

print()

for row in rows:
    (
    job_id,
    processed_at,
    title,
    company,
    location,
    final_score,
    verdict,
    salary_estimate,
    is_shortlisted,
    status,
    url
    ) = row 

    print(f"ID: {job_id}")
    print(f"Processed: {processed_at}")
    print(f"Title: {title}")
    print(f"Company: {company}")
    print(f"Location: {location}")
    print(f"Score: {final_score}")
    print(f"Verdict: {verdict}")
    print(f"Salary estimate: {salary_estimate} CZK")
    print(f"Shortlisted: {bool(is_shortlisted)}")
    print(f"Status: {status}")
    print(f"URL: {url}")
    print("-" * 80)

conn.close()