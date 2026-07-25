from pathlib import Path

APP_PORT = 5000

BASE_DIR = Path(__file__).parent

UPLOAD_DIR = BASE_DIR / "uploads" / "pdfs"
OUTPUT_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"

# SKU normalization
SKU_EXCEL_PATH = DATA_DIR / "sku_normalization.xlsx"

# SKU stats
SKU_STATS_DIR = DATA_DIR / "sku_stats"

# Printing logic
TIER1_MIN_PAGES = 10
FLIP_LAST_PAGE_TIER1 = True

# Retention
RETENTION_DAYS = 30
