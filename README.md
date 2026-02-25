# Patrick NEWS

Einfache HTML/CSS-News-Seite, die automatisch aus einem RSS-Feed aktualisiert wird.

## Lokal testen

```bash
python3 scripts/update_news.py
```

Danach `index.html` im Browser öffnen.

## Was wird aktualisiert?

- `index.html` (sichtbare News-Seite)
- `data/news.json` (Rohdaten für die letzten Einträge)

## Für tägliche Automation

Die Codex-Automation sollte täglich folgendes ausführen:

```bash
bash scripts/daily_update.sh
```

Das Skript macht:

- News aktualisieren
- Änderungen committen (nur wenn sich Inhalte ändern)
- auf `origin/main` pushen
