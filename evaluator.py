from openai import OpenAI
import json

from config import OPENAI_API_KEY, MODEL_NAME, USE_REAL_API


client = OpenAI(api_key=OPENAI_API_KEY)


def compensation_score(x: int) -> int:
    if x <= 50_000:
        return 0

    if x >= 125_000:
        return 15

    return round(x / 5000 - 10)


def component_score_and_comment(components, key):
    value = components.get(key, {})

    if isinstance(value, dict):
        return int(value.get("score", 0)), value.get("comment", "")

    if isinstance(value, (int, float)):
        return int(value), ""

    return 0, ""


def safe_list(data, key):
    value = data.get(key, [])

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [value]

    return []


def evaluate_job(
    url: str,
    prompt: str,
    job_text: str,
    private_note: str
):
    if not USE_REAL_API:
        row = {
            "mock": "mock_app",
            "title": "Mock title",
            "company": "Mock company",
            "location": "Mock location",
            "final_score": 42,
            "verdict": "Mock verdict",
            "salary_estimate_czk": 70000,
        }
        markdown = "# MOCK OUTPUT"

        return markdown, row

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": (
                    prompt
                    + "\n\nTEXT INZERATU:\n"
                    + job_text
                    + "\n\nSOUKROMÁ POZNÁMKA:\n"
                    + private_note
                ),
            }
        ],
        response_format={"type": "json_object"},
        timeout=120,
    )

    data = json.loads(response.choices[0].message.content)

    components = data.get("components", {})

    salary_estimate = int(data.get("salary_estimate_czk", 0))
    comp_score = compensation_score(salary_estimate)

    modeling_score, modeling_comment = component_score_and_comment(
        components, "modeling_relevance"
    )
    remote_score, remote_comment = component_score_and_comment(
        components, "remote_location_fit"
    )
    technical_score, technical_comment = component_score_and_comment(
        components, "technical_fit"
    )
    learning_score, learning_comment = component_score_and_comment(
        components, "learning_growth_potential"
    )
    bullshit_score, bullshit_comment = component_score_and_comment(
        components, "bullshit_risk_penalty"
    )
    reporting_score, reporting_comment = component_score_and_comment(
        components, "reporting_heavy_penalty"
    )
    english_score, english_comment = component_score_and_comment(
        components, "english_client_facing_penalty"
    )

    component_rows = [
        (
            "Modeling relevance",
            "0 až 30",
            modeling_score,
            modeling_comment,
        ),
        (
            "Remote/location fit",
            "0 až 25",
            remote_score,
            remote_comment,
        ),
        (
            "Technical fit",
            "0 až 20",
            technical_score,
            technical_comment,
        ),
        (
            "Learning/growth potential",
            "0 až 10",
            learning_score,
            learning_comment,
        ),
        (
            "Bullshit risk penalty",
            "-10 až 0",
            bullshit_score,
            bullshit_comment,
        ),
        (
            "Reporting-heavy penalty",
            "-10 až 0",
            reporting_score,
            reporting_comment,
        ),
        (
            "English/client-facing penalty",
            "-10 až 0",
            english_score,
            english_comment,
        ),
        (
            "Compensation realism",
            "0 až 15",
            comp_score,
            (
                f"Odhad x = {salary_estimate:,} CZK. "
                f"{data.get('salary_comment', '')}"
            ).replace(",", " "),
        ),
    ]

    final_score = sum(row[2] for row in component_rows)

    calculation = " + ".join(
        str(row[2]) for row in component_rows
    ).replace("+ -", "- ")

    positives = "\n".join(
        f"- {item}"
        for item in safe_list(data, "main_positives")
    )

    risks = "\n".join(
        f"- {item}"
        for item in safe_list(data, "main_risks")
    )

    table = (
        "| Komponenta | Rozsah | Skóre | Komentář |\n"
        "|---|---:|---:|---|\n"
    )

    for name, score_range, score, comment in component_rows:
        table += (
            f"| {name} "
            f"| {score_range} "
            f"| {score} "
            f"| {comment} |\n"
        )

    markdown = f"""# Job evaluation

URL: {url}

## 1. Final score
- Skóre: {final_score}/100
- Výpočet: {calculation} = {final_score}

## 2. Component scoring

{table}

## 3. Verdikt
{data.get("verdict", "")}

## 4. Hlavní důvody pro
{positives}

## 5. Hlavní rizika
{risks}

## 6. Dopad soukromé poznámky
{data.get("private_note_impact", "")}

## 7. Pravděpodobnost modelovací práce
{data.get("modeling_probability", "")}

## 8. Riziko bullshit role
{data.get("bullshit_risk", "")}

## 9. Doporučená CV varianta
{data.get("recommended_cv_variant", "")}

## 10. Stručné doporučení
{data.get("final_recommendation", "")}
"""

    row = {
        "mock": "",
        "title": data.get("title", ""),
        "company": data.get("company", ""),
        "location": data.get("location", ""),
        "final_score": final_score,
        "verdict": data.get("verdict", ""),
        "salary_estimate_czk": salary_estimate,
    }

    return markdown, row