#!/usr/bin/env python3
"""
Consolidated macro indicator collector — FRED + ECOS + BLS → raw.db macro_indicators

Replaces: old collect_macro.py (yfinance), collect_fred.py, collect_ecos.py
stdlib only (urllib, json, sqlite3) + load_env.

Usage:
    python collect_macro.py                    # all sources, 365 days
    python collect_macro.py --source fred      # FRED only
    python collect_macro.py --source ecos      # ECOS only
    python collect_macro.py --source bls       # BLS only
    python collect_macro.py --days 90          # last 90 days
"""

import argparse
import json
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# ── load_env import (same directory) ──
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_env import get_key

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "raw.db"

# ═══════════════════════════════════════════════════════════════════
# FRED series definitions (27 series)
# ═══════════════════════════════════════════════════════════════════

FRED_SERIES = {
    # Interest rates
    "DFF":    {"category": "interest_rate", "unit": "%",         "name": "Federal Funds Rate"},
    "DGS2":   {"category": "interest_rate", "unit": "%",         "name": "2Y Treasury"},
    "DGS10":  {"category": "interest_rate", "unit": "%",         "name": "10Y Treasury"},
    "T10Y2Y": {"category": "interest_rate", "unit": "%",         "name": "10Y-2Y Spread"},
    "T10Y3M": {"category": "interest_rate", "unit": "%",         "name": "10Y-3M Spread"},
    # FX
    "DEXKOUS":  {"category": "exchange_rate", "unit": "KRW/USD", "name": "USD/KRW"},
    "DEXJPUS":  {"category": "exchange_rate", "unit": "JPY/USD", "name": "USD/JPY"},
    "DEXUSEU":  {"category": "exchange_rate", "unit": "USD/EUR", "name": "EUR/USD"},
    "DTWEXBGS": {"category": "exchange_rate", "unit": "index",   "name": "USD Index (Broad)"},
    # Commodities
    "DCOILWTICO":       {"category": "commodity", "unit": "USD/barrel", "name": "WTI Crude Oil"},
    "DCOILBRENTEU":     {"category": "commodity", "unit": "USD/barrel", "name": "Brent Crude"},
    "DHHNGSP":          {"category": "commodity", "unit": "USD/MMBtu",  "name": "Henry Hub Natural Gas"},
    "GOLDAMGBD228NLBM": {"category": "commodity", "unit": "USD/oz",    "name": "Gold Price"},
    # Inflation
    "CPIAUCSL": {"category": "inflation", "unit": "index", "name": "CPI (All Urban)"},
    "CPILFESL": {"category": "inflation", "unit": "index", "name": "Core CPI"},
    "PPIACO":   {"category": "inflation", "unit": "index", "name": "PPI (All Commodities)"},
    "PCEPILFE": {"category": "inflation", "unit": "index", "name": "Core PCE"},
    # Employment
    "UNRATE": {"category": "employment", "unit": "%",         "name": "Unemployment Rate"},
    "PAYEMS": {"category": "employment", "unit": "thousands", "name": "Nonfarm Payrolls"},
    "ICSA":   {"category": "employment", "unit": "persons",   "name": "Initial Jobless Claims"},
    # GDP / economic activity
    "GDP":     {"category": "gdp", "unit": "billions", "name": "US GDP"},
    "INDPRO":  {"category": "gdp", "unit": "index",    "name": "Industrial Production"},
    "UMCSENT": {"category": "gdp", "unit": "index",    "name": "Consumer Sentiment"},
    # Credit spreads
    "BAMLH0A0HYM2": {"category": "credit_spread", "unit": "%", "name": "US HY OAS"},
    "BAMLC0A4CBBB":  {"category": "credit_spread", "unit": "%", "name": "BBB OAS"},
    # Liquidity
    "WALCL": {"category": "liquidity", "unit": "millions", "name": "Fed Balance Sheet"},
    "M2SL":  {"category": "liquidity", "unit": "billions", "name": "M2 Money Supply"},
}

# ═══════════════════════════════════════════════════════════════════
# ECOS series definitions (8 series)
# ═══════════════════════════════════════════════════════════════════

ECOS_SERIES = {
    # Interest rates
    "722Y001/0101000":   {"category": "interest_rate", "unit": "%",      "name": "Base Rate"},
    "817Y002/010200000": {"category": "interest_rate", "unit": "%",      "name": "KTB 3Y"},
    "817Y002/010210000": {"category": "interest_rate", "unit": "%",      "name": "KTB 10Y"},
    # FX
    "731Y003/0000001":   {"category": "exchange_rate", "unit": "KRW",    "name": "KRW/USD"},
    "731Y003/0000053":   {"category": "exchange_rate", "unit": "KRW",    "name": "KRW/JPY(100)"},
    # Inflation
    "901Y009/0":         {"category": "inflation",     "unit": "index",  "name": "KR CPI"},
    "901Y010/0":         {"category": "inflation",     "unit": "index",  "name": "KR PPI"},
    # Liquidity
    "101Y003/BBFA00":    {"category": "liquidity",     "unit": "bn KRW", "name": "KR M2"},
}

ECOS_FREQ_MAP = {
    "interest_rate": "D",
    "exchange_rate":  "D",
    "inflation":      "M",
    "liquidity":      "M",
}

# ═══════════════════════════════════════════════════════════════════
# BLS series definitions (4 series)
# ═══════════════════════════════════════════════════════════════════

BLS_SERIES = {
    "LNS14000000":    {"category": "employment", "unit": "%",         "name": "Unemployment Rate"},
    "CES0000000001":  {"category": "employment", "unit": "thousands", "name": "Nonfarm Payrolls"},
    "CUUR0000SA0":    {"category": "inflation",  "unit": "index",     "name": "CPI-U"},
    "CUSR0000SA0L1E": {"category": "inflation",  "unit": "index",     "name": "Core CPI"},
}


# ═══════════════════════════════════════════════════════════════════
# DB helper
# ═══════════════════════════════════════════════════════════════════

def _get_conn():
    """Open (or create) raw.db with WAL mode."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _save_rows(conn, rows):
    """INSERT OR REPLACE a list of row dicts into macro_indicators. Returns count."""
    if not rows:
        return 0
    cur = conn.cursor()
    cur.executemany(
        """INSERT OR REPLACE INTO macro_indicators
           (indicator_id, date, value, unit, country, category, source, collected_at)
           VALUES (:indicator_id, :date, :value, :unit, :country, :category, :source, :collected_at)""",
        rows,
    )
    conn.commit()
    return len(rows)


# ═══════════════════════════════════════════════════════════════════
# 1) FRED
# ═══════════════════════════════════════════════════════════════════

def fetch_fred(days=365):
    """Fetch all FRED series and write to macro_indicators (country='US', source='FRED')."""
    key = get_key("FRED_API_KEY")
    if not key:
        print("[FRED] Skipping — FRED_API_KEY not set")
        return 0

    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*50}")
    print(f"[FRED] {len(FRED_SERIES)} series, from {start_date}")
    print(f"{'='*50}")

    conn = _get_conn()
    total = 0
    ok = 0

    for i, (sid, meta) in enumerate(FRED_SERIES.items(), 1):
        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={sid}&api_key={key}&file_type=json"
            f"&observation_start={start_date}"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GapFinder/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"  [{i:2d}/{len(FRED_SERIES)}] {meta['name']:30s} — ERROR: {e}")
            time.sleep(0.2)
            continue
        except json.JSONDecodeError as e:
            print(f"  [{i:2d}/{len(FRED_SERIES)}] {meta['name']:30s} — JSON error: {e}")
            time.sleep(0.2)
            continue

        rows = []
        for obs in data.get("observations", []):
            val_str = obs.get("value", ".")
            if val_str == ".":
                continue
            try:
                rows.append({
                    "indicator_id": sid,
                    "date": obs["date"],
                    "value": float(val_str),
                    "unit": meta["unit"],
                    "country": "US",
                    "category": meta["category"],
                    "source": "FRED",
                    "collected_at": collected_at,
                })
            except (ValueError, KeyError):
                continue

        saved = _save_rows(conn, rows)
        total += saved
        if saved:
            ok += 1
        print(f"  [{i:2d}/{len(FRED_SERIES)}] {meta['name']:30s} — {saved:>4d} rows")
        time.sleep(0.2)

    conn.close()
    print(f"[FRED] Done: {ok}/{len(FRED_SERIES)} series, {total} rows")
    return total


# ═══════════════════════════════════════════════════════════════════
# 2) ECOS
# ═══════════════════════════════════════════════════════════════════

def fetch_ecos(days=365):
    """Fetch all ECOS (Bank of Korea) series and write to macro_indicators (country='KR', source='ECOS')."""
    key = get_key("ECOS_API_KEY")
    if not key:
        print("[ECOS] Skipping — ECOS_API_KEY not set")
        return 0

    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=days)
    end_date = end_dt.strftime("%Y%m%d")
    start_date = start_dt.strftime("%Y%m%d")
    collected_at = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*50}")
    print(f"[ECOS] {len(ECOS_SERIES)} series, {start_date}~{end_date}")
    print(f"{'='*50}")

    base_url = "https://ecos.bok.or.kr/api/StatisticSearch"
    conn = _get_conn()
    total = 0
    ok = 0

    for i, (series_key, meta) in enumerate(ECOS_SERIES.items(), 1):
        stat_code, item_code = series_key.split("/")
        freq = ECOS_FREQ_MAP.get(meta["category"], "M")
        indicator_id = f"ECOS:{stat_code}:{item_code}"

        url = (
            f"{base_url}/{key}/json/kr/1/1000"
            f"/{stat_code}/{freq}/{start_date}/{end_date}/{item_code}"
        )

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"  [{i}/{len(ECOS_SERIES)}] {meta['name']:20s} — ERROR: {e}")
            time.sleep(0.5)
            continue

        if "StatisticSearch" not in data:
            err = data.get("RESULT", {})
            print(f"  [{i}/{len(ECOS_SERIES)}] {meta['name']:20s} — API error: {err.get('MESSAGE', '?')}")
            time.sleep(0.5)
            continue

        rows_raw = data["StatisticSearch"].get("row", [])
        rows = []
        for r in rows_raw:
            raw_time = r.get("TIME", "")
            val_str = r.get("DATA_VALUE", "")
            # Normalize date: YYYYMMDD → YYYY-MM-DD, YYYYMM → YYYY-MM-01
            if len(raw_time) == 8:
                date_str = f"{raw_time[:4]}-{raw_time[4:6]}-{raw_time[6:8]}"
            elif len(raw_time) == 6:
                date_str = f"{raw_time[:4]}-{raw_time[4:6]}-01"
            elif len(raw_time) == 4:
                date_str = f"{raw_time}-01-01"
            else:
                date_str = raw_time
            try:
                rows.append({
                    "indicator_id": indicator_id,
                    "date": date_str,
                    "value": float(val_str),
                    "unit": meta["unit"],
                    "country": "KR",
                    "category": meta["category"],
                    "source": "ECOS",
                    "collected_at": collected_at,
                })
            except (ValueError, TypeError):
                continue

        saved = _save_rows(conn, rows)
        total += saved
        if saved:
            ok += 1
        print(f"  [{i}/{len(ECOS_SERIES)}] {meta['name']:20s} — {saved:>4d} rows")
        time.sleep(0.5)

    conn.close()
    print(f"[ECOS] Done: {ok}/{len(ECOS_SERIES)} series, {total} rows")
    return total


# ═══════════════════════════════════════════════════════════════════
# 3) BLS
# ═══════════════════════════════════════════════════════════════════

def fetch_bls(days=365):
    """Fetch BLS series via API v2 and write to macro_indicators (country='US', source='BLS')."""
    key = get_key("BLS_API_KEY")
    if not key:
        print("[BLS] Skipping — BLS_API_KEY not set")
        return 0

    now = datetime.now()
    start_year = (now - timedelta(days=days)).year
    end_year = now.year
    collected_at = now.strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{'='*50}")
    print(f"[BLS] {len(BLS_SERIES)} series, {start_year}~{end_year}")
    print(f"{'='*50}")

    api_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    series_ids = list(BLS_SERIES.keys())

    payload = json.dumps({
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": key,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "GapFinder/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"  [BLS] Network error: {e}")
        return 0
    except json.JSONDecodeError as e:
        print(f"  [BLS] JSON error: {e}")
        return 0

    if data.get("status") != "REQUEST_SUCCEEDED":
        print(f"  [BLS] API error: {data.get('message', ['unknown'])}")
        return 0

    conn = _get_conn()
    total = 0
    ok = 0

    for series_data in data.get("Results", {}).get("series", []):
        sid = series_data.get("seriesID", "")
        meta = BLS_SERIES.get(sid)
        if not meta:
            continue

        rows = []
        for item in series_data.get("data", []):
            year = item.get("year", "")
            period = item.get("period", "")  # M01..M12, M13=annual avg

            # Skip annual averages
            if period == "M13":
                continue

            # Build date from period code (M01 → 01)
            if period.startswith("M"):
                month_num = period[1:]
            else:
                month_num = "01"
            date_str = f"{year}-{month_num}-01"

            val_str = item.get("value", "")
            try:
                rows.append({
                    "indicator_id": sid,
                    "date": date_str,
                    "value": float(val_str),
                    "unit": meta["unit"],
                    "country": "US",
                    "category": meta["category"],
                    "source": "BLS",
                    "collected_at": collected_at,
                })
            except (ValueError, TypeError):
                continue

        saved = _save_rows(conn, rows)
        total += saved
        if saved:
            ok += 1
        print(f"  {meta['name']:30s} — {saved:>4d} rows")

    conn.close()
    print(f"[BLS] Done: {ok}/{len(BLS_SERIES)} series, {total} rows")
    return total


# ═══════════════════════════════════════════════════════════════════
# main
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Consolidated macro indicator collector (FRED + ECOS + BLS)"
    )
    parser.add_argument(
        "--source", choices=["all", "fred", "ecos", "bls"],
        default="all", help="Data source to fetch (default: all)"
    )
    parser.add_argument(
        "--days", type=int, default=365,
        help="Look-back period in days (default: 365)"
    )
    args = parser.parse_args()

    print(f"=== Macro Indicator Collector ===")
    print(f"  Source : {args.source}")
    print(f"  Days   : {args.days}")
    print(f"  DB     : {DB_PATH}")

    grand_total = 0

    if args.source in ("all", "fred"):
        grand_total += fetch_fred(days=args.days)

    if args.source in ("all", "ecos"):
        grand_total += fetch_ecos(days=args.days)

    if args.source in ("all", "bls"):
        grand_total += fetch_bls(days=args.days)

    print(f"\n{'='*50}")
    print(f"=== Grand total: {grand_total} rows saved ===")


if __name__ == "__main__":
    main()
