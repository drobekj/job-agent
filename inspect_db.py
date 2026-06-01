import sqlite3

from config import DATABASE_PATH


conn = sqlite3.connect(DATABASE_PATH)

cursor = conn.cursor()

cursor.execute("""
    SELECT
        id,
        processed_at,
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
        url
    FROM job_evaluations
    ORDER BY id DESC
    LIMIT 10
""")

rows = cursor.fetchall()

print()
print("=" * 120)
print(f"TOTAL ROWS LOADED: {len(rows)}")
print("=" * 120)
print()

for row in rows:

    (
        job_id,
        processed_at,
        source_file,
        title,
        company,
        location,
        final_score,
        verdict,
        salary_estimate,
        is_shortlisted,
        status,
        private_note,
        markdown_report,
        url
    ) = row

    is_mock = markdown_report == "# MOCK OUTPUT"

    markdown_preview = (
        markdown_report[:120].replace("\n", " ")
        if markdown_report
        else ""
    )

    print(f"ID:               {job_id}")
    print(f"Processed:        {processed_at}")
    print(f"Source:           {source_file}")
    print(f"Title:            {title}")
    print(f"Company:          {company}")
    print(f"Location:         {location}")
    print(f"Score:            {final_score}")
    print(f"Verdict:          {verdict}")
    print(f"Salary estimate:  {salary_estimate} CZK")
    print(f"Shortlisted:      {bool(is_shortlisted)}")
    print(f"Status:           {status}")
    print(f"Private note:     {private_note}")
    print(f"Mock output:      {is_mock}")
    print(f"URL:              {url}")
    #print(f"Markdown preview: {markdown_preview}")
    print("-" * 120)

conn.close()