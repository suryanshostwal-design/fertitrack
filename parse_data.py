import openpyxl
import pandas as pd
import json
import os
from datetime import datetime

CRU_FOLDER = os.path.join(os.path.dirname(__file__), "data")

def parse_prices():
    """Parse the historical prices Excel file and return JSON-ready data."""
    path = None
    for f in os.listdir(CRU_FOLDER):
        if "historical-prices" in f and f.endswith(".xlsx") and "averages" not in f and "(1)" not in f:
            path = os.path.join(CRU_FOLDER, f)
            break
    if not path:
        return {}

    wb = openpyxl.load_workbook(path)
    ws = wb['All_W']
    rows = list(ws.iter_rows(values_only=True))

    # Row 0: product name (merged, so only first col of group has value)
    # Row 1: location
    # Row 2: unit
    # Row 3: Year, Quarter, Month, PriceDate, Max, Min, Avg, ...
    # Row 4+: data

    product_row = rows[0]
    location_row = rows[1]
    header_row = rows[3]

    # Build column mapping: col index -> (product, location)
    col_map = {}
    current_product = None
    current_location = None
    for i, val in enumerate(product_row):
        if val and val != 'Back to Contents':
            current_product = val
        if i < len(location_row) and location_row[i]:
            current_location = location_row[i]
        if i >= 4 and current_product:
            col_map[i] = (current_product, current_location)

    # Group columns by (product, location) -> list of (avg_col_index)
    series = {}
    for i, (prod, loc) in col_map.items():
        if header_row[i] == 'Avg':
            key = f"{prod} | {loc}"
            series[key] = i

    # Parse data rows
    data = {}
    for row in rows[4:]:
        date_val = row[3]
        if not date_val or not isinstance(date_val, datetime):
            continue
        date_str = date_val.strftime("%Y-%m-%d")
        for key, col_idx in series.items():
            val = row[col_idx]
            if val and val != '':
                try:
                    val = float(val)
                except:
                    continue
                if key not in data:
                    data[key] = []
                data[key].append({"date": date_str, "price": val})

    # Limit to last 5 years for performance
    cutoff = "2021-01-01"
    filtered = {}
    for key, points in data.items():
        pts = [p for p in points if p["date"] >= cutoff]
        if len(pts) > 5:
            filtered[key] = pts

    return filtered


def get_product_list(data):
    products = set()
    for key in data.keys():
        prod = key.split(" | ")[0]
        products.add(prod)
    return sorted(products)


def get_latest_prices(data):
    latest = {}
    for key, points in data.items():
        if points:
            last = points[-1]
            prev = points[-2] if len(points) > 1 else None
            change = None
            if prev and prev["price"]:
                change = round(((last["price"] - prev["price"]) / prev["price"]) * 100, 2)
            latest[key] = {
                "price": last["price"],
                "date": last["date"],
                "change": change
            }
    return latest


if __name__ == "__main__":
    data = parse_prices()
    print(f"Parsed {len(data)} price series")
    print("Sample keys:", list(data.keys())[:5])
