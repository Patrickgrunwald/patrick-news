#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/update_news.py

if [[ -n "$(git status --porcelain index.html data/news.json)" ]]; then
  git add index.html data/news.json
  git commit -m "chore: daily news update $(date '+%Y-%m-%d')"
  git push origin main
else
  echo "No changes in news content."
fi
