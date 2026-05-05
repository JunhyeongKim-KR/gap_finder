#!/usr/bin/env python3
"""
collect_stocks.py — 종목 데이터 크롤러
저장 테이블: companies, financials, price_daily
소스: yfinance (미국/한국), OpenDART (한국 재무), KRX (한국 시세)
"""
import sys
import argparse
import sqlite3
import json
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from load_env import get_key

DB_PATH = Path(__file__).resolve().parent.parent.parent / "db" / 'raw.db'


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _safe(val):
    """NaN/None 안전 변환."""
    if val is None:
        return None
    s = str(val)
    if s in ('nan', 'NaN', 'None', ''):
        return None
    return float(val)


def _get(df, key, col):
    """DataFrame에서 안전하게 값 추출."""
    try:
        if key in df.index:
            val = df.loc[key, col]
            if val is not None and str(val) != 'nan':
                return float(val)
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# 1. yfinance
# ---------------------------------------------------------------------------

def fetch_yfinance(tickers, days=365):
    """yfinance로 기업정보/시세/재무 수집 → companies, price_daily, financials."""
    try:
        import yfinance as yf
    except ImportError:
        print("[오류] yfinance가 설치되지 않았습니다: pip install yfinance")
        return

    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    summary = {"companies": 0, "price_daily": 0, "financials": 0}

    for ticker in tickers:
        print(f"\n--- [yfinance] {ticker} ---")
        try:
            stock = yf.Ticker(ticker)

            # ── 기업 정보 → companies ──
            print(f"  [{ticker}] 기업 정보 수집 중...")
            info = stock.info
            market = None
            exchange = (info.get("exchange") or "").upper()
            if "KS" in ticker.upper() or "KOSPI" in exchange:
                market = "KR_KOSPI"
            elif "KQ" in ticker.upper() or "KOSDAQ" in exchange:
                market = "KR_KOSDAQ"
            elif exchange in ("NYQ", "NYSE"):
                market = "US_NYSE"
            elif exchange in ("NMS", "NASDAQ", "NGM", "NCM"):
                market = "US_NASDAQ"

            conn.execute("""
                INSERT OR REPLACE INTO companies
                    (ticker, name_en, market, country, sector, industry,
                     description, market_cap, market_cap_date, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticker,
                info.get("shortName") or info.get("longName"),
                market,
                info.get("country"),
                info.get("sector"),
                info.get("industry"),
                info.get("longBusinessSummary"),
                info.get("marketCap"),
                now,
                now,
            ))
            summary["companies"] += 1
            print(f"  [{ticker}] 기업 정보 저장 완료 — {info.get('shortName')}")

            # ── 시세 → price_daily ──
            print(f"  [{ticker}] 시세 수집 중 ({days}일)...")
            hist = stock.history(start=start_date)
            price_count = 0
            if hist is not None and not hist.empty:
                for date, row in hist.iterrows():
                    conn.execute("""
                        INSERT OR REPLACE INTO price_daily
                            (ticker, date, open, high, low, close, volume,
                             market_cap, source, collected_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ticker,
                        date.strftime("%Y-%m-%d"),
                        round(row["Open"], 4),
                        round(row["High"], 4),
                        round(row["Low"], 4),
                        round(row["Close"], 4),
                        int(row["Volume"]),
                        info.get("marketCap"),
                        "yfinance",
                        now,
                    ))
                    price_count += 1
            summary["price_daily"] += price_count
            print(f"  [{ticker}] 시세 {price_count}일 저장 완료")

            # ── 분기 재무 → financials ──
            print(f"  [{ticker}] 재무제표 수집 중...")
            fin_count = 0
            try:
                qi = stock.quarterly_income_stmt
                qb = stock.quarterly_balance_sheet
                qc = stock.quarterly_cashflow

                if qi is not None and not qi.empty:
                    for col in qi.columns:
                        period = col.strftime("%Y-%m-%d")

                        revenue = _get(qi, "Total Revenue", col)
                        op_income = _get(qi, "Operating Income", col)
                        net_income = _get(qi, "Net Income", col)
                        ebitda = _get(qi, "EBITDA", col) or _get(qi, "Normalized EBITDA", col)
                        eps = _get(qi, "Basic EPS", col) or _get(qi, "Diluted EPS", col)

                        # 재무상태표
                        bps = roe = debt_ratio = debt = cash = shares = None
                        if qb is not None and col in qb.columns:
                            total_equity = (_get(qb, "Stockholders Equity", col)
                                            or _get(qb, "Total Equity Gross Minority Interest", col))
                            total_assets = _get(qb, "Total Assets", col)
                            debt = _get(qb, "Total Debt", col)
                            cash = (_get(qb, "Cash And Cash Equivalents", col)
                                    or _get(qb, "Cash Cash Equivalents And Short Term Investments", col))
                            shares = (_get(qb, "Share Issued", col)
                                      or _get(qb, "Ordinary Shares Number", col))

                            if total_equity and shares:
                                bps = round(total_equity / shares, 2)
                            if total_equity and net_income:
                                roe = round((net_income / total_equity) * 100, 2)
                            if debt and total_equity:
                                debt_ratio = round((debt / total_equity) * 100, 2)

                        # 현금흐름
                        ocf = fcf = capex = None
                        if qc is not None and col in qc.columns:
                            ocf = _get(qc, "Operating Cash Flow", col)
                            fcf = _get(qc, "Free Cash Flow", col)
                            capex = _get(qc, "Capital Expenditure", col)

                        conn.execute("""
                            INSERT OR REPLACE INTO financials
                                (ticker, fiscal_period, revenue, operating_income,
                                 net_income, ebitda, fcf, capex, cash, debt,
                                 shares_outstanding, eps, bps, roe, debt_ratio,
                                 ocf, per, pbr, ev_ebitda,
                                 source, collected_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ticker, period,
                            revenue, op_income, net_income, ebitda,
                            fcf, capex, cash, debt,
                            shares,
                            eps, bps, roe, debt_ratio,
                            ocf,
                            _safe(info.get("trailingPE")),
                            _safe(info.get("priceToBook")),
                            _safe(info.get("enterpriseToEbitda")),
                            "yfinance", now,
                        ))
                        fin_count += 1
                else:
                    print(f"  [{ticker}] 재무제표 데이터 없음")
            except Exception as e:
                print(f"  [{ticker}] 재무 수집 오류: {e}")

            summary["financials"] += fin_count
            print(f"  [{ticker}] 재무 {fin_count}분기 저장 완료")

            conn.commit()
            print(f"  [{ticker}] 완료!")

        except Exception as e:
            print(f"  [{ticker}] 오류 발생 — 건너뜀: {e}")
            continue

    conn.close()
    return summary


# ---------------------------------------------------------------------------
# 2. OpenDART (한국 재무제표)
# ---------------------------------------------------------------------------

def fetch_dart_financials(tickers, days=365):
    """OpenDART API로 한국 기업 재무제표 수집 → financials 테이블.

    참고: ticker가 아닌 corp_code가 필요. ticker에 corp_code를 직접 전달하거나,
    ticker→corp_code 매핑이 구현될 때까지 건너뜀.
    """
    api_key = get_key("DART_API_KEY")
    if not api_key:
        print("[DART] API 키 미설정 — 건너뜀")
        return {"financials": 0}

    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d")
    summary = {"financials": 0}

    # 최근 연도 계산
    current_year = datetime.now().year
    years_back = max(1, days // 365)
    years = list(range(current_year - years_back, current_year + 1))

    # 보고서 코드: 1분기=11013, 반기=11012, 3분기=11014, 사업보고서=11011
    reprt_codes = [
        ("11013", "Q1"),
        ("11012", "Q2"),
        ("11014", "Q3"),
        ("11011", "Q4"),
    ]

    for corp_code in tickers:
        print(f"\n--- [DART] {corp_code} ---")
        for year in years:
            for reprt_code, label in reprt_codes:
                try:
                    params = urllib.parse.urlencode({
                        "crtfc_key": api_key,
                        "corp_code": corp_code,
                        "bsns_year": str(year),
                        "reprt_code": reprt_code,
                        "fs_div": "CFS",  # 연결재무제표
                    })
                    url = f"https://opendart.fss.or.kr/api/fnlttSinglAcnt.json?{params}"

                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        data = json.loads(resp.read().decode("utf-8"))

                    if data.get("status") != "000":
                        # 데이터 없음 등 — 조용히 넘어감
                        continue

                    items = data.get("list", [])
                    if not items:
                        continue

                    # DART 계정과목명 → 값 매핑
                    acct = {}
                    for item in items:
                        name = item.get("account_nm", "")
                        amt_str = (item.get("thstrm_amount") or "").replace(",", "")
                        try:
                            amt = float(amt_str) if amt_str else None
                        except ValueError:
                            amt = None
                        acct[name] = amt

                    fiscal_period = f"{year}-{label}"

                    conn.execute("""
                        INSERT OR REPLACE INTO financials
                            (ticker, fiscal_period, revenue, operating_income,
                             net_income, source, collected_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        corp_code, fiscal_period,
                        acct.get("매출액") or acct.get("수익(매출액)"),
                        acct.get("영업이익"),
                        acct.get("당기순이익") or acct.get("당기순이익(손실)"),
                        "DART", now,
                    ))
                    summary["financials"] += 1
                    print(f"  [{corp_code}] {year}-{label} 저장 완료")

                except Exception as e:
                    print(f"  [{corp_code}] {year}-{label} 오류: {e}")
                    continue

    conn.commit()
    conn.close()
    return summary


# ---------------------------------------------------------------------------
# 3. KRX (한국 시세) — 미구현
# ---------------------------------------------------------------------------

def fetch_krx(tickers, days=365):
    """KRX API로 한국 시세 수집 — 승인 대기 중."""
    print("KRX API 승인 대기 중 — 건너뜀")
    return {"price_daily": 0}


# ---------------------------------------------------------------------------
# 4. main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="종목 데이터 크롤러 (companies, financials, price_daily)")
    parser.add_argument(
        "--source", default="all",
        choices=["all", "yfinance", "dart", "krx"],
        help="데이터 소스 (default: all)")
    parser.add_argument(
        "--tickers", default="005930.KS,NKE",
        help="쉼표 구분 티커 목록 (default: 005930.KS,NKE)")
    parser.add_argument(
        "--days", type=int, default=365,
        help="과거 조회 기간-일 (default: 365)")
    args = parser.parse_args()

    tickers = [t.strip() for t in args.tickers.split(",") if t.strip()]
    source = args.source

    print(f"=== 종목 데이터 수집 ===")
    print(f"소스: {source} | 티커: {tickers} | 기간: {args.days}일\n")

    # DB 디렉토리 확인
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    total_summary = {}

    if source in ("all", "yfinance"):
        result = fetch_yfinance(tickers, args.days)
        if result:
            for k, v in result.items():
                total_summary[k] = total_summary.get(k, 0) + v

    if source in ("all", "dart"):
        result = fetch_dart_financials(tickers, args.days)
        if result:
            for k, v in result.items():
                total_summary[k] = total_summary.get(k, 0) + v

    if source in ("all", "krx"):
        result = fetch_krx(tickers, args.days)
        if result:
            for k, v in result.items():
                total_summary[k] = total_summary.get(k, 0) + v

    # 최종 요약
    print(f"\n{'='*40}")
    print("=== 수집 완료 요약 ===")
    print(f"{'='*40}")
    if total_summary:
        for table, count in sorted(total_summary.items()):
            print(f"  {table:<20} {count:>6}건")
    else:
        print("  저장된 데이터 없음")
    print()


if __name__ == "__main__":
    main()
