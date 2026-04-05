#!/usr/bin/env python3
"""
이벤트 + 문서 크롤러 — Google News RSS, DART, SEC EDGAR

raw.db의 documents / events 테이블에 저장한다.
외부 패키지 없이 stdlib만 사용.
"""

import argparse
import hashlib
import json
import sqlite3
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load_env import get_key

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "raw.db"

DEFAULT_NEWS_QUERIES = ["삼성전자", "나이키 Nike", "반도체", "금리 인하"]
DEFAULT_SEC_TICKERS = ["NKE"]

# query -> tickers mapping (best-effort)
QUERY_TICKER_MAP = {
    "삼성전자": ["005930.KS"],
    "나이키 Nike": ["NKE"],
    "반도체": [],
    "금리 인하": [],
}

# DART report_nm -> event_type mapping
DART_EVENT_TYPE_MAP = {
    "사업보고서": "earnings",
    "반기보고서": "earnings",
    "분기보고서": "earnings",
    "실적": "earnings",
    "유상증자": "capital_raise",
    "무상증자": "capital_raise",
    "자기주식": "buyback",
    "배당": "dividend",
    "합병": "ma",
    "분할": "ma",
    "임원": "management_change",
}

# SEC form_type -> event_type mapping
SEC_EVENT_TYPE_MAP = {
    "10-K": "earnings",
    "10-Q": "earnings",
    "20-F": "earnings",
    "8-K": "other",
    "S-1": "ipo",
    "SC 13D": "other",
    "DEF 14A": "other",
    "4": "other",
}


def _short_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]


def _has_korean(text: str) -> bool:
    return any('\uac00' <= c <= '\ud7a3' for c in text)


def _get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _insert_document(conn, doc):
    conn.execute(
        """INSERT OR REPLACE INTO documents
           (doc_id, title, source, source_type, published_at, url,
            raw_text, cleaned_text, language, tags, related_tickers, collected_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        (
            doc["doc_id"], doc.get("title"), doc.get("source"),
            doc.get("source_type"), doc.get("published_at"), doc.get("url"),
            doc.get("raw_text"), doc.get("cleaned_text"),
            doc.get("language", "ko"),
            json.dumps(doc.get("tags", []), ensure_ascii=False),
            json.dumps(doc.get("related_tickers", []), ensure_ascii=False),
        ),
    )


def _insert_event(conn, evt):
    conn.execute(
        """INSERT OR REPLACE INTO events
           (event_id, event_type, date, title, summary, url, source,
            source_doc_id, related_tickers, related_countries,
            related_industries, importance, tags, collected_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        (
            evt["event_id"], evt.get("event_type", "other"),
            evt.get("date"), evt.get("title"), evt.get("summary"),
            evt.get("url"), evt.get("source"), evt.get("source_doc_id"),
            json.dumps(evt.get("related_tickers", []), ensure_ascii=False),
            json.dumps(evt.get("related_countries", []), ensure_ascii=False),
            json.dumps(evt.get("related_industries", []), ensure_ascii=False),
            evt.get("importance", "MEDIUM"),
            json.dumps(evt.get("tags", []), ensure_ascii=False),
        ),
    )


# ---------------------------------------------------------------------------
# 1. Google News RSS
# ---------------------------------------------------------------------------

def fetch_news(queries=None, max_items=20) -> dict:
    """Google News RSS로 뉴스 수집 -> documents + events 저장."""
    queries = queries or DEFAULT_NEWS_QUERIES
    conn = _get_db()
    stats = {"docs": 0, "events": 0, "errors": 0}

    for query in queries:
        lang = "ko" if _has_korean(query) else "en"
        encoded = quote(query)
        if lang == "ko":
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
        else:
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=US&ceid=US:en"

        print(f"  [News] '{query}' 수집 중 ({lang})...")

        try:
            req = Request(rss_url, headers={"User-Agent": "GapFinder/1.0"})
            with urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
        except Exception as e:
            print(f"  [News] '{query}' RSS 가져오기 실패: {e}")
            stats["errors"] += 1
            continue

        items = root.findall(".//item")
        tickers = QUERY_TICKER_MAP.get(query, [])

        for item in items[:max_items]:
            try:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                description = item.findtext("description", "")
                # source tag in Google News RSS
                source_el = item.find("source")
                source_name = source_el.text if source_el is not None else ""

                # Parse date
                date_str = ""
                if pub_date:
                    try:
                        # RFC 2822: "Sat, 05 Apr 2026 07:00:00 GMT"
                        dt = datetime.strptime(
                            pub_date.replace(" GMT", " +0000").strip(),
                            "%a, %d %b %Y %H:%M:%S %z",
                        )
                        date_str = dt.strftime("%Y-%m-%d")
                    except ValueError:
                        date_str = pub_date[:10]

                doc_id = f"news_{date_str}_{_short_hash(link)}"
                event_id = f"evt_{doc_id}"

                _insert_document(conn, {
                    "doc_id": doc_id,
                    "title": title,
                    "source": source_name,
                    "source_type": "news",
                    "published_at": pub_date,
                    "url": link,
                    "raw_text": description[:500] if description else None,
                    "cleaned_text": None,
                    "language": lang,
                    "tags": [query],
                    "related_tickers": tickers,
                })
                stats["docs"] += 1

                _insert_event(conn, {
                    "event_id": event_id,
                    "event_type": "other",
                    "date": date_str,
                    "title": title,
                    "summary": description[:300] if description else None,
                    "url": link,
                    "source": "google_news",
                    "source_doc_id": doc_id,
                    "related_tickers": tickers,
                    "related_countries": ["KR"] if lang == "ko" else ["US"],
                    "related_industries": [],
                    "importance": "MEDIUM",
                    "tags": [query],
                })
                stats["events"] += 1

            except Exception as e:
                print(f"  [News] 항목 처리 오류: {e}")
                stats["errors"] += 1

        print(f"  [News] '{query}' 완료 — {len(items[:max_items])}건")

    conn.commit()
    conn.close()
    return stats


# ---------------------------------------------------------------------------
# 2. DART (OpenDART) 공시
# ---------------------------------------------------------------------------

def _classify_dart_event(report_nm: str) -> str:
    for keyword, etype in DART_EVENT_TYPE_MAP.items():
        if keyword in report_nm:
            return etype
    return "filing"


def fetch_dart_filings(corp_codes=None, days=30) -> dict:
    """DART 공시 수집 -> documents + events."""
    api_key = get_key("DART_API_KEY")
    if not api_key:
        print("  [DART] API 키 없음 — 건너뜁니다.")
        return {"docs": 0, "events": 0, "errors": 0, "skipped": True}

    conn = _get_db()
    stats = {"docs": 0, "events": 0, "errors": 0}

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    bgn_de = start_date.strftime("%Y%m%d")
    end_de = end_date.strftime("%Y%m%d")

    params = (
        f"crtfc_key={api_key}&bgn_de={bgn_de}&end_de={end_de}"
        f"&corp_cls=Y&page_count=100"
    )
    url = f"https://opendart.fss.or.kr/api/list.json?{params}"

    print(f"  [DART] 공시 수집 중 ({bgn_de} ~ {end_de})...")

    try:
        req = Request(url)
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  [DART] API 호출 실패: {e}")
        conn.close()
        return {"docs": 0, "events": 0, "errors": 1}

    if data.get("status") != "000":
        msg = data.get("message", "알 수 없는 오류")
        print(f"  [DART] API 오류: {msg}")
        conn.close()
        return {"docs": 0, "events": 0, "errors": 1}

    filings = data.get("list", [])
    print(f"  [DART] {len(filings)}건 공시 발견")

    for f in filings:
        try:
            rcept_no = f.get("rcept_no", "")
            report_nm = f.get("report_nm", "")
            corp_name = f.get("corp_name", "")
            rcept_dt = f.get("rcept_dt", "")
            corp_code = f.get("corp_code", "")

            doc_id = f"dart_{rcept_no}"
            event_id = f"evt_{doc_id}"
            filing_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"

            date_str = ""
            if rcept_dt and len(rcept_dt) == 8:
                date_str = f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}"

            event_type = _classify_dart_event(report_nm)

            _insert_document(conn, {
                "doc_id": doc_id,
                "title": f"[{corp_name}] {report_nm}",
                "source": "DART",
                "source_type": "filing",
                "published_at": date_str,
                "url": filing_url,
                "raw_text": None,
                "cleaned_text": None,
                "language": "ko",
                "tags": ["DART", report_nm],
                "related_tickers": [corp_code],
            })
            stats["docs"] += 1

            _insert_event(conn, {
                "event_id": event_id,
                "event_type": event_type,
                "date": date_str,
                "title": f"[{corp_name}] {report_nm}",
                "summary": report_nm,
                "url": filing_url,
                "source": "DART",
                "source_doc_id": doc_id,
                "related_tickers": [corp_code],
                "related_countries": ["KR"],
                "related_industries": [],
                "importance": "MEDIUM",
                "tags": ["DART"],
            })
            stats["events"] += 1

        except Exception as e:
            print(f"  [DART] 항목 처리 오류: {e}")
            stats["errors"] += 1

    # Also fetch KOSDAQ if desired
    params_k = (
        f"crtfc_key={api_key}&bgn_de={bgn_de}&end_de={end_de}"
        f"&corp_cls=K&page_count=100"
    )
    url_k = f"https://opendart.fss.or.kr/api/list.json?{params_k}"

    try:
        req = Request(url_k)
        with urlopen(req, timeout=20) as resp:
            data_k = json.loads(resp.read())
        if data_k.get("status") == "000":
            filings_k = data_k.get("list", [])
            print(f"  [DART] 코스닥 {len(filings_k)}건 추가 발견")
            for f in filings_k:
                try:
                    rcept_no = f.get("rcept_no", "")
                    report_nm = f.get("report_nm", "")
                    corp_name = f.get("corp_name", "")
                    rcept_dt = f.get("rcept_dt", "")
                    corp_code = f.get("corp_code", "")

                    doc_id = f"dart_{rcept_no}"
                    event_id = f"evt_{doc_id}"
                    filing_url = f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}"

                    date_str = ""
                    if rcept_dt and len(rcept_dt) == 8:
                        date_str = f"{rcept_dt[:4]}-{rcept_dt[4:6]}-{rcept_dt[6:8]}"

                    event_type = _classify_dart_event(report_nm)

                    _insert_document(conn, {
                        "doc_id": doc_id,
                        "title": f"[{corp_name}] {report_nm}",
                        "source": "DART",
                        "source_type": "filing",
                        "published_at": date_str,
                        "url": filing_url,
                        "raw_text": None,
                        "cleaned_text": None,
                        "language": "ko",
                        "tags": ["DART", report_nm],
                        "related_tickers": [corp_code],
                    })
                    stats["docs"] += 1

                    _insert_event(conn, {
                        "event_id": event_id,
                        "event_type": event_type,
                        "date": date_str,
                        "title": f"[{corp_name}] {report_nm}",
                        "summary": report_nm,
                        "url": filing_url,
                        "source": "DART",
                        "source_doc_id": doc_id,
                        "related_tickers": [corp_code],
                        "related_countries": ["KR"],
                        "related_industries": [],
                        "importance": "MEDIUM",
                        "tags": ["DART"],
                    })
                    stats["events"] += 1
                except Exception as e:
                    print(f"  [DART] 코스닥 항목 처리 오류: {e}")
                    stats["errors"] += 1
    except Exception as e:
        print(f"  [DART] 코스닥 API 호출 실패: {e}")
        stats["errors"] += 1

    conn.commit()
    conn.close()
    print(f"  [DART] 완료 — 문서 {stats['docs']}건, 이벤트 {stats['events']}건")
    return stats


# ---------------------------------------------------------------------------
# 3. SEC EDGAR
# ---------------------------------------------------------------------------

def _classify_sec_event(form_type: str) -> str:
    for ft, etype in SEC_EVENT_TYPE_MAP.items():
        if form_type.strip().upper().startswith(ft):
            return etype
    return "filing"


def fetch_sec_filings(tickers=None, days=30) -> dict:
    """SEC EDGAR 공시 수집 -> documents + events."""
    tickers = tickers or DEFAULT_SEC_TICKERS
    conn = _get_db()
    stats = {"docs": 0, "events": 0, "errors": 0}

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    headers = {
        "User-Agent": "GapFinder/1.0 (contact@example.com)",
        "Accept": "application/json",
    }

    for ticker in tickers:
        print(f"  [SEC] '{ticker}' 수집 중 ({start_str} ~ {end_str})...")

        search_url = (
            f"https://efts.sec.gov/LATEST/search-index?"
            f"q={quote(ticker)}&dateRange=custom"
            f"&startdt={start_str}&enddt={end_str}"
        )

        try:
            req = Request(search_url, headers=headers)
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            print(f"  [SEC] '{ticker}' API 호출 실패: {e}")
            stats["errors"] += 1
            continue

        # EDGAR full-text search API returns hits
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            # Try alternative EDGAR search endpoint
            alt_url = (
                f"https://efts.sec.gov/LATEST/search-index?"
                f"q=%22{quote(ticker)}%22&dateRange=custom"
                f"&startdt={start_str}&enddt={end_str}"
            )
            try:
                req = Request(alt_url, headers=headers)
                with urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read())
                hits = data.get("hits", {}).get("hits", [])
            except Exception:
                pass

        print(f"  [SEC] '{ticker}' {len(hits)}건 발견")

        for hit in hits:
            try:
                src = hit.get("_source", hit)
                accession = src.get("file_num", src.get("accession_no", ""))
                # Clean accession number for ID
                acc_clean = accession.replace("-", "").replace(" ", "")
                if not acc_clean:
                    acc_clean = _short_hash(json.dumps(src))

                form_type = src.get("form_type", src.get("file_type", ""))
                filing_date = src.get("file_date", src.get("period_of_report", ""))
                company = src.get("display_names", [ticker])[0] if src.get("display_names") else ticker
                title = f"[{company}] {form_type}"

                filing_url = ""
                if src.get("file_num"):
                    filing_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&filenum={src['file_num']}"

                doc_id = f"sec_{acc_clean}"
                event_id = f"evt_{doc_id}"
                event_type = _classify_sec_event(form_type)

                _insert_document(conn, {
                    "doc_id": doc_id,
                    "title": title,
                    "source": "SEC_EDGAR",
                    "source_type": "filing",
                    "published_at": filing_date,
                    "url": filing_url,
                    "raw_text": None,
                    "cleaned_text": None,
                    "language": "en",
                    "tags": ["SEC", form_type],
                    "related_tickers": [ticker],
                })
                stats["docs"] += 1

                _insert_event(conn, {
                    "event_id": event_id,
                    "event_type": event_type,
                    "date": filing_date,
                    "title": title,
                    "summary": f"{form_type} filing by {company}",
                    "url": filing_url,
                    "source": "SEC_EDGAR",
                    "source_doc_id": doc_id,
                    "related_tickers": [ticker],
                    "related_countries": ["US"],
                    "related_industries": [],
                    "importance": "MEDIUM",
                    "tags": ["SEC", form_type],
                })
                stats["events"] += 1

                # SEC rate limit: 10 req/sec
                time.sleep(0.1)

            except Exception as e:
                print(f"  [SEC] 항목 처리 오류: {e}")
                stats["errors"] += 1

    conn.commit()
    conn.close()
    print(f"  [SEC] 완료 — 문서 {stats['docs']}건, 이벤트 {stats['events']}건")
    return stats


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="이벤트 + 문서 크롤러 (News / DART / SEC EDGAR)"
    )
    parser.add_argument(
        "--source", choices=["all", "news", "dart", "sec"], default="all",
        help="수집 소스 (default: all)",
    )
    parser.add_argument(
        "--days", type=int, default=30,
        help="수집 기간 일수 (default: 30)",
    )
    parser.add_argument(
        "--queries", type=str, default=None,
        help="뉴스 검색어 (콤마 구분, e.g. '삼성전자,반도체')",
    )
    parser.add_argument(
        "--max-items", type=int, default=20,
        help="뉴스 최대 수집 건수 per query (default: 20)",
    )
    args = parser.parse_args()

    queries = args.queries.split(",") if args.queries else None

    print("=" * 50)
    print(f"  이벤트/문서 수집 시작 — source={args.source}, days={args.days}")
    print("=" * 50)

    total = {"docs": 0, "events": 0, "errors": 0}

    if args.source in ("all", "news"):
        print("\n--- Google News RSS ---")
        s = fetch_news(queries=queries, max_items=args.max_items)
        total["docs"] += s["docs"]
        total["events"] += s["events"]
        total["errors"] += s["errors"]

    if args.source in ("all", "dart"):
        print("\n--- DART 공시 ---")
        s = fetch_dart_filings(days=args.days)
        total["docs"] += s["docs"]
        total["events"] += s["events"]
        total["errors"] += s["errors"]

    if args.source in ("all", "sec"):
        print("\n--- SEC EDGAR ---")
        s = fetch_sec_filings(days=args.days)
        total["docs"] += s["docs"]
        total["events"] += s["events"]
        total["errors"] += s["errors"]

    print("\n" + "=" * 50)
    print(f"  수집 완료 — 문서 {total['docs']}건, 이벤트 {total['events']}건, 오류 {total['errors']}건")
    print(f"  DB: {DB_PATH}")
    print("=" * 50)


if __name__ == "__main__":
    main()
