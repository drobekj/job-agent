import sqlite3

conn = sqlite3.connect("jobs.db")
cur = conn.cursor()

cur.execute("""
SELECT private_note
FROM job_evaluations
WHERE id=194
""")

for row in cur.fetchall():
    print(row)
    print()

conn.close()