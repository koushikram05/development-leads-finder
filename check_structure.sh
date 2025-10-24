set -euo pipefail
root="$(pwd)"
echo "Project root: $root"
echo
expected=(
  "app"
  "app/__init__.py"
  "app/scraper"
  "app/scraper/__init__.py"
  "app/scraper/zillow_scraper.py"
  "app/scraper/redfin_scraper.py"
  "app/scraper/realtor_scraper.py"
  "app/scraper/llm_search.py"
  "app/enrichment"
  "app/enrichment/__init__.py"
  "app/enrichment/gis_enrichment.py"
  "app/classifier"
  "app/classifier/__init__.py"
  "app/classifier/llm_classifier.py"
  "app/dev_pipeline.py"
  "app/utils.py"
  "data"
  "data/raw_listings.csv"
  "data/classified_listings.csv"
  ".env"
  "requirements.txt"
  "README.md"
)missing_count=0
echo "Checking expected files & folders..."
for p in "${expected[@]}"; do
  if [ -e "$p" ]; then
    printf "  \033[32m✅\033[0m %s\n" "$p"
  else
    printf "  \033[31m❌ MISSING\033[0m %s\n" "$p"
    missing_count=$((missing_count+1))
  fi
done

echo
echo "Top-level contents (for quick inspection):"
ls -1A

echo
echo "Top-level items not in the expected whitelist:"
# whitelist of top-level items we expect (add more if needed)
whitelist_regex='^(app|data|\.env|requirements.txt|README.md|folder_structure.txt)$'
ls -1A | grep -v -E "$whitelist_regex" || true

echo
printf "Summary: %d missing item(s)\n" "$missing_count"

if [ "$missing_count" -eq 0 ]; then
  echo "All required files/folders present. ✅"
  exit 0
else
  echo "One or more expected items are missing. Fix by creating/moving the files. See the checklist above. ❌"
  exit 1
fi
