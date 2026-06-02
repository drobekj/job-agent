import sqlite3

conn = sqlite3.connect("jobs.db")

conn.execute("""
UPDATE job_evaluations
SET final_score = 91
WHERE id = 158
""")

conn.commit()
conn.close()