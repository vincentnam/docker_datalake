#!/bin/bash

# Script pour concaténer tous les fichiers de code (.js, .css, .html) et package.json
# Sortie: output.txt avec séparateurs par fichier

OUTPUT_FILE="output.txt"
> "$OUTPUT_FILE"  # Vider le fichier

echo "=== package.json ===" >> "$OUTPUT_FILE"
cat package.json >> "$OUTPUT_FILE"
echo -e "\n\n" >> "$OUTPUT_FILE"

# Concaténer public (html, etc.)
echo "=== public/index.html ===" >> "$OUTPUT_FILE"
cat public/index.html >> "$OUTPUT_FILE"
echo -e "\n\n" >> "$OUTPUT_FILE"

# Concaténer src (js, css)
find src -name "*.js" -o -name "*.css" -o -name "*.html" | sort | while read -r file; do
  echo "=== $file ===" >> "$OUTPUT_FILE"
  cat "$file" >> "$OUTPUT_FILE"
  echo -e "\n\n" >> "$OUTPUT_FILE"
done

echo "Concaténation terminée. Fichier: $OUTPUT_FILE"