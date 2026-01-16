import json
import pandas as pd
import spacy
from spacy.matcher import Matcher

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def build_matcher(nlp):
    matcher = Matcher(nlp.vocab)

    # ACTION patterns
    action_patterns = [
        [{"LEMMA": {"IN": ["replace", "clean", "adjust", "tighten", "lubricate", "inspect", "reset", "change", "calibrate", "remove", "top"]}}],
        [{"LOWER": {"IN": ["replaced", "cleaned", "adjusted", "tightened", "lubricated", "inspected", "reset", "changed", "recalibrated", "removed", "topped"]}}],
    ]
    matcher.add("ACTION", action_patterns)

    # COMPONENT patterns
    component_patterns = [
        [{"LOWER": {"IN": ["pump", "seal", "belt", "bearing", "coolant", "filter", "wiring", "motor", "reservoir", "tool", "roller", "oil"]}}],
        [{"LOWER": "coolant"}, {"LOWER": "filter"}],
        [{"LOWER": "loose"}, {"LOWER": "wiring"}],
    ]
    matcher.add("COMPONENT", component_patterns)

    # SYMPTOM patterns
    symptom_patterns = [
        [{"LOWER": {"IN": ["overheating", "vibration", "noise", "leakage", "leak", "alarm", "tripped", "jammed", "misalignment", "contamination", "pressure"]}}],
        [{"LOWER": "pressure"}, {"LOWER": {"IN": ["low", "drop"]}}],
        [{"LOWER": "poor"}, {"LOWER": "finish"}],
    ]
    matcher.add("SYMPTOM", symptom_patterns)

    return matcher


matcher = build_matcher(nlp)


def extract_fields(text: str) -> dict:
    doc = nlp(text)
    matches = matcher(doc)

    actions, components, symptoms = set(), set(), set()

    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        span = doc[start:end].text.strip()

        if label == "ACTION":
            actions.add(span)
        elif label == "COMPONENT":
            components.add(span)
        elif label == "SYMPTOM":
            symptoms.add(span)

    status = []
    lowered = text.lower()
    if "monitor" in lowered:
        status.append("monitor")
    if "tested ok" in lowered:
        status.append("tested_ok")
    if "scheduled" in lowered:
        status.append("scheduled")
    if "reset" in lowered:
        status.append("reset_done")

    return {
        "actions": sorted(actions),
        "components": sorted(components),
        "symptoms": sorted(symptoms),
        "status": status
    }


def run_extraction(input_csv: str, output_jsonl: str):
    df = pd.read_csv(input_csv)
    text_col = "notes_clean" if "notes_clean" in df.columns else "notes"

    records = []

    for _, row in df.iterrows():
        extracted = extract_fields(str(row[text_col]))
        record = {
            "log_id": int(row["log_id"]),
            "machine": row["machine"],
            "text": row[text_col],
            "extracted": extracted
        }
        records.append(record)

    with open(output_jsonl, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    print("Saved:", output_jsonl)
    print("Sample record:")
    print(json.dumps(records[0], indent=2))


if __name__ == "__main__":
    input_file = "data/processed/maintenance_logs_cleaned.csv"
    output_file = "outputs/extracted_fields.jsonl"
    run_extraction(input_file, output_file)
