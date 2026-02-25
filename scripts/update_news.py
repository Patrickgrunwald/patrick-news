#!/usr/bin/env python3
import datetime as dt
import html
import json
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

RSS_URL = "https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de"
MAX_ITEMS = 12
ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "news.json"
INDEX_FILE = ROOT / "index.html"


def fetch_rss(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception:
        # Fallback for local environments with broken CA chains.
        insecure_context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=20, context=insecure_context) as r:
            return r.read().decode("utf-8", errors="replace")


def parse_items(xml_text: str):
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        return []

    items = []
    for item in channel.findall("item")[:MAX_ITEMS]:
        title = (item.findtext("title") or "Ohne Titel").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        source = ""
        source_el = item.find("source")
        if source_el is not None and source_el.text:
            source = source_el.text.strip()

        items.append({
            "title": title,
            "link": link,
            "published": pub_date,
            "source": source,
        })

    return items


def save_json(items):
    payload = {
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "count": len(items),
        "items": items,
    }
    DATA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def render_html(items):
    now_local = dt.datetime.now().strftime("%d.%m.%Y %H:%M")

    cards = []
    for it in items:
        title = html.escape(it["title"])
        link = html.escape(it["link"])
        source = html.escape(it["source"] or "Unbekannt")
        published = html.escape(it["published"] or "Zeit unbekannt")
        cards.append(
            f"""
            <article class=\"news-card\">
              <h2><a href=\"{link}\" target=\"_blank\" rel=\"noopener noreferrer\">{title}</a></h2>
              <p class=\"meta\">Quelle: {source}</p>
              <p class=\"meta\">Veröffentlicht: {published}</p>
            </article>
            """.strip()
        )

    html_doc = f"""<!doctype html>
<html lang=\"de\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Daily News</title>
    <link rel=\"stylesheet\" href=\"styles.css\" />
  </head>
  <body>
    <main class=\"container\">
      <header>
        <h1>Daily News</h1>
        <p>Automatisch aktualisierte Top-News</p>
        <p class=\"updated\">Letztes Update: {now_local}</p>
      </header>
      <section class=\"news-grid\">
        {''.join(cards) if cards else '<p>Keine News gefunden.</p>'}
      </section>
    </main>
  </body>
</html>
"""
    INDEX_FILE.write_text(html_doc, encoding="utf-8")


def main():
    xml_text = fetch_rss(RSS_URL)
    items = parse_items(xml_text)
    save_json(items)
    render_html(items)
    print(f"Updated {len(items)} items.")


if __name__ == "__main__":
    main()
