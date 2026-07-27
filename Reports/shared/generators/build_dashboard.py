"""
DurianX Report Builder
======================
Usage:
    python build_dashboard.py --store tua_deum_chek

Reads CSVs from stores/<store>/data/ and regenerates stores/<store>/index.html
from the shared template.

TODO: Replace static data in index.html with Jinja2 template rendering.
"""

import argparse
import json
import os
import csv

STORES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "stores")

def load_store_meta(store_id):
    meta_path = os.path.join(STORES_DIR, store_id, "store.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_csv(store_id, filename):
    path = os.path.join(STORES_DIR, store_id, "data", filename)
    if not os.path.exists(path):
        print(f"  [WARN] Missing: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def build(store_id):
    print(f"Building dashboard for store: {store_id}")
    meta    = load_store_meta(store_id)
    revenue = load_csv(store_id, "revenue.csv")
    phones  = load_csv(store_id, "phone_lead.csv")

    print(f"  Revenue rows:    {len(revenue)}")
    print(f"  Phone lead rows: {len(phones)}")
    print(f"  Store name:      {meta['name_kh']}")
    # TODO: render Jinja2 template and write to stores/<store_id>/index.html
    print("  [INFO] Template rendering not yet implemented.")
    print(f"  Dashboard lives at: stores/{store_id}/index.html")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DurianX Dashboard Builder")
    parser.add_argument("--store", required=True, help="Store ID (e.g. tua_deum_chek)")
    args = parser.parse_args()
    build(args.store)
