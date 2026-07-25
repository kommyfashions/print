import pandas as pd
import re
from config import SKU_EXCEL_PATH

sku_df = pd.read_excel(SKU_EXCEL_PATH)
sku_df.columns = [c.strip() for c in sku_df.columns]

SKU_MAP = dict(
    zip(
        sku_df["RawSKU"].astype(str).str.strip(),
        sku_df["NormalizedSKU"].astype(str).str.strip()
    )
)

def normalize_sku(raw_sku: str) -> str:
    return SKU_MAP.get(raw_sku, raw_sku)

def extract_size(text: str) -> str:
    match = re.search(
        r"Product Details\s+SKU Size Qty Color Order No\.\s+[^\s]+\s+(.+?)\s+\d+\s+",
        text
    )
    return match.group(1).strip() if match else ""

def size_sort_key(size: str) -> float:
    nums = re.findall(r"\d+\.?\d*", size)
    return float(nums[0]) if nums else 999.0
