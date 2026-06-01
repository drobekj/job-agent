import sqlite3

conn = sqlite3.connect("jobs.db")

conn.execute("""
UPDATE job_evaluations
SET status = "applied"
WHERE id = 143
""")

conn.commit()
conn.close()