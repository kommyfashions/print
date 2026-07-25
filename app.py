from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from pathlib import Path

from config import UPLOAD_DIR, OUTPUT_DIR
from services.processor import process_pdfs
from services.stats_service import (
    load_today_sku_totals,
    load_last_30_days_sku_totals,
    load_today_courier_totals
)

app = Flask(__name__)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    today = load_today_sku_totals()
    last_30 = load_last_30_days_sku_totals()
    courier_today = load_today_courier_totals()

    summary = sorted(
        set(today) | set(last_30),
        key=lambda x: last_30.get(x, 0),
        reverse=True
    )

    return render_template(
        "index.html",
        outputs=None,
        summary=summary,
        today=today,
        last_30=last_30,
        courier_today=courier_today
    )


@app.route("/process", methods=["POST"])
def process():
    files = request.files.getlist("pdfs")
    saved = []

    for f in files:
        path = UPLOAD_DIR / f.filename
        f.save(path)
        saved.append(path)

    run_id = process_pdfs(saved)

    # 🔐 PRG: redirect after POST
    return redirect(url_for("result", run_id=run_id))


@app.route("/result/<run_id>")
def result(run_id):
    run_dir = OUTPUT_DIR / run_id

    today = load_today_sku_totals()
    last_30 = load_last_30_days_sku_totals()
    courier_today = load_today_courier_totals()

    summary = sorted(
        set(today) | set(last_30),
        key=lambda x: last_30.get(x, 0),
        reverse=True
    )

    outputs = {
        "run_id": run_id,
        "files": list(run_dir.glob("*.pdf"))
    }

    return render_template(
        "index.html",
        outputs=outputs,
        summary=summary,
        today=today,
        last_30=last_30,
        courier_today=courier_today
    )


@app.route("/download/<run_id>/<filename>")
def download(run_id, filename):
    return send_from_directory(OUTPUT_DIR / run_id, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=False)
