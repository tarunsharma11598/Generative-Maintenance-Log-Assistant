import json
import os
from openai import OpenAI

# Make sure key exists
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Set it in your environment variable first.")

client = OpenAI(api_key=api_key)

INPUT_JSONL = "outputs/extracted_fields.jsonl"
OUTPUT_JSONL = "outputs/final_reports.jsonl"

SYSTEM_PROMPT = """You are a maintenance analysis assistant.
Return ONLY valid JSON that matches the schema exactly.
Do not add extra keys. Do not wrap in markdown.

Schema:
{
  "issue_summary": string,
  "likely_cause": string,
  "recommended_actions": [string],
  "priority": "low" | "medium" | "high",
  "safety_risk": "low" | "medium" | "high"
}
"""

def build_user_prompt(record: dict) -> str:
    return f"""
Maintenance log:
Machine: {record.get("machine")}
Text: {record.get("text")}

Extracted signals:
Actions: {record["extracted"].get("actions")}
Components: {record["extracted"].get("components")}
Symptoms: {record["extracted"].get("symptoms")}
Status: {record["extracted"].get("status")}

Task:
Create a concise maintenance report in the required JSON schema.
- issue_summary: 1 sentence
- likely_cause: best guess from text/signals (use 'unknown' if unclear)
- recommended_actions: 2–4 short action steps
- priority and safety_risk based on severity
""".strip()

def call_llm(prompt: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

def main():
    print("LLM summarization started...")

    if not os.path.exists(INPUT_JSONL):
        raise FileNotFoundError(f"Missing input file: {INPUT_JSONL}")

    os.makedirs("outputs", exist_ok=True)

    results = []
    with open(INPUT_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            log_id = record.get("log_id")
            print("Calling LLM for log_id:", log_id)
            report = call_llm(build_user_prompt(record))
            results.append({
                "log_id": log_id,
                "machine": record.get("machine"),
                "report": report
            })

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print("Saved:", OUTPUT_JSONL)
    print("Sample final report:")
    print(json.dumps(results[0], indent=2))

if __name__ == "__main__":
    main()
