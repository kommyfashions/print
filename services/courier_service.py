import pandas as pd
import re
from config import DATA_DIR

COURIER_CONFIG_FILE = DATA_DIR / "courier_config.xlsx"


def load_courier_config():
    if not COURIER_CONFIG_FILE.exists():
        return []

    df = pd.read_excel(COURIER_CONFIG_FILE)
    df.columns = [c.strip() for c in df.columns]

    required = {"CourierName", "MatchText"}
    if not required.issubset(df.columns):
        raise ValueError(
            "courier_config.xlsx must contain columns: CourierName, MatchText"
        )

    records = []
    for _, row in df.iterrows():
        name = str(row["CourierName"]).strip()
        text = str(row["MatchText"]).strip()
        if name and text:
            records.append((name, text))

    return records


def extract_courier(label_text: str, courier_rules) -> str:
    for courier_name, match_text in courier_rules:
        if re.search(rf"\b{re.escape(match_text)}\b", label_text, re.IGNORECASE):
            return courier_name
    return "UNKNOWN"
