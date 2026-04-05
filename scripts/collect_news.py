# DEPRECATED: 이 스크립트는 통합 스크립트로 대체되었습니다.
#!/usr/bin/env python3
"""종목별 뉴스 수집 — Google News RSS (API 키 불필요).

종목명으로 검색해 최근 뉴스를 수집하고 raw/news/에 저장한다.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

import feedparser

RAW_DIR = Path(__file__).resolve().parent.parent / "raw" / "news"


def collect_news(query: str, lang: str = "ko", max_items: int = 20) -> list:
    """Google News RSS로 뉴스 수집."""
    # Google News RSS URL
    encoded = quote(query)
    if lang == "ko":
        url = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
    else:
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=US&ceid=US:en"

    print(f"  [{query}] 뉴스 수집 중 ({lang})...")
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries[:max_items]:
        articles.append({
            "title": entry.get("title", ""),
            "source": entry.get("source", {}).get("title", "") if hasattr(entry, "source") else "",
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", "")[:200],
        })

    print(f"  [{query}] {len(articles)}건 수집 완료")
    return articles


def save_raw(query: str, articles: list):
    """원본 뉴스를 raw/news/에 저장."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M")
    safe_query = query.replace(" ", "_").replace("/", "_")
    path = RAW_DIR / f"{safe_query}_{now}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump({"query": query, "count": len(articles), "articles": articles},
                  f, ensure_ascii=False, indent=2)

    print(f"  저장 → {path}")


def print_summary(query: str, articles: list):
    """뉴스 요약 출력."""
    print(f"\n  === {query} 최근 뉴스 ({len(articles)}건) ===")
    for i, a in enumerate(articles[:10], 1):
        src = f" [{a['source']}]" if a.get("source") else ""
        print(f"  {i:2d}. {a['title']}{src}")
    if len(articles) > 10:
        print(f"  ... 외 {len(articles)-10}건")


def main():
    # 기본: 삼성전자(한국어) + Nike(영어)
    queries = sys.argv[1:] if len(sys.argv) > 1 else ["삼성전자 주가", "Nike NKE stock"]

    print(f"=== 뉴스 수집 (Google News RSS) ===\n")

    for query in queries:
        lang = "ko" if any('\uac00' <= c <= '\ud7a3' for c in query) else "en"
        try:
            articles = collect_news(query, lang=lang)
            save_raw(query, articles)
            print_summary(query, articles)
        except Exception as e:
            print(f"  [{query}] 오류: {e}")

    print(f"\n=== 수집 완료 ===")


if __name__ == "__main__":
    main()
