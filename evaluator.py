from openai import OpenAI
import json
from config import (OPENAI_API_KEY, MODEL_NAME)

client = OpenAI(api_key=OPENAI_API_KEY)

def compensation_score(x: int) -> int:

    if x <= 50_000:
        return 0

    if x >= 125_000:
        return 15

    return round(x / 5000 - 10)


def evaluate_job(
    url: str,
    prompt: str,
    job_text: str,
    private_note: str
):

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
                )
            }
        ],
        response_format={"type": "json_object"}
    )

    data = json.loads(
        response.choices[0].message.content
    )

    components = data["components"]

    salary_estimate = int(
        data["salary_estimate_czk"]
    )

    comp_score = compensation_score(
        salary_estimate
    )

    component_rows = [
        (
            "Modeling relevance",
            "0 až 30",
            components["modeling_relevance"]["score"],
            components["modeling_relevance"]["comment"]
        ),

        (
            "Remote/location fit",
            "0 až 25",
            components["remote_location_fit"]["score"],
            components["remote_location_fit"]["comment"]
        ),

        (
            "Technical fit",
            "0 až 20",
            components["technical_fit"]["score"],
            components["technical_fit"]["comment"]
        ),

        (
            "Learning/growth potential",
            "0 až 10",
            components["learning_growth_potential"]["score"],
            components["learning_growth_potential"]["comment"]
        ),

        (
            "Bullshit risk penalty",
            "-10 až 0",
            components["bullshit_risk_penalty"]["score"],
            components["bullshit_risk_penalty"]["comment"]
        ),

        (
            "Reporting-heavy penalty",
            "-10 až 0",
            components["reporting_heavy_penalty"]["score"],
            components["reporting_heavy_penalty"]["comment"]
        ),

        (
            "English/client-facing penalty",
            "-10 až 0",
            components["english_client_facing_penalty"]["score"],
            components["english_client_facing_penalty"]["comment"]
        ),

        (
            "Compensation realism",
            "0 až 15",
            comp_score,
            (
                f"Odhad x = "
                f"{salary_estimate:,} CZK. "
                f"{data['salary_comment']}"
            ).replace(",", " ")
        ),
    ]

    final_score = sum(
        row[2] for row in component_rows
    )

    calculation = " + ".join(
        str(row[2]) for row in component_rows
    ).replace("+ -", "- ")

    positives = "\n".join(
        f"- {item}"
        for item in data["main_positives"]
    )

    risks = "\n".join(
        f"- {item}"
        for item in data["main_risks"]
    )

    table = (
        "| Komponenta | Rozsah "
        "| Skóre | Komentář |\n"
    )

    table += (
        "|---|---:|---:|---|\n"
    )

    for (
        name,
        score_range,
        score,
        comment
    ) in component_rows:

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
{data["verdict"]}

## 4. Hlavní důvody pro
{positives}

## 5. Hlavní rizika
{risks}

## 6. Dopad soukromé poznámky
{data["private_note_impact"]}

## 7. Pravděpodobnost modelovací práce
{data["modeling_probability"]}

## 8. Riziko bullshit role
{data["bullshit_risk"]}

## 9. Doporučená CV varianta
{data["recommended_cv_variant"]}

## 10. Stručné doporučení
{data["final_recommendation"]}
"""
    row = {
        "title": data.get("title", ""),
        "company": data.get("company", ""),
        "location": data.get("location", ""),

        "final_score": final_score,
        "verdict": data["verdict"],
        "salary_estimate_czk": salary_estimate
    }

    return markdown, row