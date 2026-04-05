#!/usr/bin/env python3
"""미국주식 데이터 수집 — yfinance 기반 (API 키 불필요).

수집 항목:
  - 시세 (price_daily)
  - 재무제표 (financials)
  - 기업 정보 (stock_master 업데이트용)
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

import yfinance as yf

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "raw.db"
RAW_DIR = Path(__file__).resolve().parent.parent / "raw" / "yahoo"


def collect_price(ticker: str, period: str = "6mo") -> dict:
    """일별 시세 수집."""
    print(f"  [{ticker}] 시세 수집 중 (기간: {period})...")
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty:
        print(f"  [{ticker}] 시세 데이터 없음!")
        return {"ticker": ticker, "prices": []}

    prices = []
    for date, row in hist.iterrows():
        prices.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })

    print(f"  [{ticker}] 시세 {len(prices)}일 수집 완료")
    return {"ticker": ticker, "prices": prices}


def collect_financials(ticker: str) -> dict:
    """분기별 재무제표 수집."""
    print(f"  [{ticker}] 재무제표 수집 중...")
    stock = yf.Ticker(ticker)

    result = {"ticker": ticker, "quarterly": []}

    # 분기 손익계산서
    try:
        qi = stock.quarterly_income_stmt
        qb = stock.quarterly_balance_sheet
        qc = stock.quarterly_cashflow

        if qi is not None and not qi.empty:
            for col in qi.columns:
                period = col.strftime("%Y-%m-%d")
                entry = {"fiscal_period": period}

                # 손익
                entry["revenue"] = _get(qi, "Total Revenue", col)
                entry["operating_income"] = _get(qi, "Operating Income", col)
                entry["net_income"] = _get(qi, "Net Income", col)
                entry["eps"] = _get(qi, "Basic EPS", col) or _get(qi, "Diluted EPS", col)

                # 재무상태표
                if qb is not None and col in qb.columns:
                    total_equity = _get(qb, "Stockholders Equity", col) or _get(qb, "Total Equity Gross Minority Interest", col)
                    total_assets = _get(qb, "Total Assets", col)
                    total_debt = _get(qb, "Total Debt", col)
                    shares = _get(qb, "Share Issued", col) or _get(qb, "Ordinary Shares Number", col)

                    if total_equity and shares:
                        entry["bps"] = round(total_equity / shares, 2)
                    if total_equity and entry.get("net_income"):
                        entry["roe"] = round((entry["net_income"] / total_equity) * 100, 2)
                    if total_debt and total_equity:
                        entry["debt_ratio"] = round((total_debt / total_equity) * 100, 2)

                # 현금흐름
                if qc is not None and col in qc.columns:
                    entry["ocf"] = _get(qc, "Operating Cash Flow", col)
                    entry["fcf"] = _get(qc, "Free Cash Flow", col)

                result["quarterly"].append(entry)

            print(f"  [{ticker}] 재무 {len(result['quarterly'])}분기 수집 완료")
        else:
            print(f"  [{ticker}] 재무제표 데이터 없음")
    except Exception as e:
        print(f"  [{ticker}] 재무 수집 오류: {e}")

    return result


def collect_info(ticker: str) -> dict:
    """기업 기본 정보 수집."""
    print(f"  [{ticker}] 기업 정보 수집 중...")
    stock = yf.Ticker(ticker)
    info = stock.info

    result = {
        "ticker": ticker,
        "name": info.get("shortName") or info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "forward_pe": info.get("forwardPE"),
        "trailing_pe": info.get("trailingPE"),
        "pb_ratio": info.get("priceToBook"),
        "business_summary": info.get("longBusinessSummary"),
        "dividend_yield": info.get("dividendYield"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "beta": info.get("beta"),
    }

    print(f"  [{ticker}] 기업 정보 수집 완료 — {result['name']}")
    return result


def _get(df, key, col):
    """DataFrame에서 안전하게 값 추출."""
    try:
        if key in df.index:
            val = df.loc[key, col]
            if val is not None and str(val) != "nan":
                return float(val)
    except Exception:
        pass
    return None


def save_to_db(conn: sqlite3.Connection, price_data: dict, fin_data: dict, info_data: dict):
    """수집된 데이터를 DB에 저장."""
    cur = conn.cursor()
    ticker = price_data["ticker"]
    now = datetime.now().strftime("%Y-%m-%d")

    # 시세 저장
    count = 0
    for p in price_data["prices"]:
        cur.execute("""
        INSERT OR REPLACE INTO price_daily (ticker, date, open, high, low, close, volume, market_cap)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticker, p["date"], p["open"], p["high"], p["low"], p["close"], p["volume"],
              info_data.get("market_cap")))
        count += 1
    print(f"  [{ticker}] DB 시세 {count}건 저장")

    # 재무 저장
    count = 0
    for q in fin_data["quarterly"]:
        cur.execute("""
        INSERT OR REPLACE INTO financials
            (ticker, fiscal_period, revenue, operating_income, net_income,
             eps, bps, roe, debt_ratio, ocf, fcf, per, pbr, ev_ebitda,
             source, collected_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker, q["fiscal_period"],
            q.get("revenue"), q.get("operating_income"), q.get("net_income"),
            q.get("eps"), q.get("bps"), q.get("roe"), q.get("debt_ratio"),
            q.get("ocf"), q.get("fcf"),
            info_data.get("trailing_pe"), info_data.get("pb_ratio"), None,
            "yfinance", now
        ))
        count += 1
    print(f"  [{ticker}] DB 재무 {count}건 저장")

    conn.commit()


def save_raw(ticker: str, price_data: dict, fin_data: dict, info_data: dict):
    """원본 데이터를 raw/yahoo/에 JSON으로 저장."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d")

    for name, data in [("price", price_data), ("financials", fin_data), ("info", info_data)]:
        path = RAW_DIR / f"{ticker}_{name}_{now}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    print(f"  [{ticker}] raw 데이터 저장 → {RAW_DIR}/")


def main():
    tickers = sys.argv[1:] if len(sys.argv) > 1 else ["NKE"]

    print(f"=== 미국주식 데이터 수집 (yfinance) ===")
    print(f"대상: {tickers}\n")

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys=ON")

    for ticker in tickers:
        print(f"\n--- {ticker} ---")
        try:
            price_data = collect_price(ticker)
            fin_data = collect_financials(ticker)
            info_data = collect_info(ticker)

            save_raw(ticker, price_data, fin_data, info_data)
            save_to_db(conn, price_data, fin_data, info_data)
            print(f"  [{ticker}] 완료!")
        except Exception as e:
            print(f"  [{ticker}] 오류: {e}")

    conn.close()
    print(f"\n=== 수집 완료 ===")


if __name__ == "__main__":
    main()
