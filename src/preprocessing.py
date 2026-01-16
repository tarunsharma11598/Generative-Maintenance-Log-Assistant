import re
import pandas as pd


def clean_text(text: str) -> str:
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s\.\,\;\:\-\/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_csv(input_path: str, output_path: str):
    df = pd.read_csv(input_path)

    if "notes" not in df.columns:
        raise ValueError("CSV must contain a 'notes' column")

    df["notes_clean"] = df["notes"].apply(clean_text)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    input_file = "data/raw/maintenance_logs.csv"
    output_file = "data/processed/maintenance_logs_cleaned.csv"

    df = preprocess_csv(input_file, output_file)
    print("Saved:", output_file)
    print(df[["log_id", "machine", "notes_clean"]].head())
