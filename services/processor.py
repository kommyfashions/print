import pdfplumber
from collections import defaultdict
from datetime import datetime
from pypdf import PdfWriter
import copy

from config import OUTPUT_DIR, TIER1_MIN_PAGES, FLIP_LAST_PAGE_TIER1
from services.sku_service import normalize_sku, extract_size, size_sort_key
from services.pdf_service import load_reader
from services.courier_service import load_courier_config, extract_courier
from services.stats_service import apply_run_delta


def process_pdfs(pdf_files):
    sku_pages = defaultdict(list)
    courier_counts = defaultdict(int)
    readers = []

    courier_rules = load_courier_config()

    # ---------- READ & INDEX ----------
    for pdf_idx, pdf_path in enumerate(pdf_files):
        reader = load_reader(pdf_path)
        readers.append(reader)

        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                text = (page.extract_text() or "").replace("\n", " ")

                if "Product Details" not in text:
                    continue

                parts = text.split("SKU Size Qty Color Order No.")
                if len(parts) < 2:
                    continue

                raw_sku = parts[1].split()[0]
                sku = normalize_sku(raw_sku)
                size = extract_size(text)

                courier = extract_courier(text, courier_rules)
                courier_counts[courier] += 1

                sku_pages[sku].append({
                    "reader": pdf_idx,
                    "page": page_idx,
                    "size": size
                })

    # ---------- APPLY STATS (ONLY HERE) ----------
    run_sku_counts = {sku: len(pages) for sku, pages in sku_pages.items()}
    apply_run_delta(run_sku_counts, courier_counts)

    # ---------- SPLIT TIERS ----------
    tier1 = {k: v for k, v in sku_pages.items() if len(v) >= TIER1_MIN_PAGES}
    tier2 = {k: v for k, v in sku_pages.items() if len(v) < TIER1_MIN_PAGES}

    tier1_sorted = sorted(tier1.keys(), key=lambda k: -len(tier1[k]))
    tier2_sorted = sorted(tier2.keys())

    run_id = datetime.now().strftime("RUN_%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    master_writer = PdfWriter()
    tier1_writer = PdfWriter()
    tier2_writer = PdfWriter()

    # ---------- TIER 1 ----------
    for sku in tier1_sorted:
        pages = sorted(tier1[sku], key=lambda x: size_sort_key(x["size"]))
        for idx, p in enumerate(pages):
            original = readers[p["reader"]].pages[p["page"]]
            page1 = copy.copy(original)
            page2 = copy.copy(original)

            if FLIP_LAST_PAGE_TIER1 and idx == len(pages) - 1:
                page1.rotate(180)
                page2.rotate(180)

            master_writer.add_page(page1)
            tier1_writer.add_page(page2)

    # ---------- TIER 2 ----------
    for sku in tier2_sorted:
        pages = sorted(tier2[sku], key=lambda x: size_sort_key(x["size"]))
        for p in pages:
            original = readers[p["reader"]].pages[p["page"]]
            master_writer.add_page(copy.copy(original))
            tier2_writer.add_page(copy.copy(original))

    for name, writer in {
        "MASTER_PRINT.pdf": master_writer,
        "TIER1_HIGH_VOLUME.pdf": tier1_writer,
        "TIER2_LOW_VOLUME.pdf": tier2_writer
    }.items():
        with open(run_dir / name, "wb") as f:
            writer.write(f)

    return run_id
