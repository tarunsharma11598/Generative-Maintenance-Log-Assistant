import sys
from pathlib import Path
import os
import json

import pandas as pd
import streamlit as st

# MUST be first Streamlit command
st.set_page_config(page_title="Gen Log Assistant", layout="wide")

# Ensure project root is on Python path so `src.*` imports work
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

st.title("🛠️ Generative Maintenance Log Assistant")
st.caption("Upload maintenance logs → preprocess → extract signals → (optional) generate final report.")

st.sidebar.header("Settings")
use_llm = st.sidebar.toggle("Use LLM (costs money)", value=False)
st.sidebar.caption("Keep OFF for $0 demos. Turn ON only when needed.")

# Paths
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
OUTPUT_DIR = "outputs"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Imports from your pipeline
from src.preprocessing import preprocess_csv
from src.nlp_extract import run_extraction

st.info("👈 Upload a CSV file to start. The page should never be blank now.")

uploaded = st.file_uploader(
    "Upload a CSV with maintenance logs (must include a 'notes' column).",
    type=["csv"]
)

col1, col2 = st.columns(2)

def run_llm(processed_input_jsonl: str):
    """Runs LLM summarization (costs money)."""
    import src.llm_summarize as llm_mod
    llm_mod.main()
    return "outputs/final_reports.jsonl"

if uploaded:
    raw_path = os.path.join(RAW_DIR, "uploaded_logs.csv")
    with open(raw_path, "wb") as f:
        f.write(uploaded.getbuffer())

    with col1:
        st.subheader("1) Preview Raw Data")
        df_raw = pd.read_csv(raw_path)
        st.dataframe(df_raw.head(20), use_container_width=True)

    with col2:
        st.subheader("Run")
        run_btn = st.button("🚀 Run Pipeline", type="primary")

    if run_btn:
        # Step A: preprocess
        processed_path = os.path.join(PROCESSED_DIR, "uploaded_logs_cleaned.csv")
        preprocess_csv(raw_path, processed_path)
        st.success(f"Preprocessing done → {processed_path}")

        # Step B: NLP extraction
        extracted_path = os.path.join(OUTPUT_DIR, "extracted_fields.jsonl")
        run_extraction(processed_path, extracted_path)
        st.success(f"NLP extraction done → {extracted_path}")

        # Step C: Optional LLM report generation
        final_path = None
        if use_llm:
            try:
                final_path = run_llm(extracted_path)
                st.success(f"LLM report generation done → {final_path}")
            except Exception as e:
                st.error(f"LLM step failed: {e}")

        # Show extracted
        st.divider()
        st.subheader("2) Extracted Fields (JSONL)")
        extracted_records = []
        with open(extracted_path, "r", encoding="utf-8") as f:
            for line in f:
                extracted_records.append(json.loads(line))

        if extracted_records:
            st.json(extracted_records[0])
            st.dataframe(
                pd.DataFrame([{
                    "log_id": r.get("log_id"),
                    "machine": r.get("machine"),
                    "actions": ", ".join(r["extracted"].get("actions", [])),
                    "components": ", ".join(r["extracted"].get("components", [])),
                    "symptoms": ", ".join(r["extracted"].get("symptoms", [])),
                    "status": ", ".join(r["extracted"].get("status", [])),
                } for r in extracted_records]),
                use_container_width=True
            )
        else:
            st.warning("No extracted records found.")

        # Show final reports if generated
        if use_llm and final_path and os.path.exists(final_path):
            st.divider()
            st.subheader("3) Final Reports (LLM JSONL)")
            final_records = []
            with open(final_path, "r", encoding="utf-8") as f:
                for line in f:
                    final_records.append(json.loads(line))

            if final_records:
                st.json(final_records[0])
                st.dataframe(
                    pd.DataFrame([{
                        "log_id": r.get("log_id"),
                        "machine": r.get("machine"),
                        "issue_summary": r["report"].get("issue_summary"),
                        "likely_cause": r["report"].get("likely_cause"),
                        "priority": r["report"].get("priority"),
                        "safety_risk": r["report"].get("safety_risk"),
                    } for r in final_records]),
                    use_container_width=True
                )
            else:
                st.warning("No final reports found.")

else:
    st.subheader("Expected CSV format")
    st.code(
        "log_id,date,machine,notes\n"
        "1,2025-01-05,CNC-12,\"Machine stopped suddenly...\"",
        language="text"
    )

st.sidebar.divider()
st.sidebar.write("Tip: LLM OFF = free. LLM ON = small API cost per run.")
