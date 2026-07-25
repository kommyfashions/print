import json
from pathlib import Path
from datetime import datetime
from config import DATA_DIR

AGG_DIR = DATA_DIR / "aggregates"
SKU_TOTALS_FILE = AGG_DIR / "sku_totals.json"
COURIER_TOTALS_FILE = AGG_DIR / "courier_totals.json"


def _load_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def apply_run_delta(run_sku_counts, run_courier_counts):
    """
    This is the ONLY place where stats are mutated.
    Called ONLY from PROCESS.
    """

    sku_totals = _load_json(SKU_TOTALS_FILE)
    courier_totals = _load_json(COURIER_TOTALS_FILE)

    today = datetime.now().strftime("%Y-%m-%d")

    # SKU totals
    day_bucket = sku_totals.get(today, {})
    for sku, count in run_sku_counts.items():
        day_bucket[sku] = day_bucket.get(sku, 0) + count
    sku_totals[today] = day_bucket

    # Courier totals (today only)
    courier_bucket = courier_totals.get(today, {})
    for courier, count in run_courier_counts.items():
        courier_bucket[courier] = courier_bucket.get(courier, 0) + count
    courier_totals[today] = courier_bucket

    _save_json(SKU_TOTALS_FILE, sku_totals)
    _save_json(COURIER_TOTALS_FILE, courier_totals)


def load_today_sku_totals():
    today = datetime.now().strftime("%Y-%m-%d")
    return _load_json(SKU_TOTALS_FILE).get(today, {})


def load_last_30_days_sku_totals():
    all_days = _load_json(SKU_TOTALS_FILE)
    totals = {}

    for day_data in all_days.values():
        for sku, count in day_data.items():
            totals[sku] = totals.get(sku, 0) + count

    return totals


def load_today_courier_totals():
    today = datetime.now().strftime("%Y-%m-%d")
    return _load_json(COURIER_TOTALS_FILE).get(today, {})
