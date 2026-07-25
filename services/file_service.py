import shutil
from datetime import datetime, timedelta
from config import UPLOAD_DIR, OUTPUT_DIR, SKU_STATS_DIR, RETENTION_DAYS


def prepare_folders():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SKU_STATS_DIR.mkdir(parents=True, exist_ok=True)


def clear_uploads():
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_old_outputs():
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)

    for folder in OUTPUT_DIR.glob("RUN_*"):
        try:
            ts = folder.name.replace("RUN_", "")
            run_time = datetime.strptime(ts, "%Y%m%d_%H%M%S")
            if run_time < cutoff:
                shutil.rmtree(folder)
        except Exception:
            continue


def cleanup_old_stats():
    cutoff = datetime.now().date() - timedelta(days=RETENTION_DAYS)

    for file in SKU_STATS_DIR.glob("RUN_*.json"):
        try:
            data = file.read_text()
            date_str = json.loads(data)["date"]
            run_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if run_date < cutoff:
                file.unlink()
        except Exception:
            continue
