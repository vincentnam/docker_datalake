#!/bin/bash
FILES=("$@")
for file in "${FILES[@]}"; do
  while [ ! -f "$file" ]; do echo "Waiting $file..."; sleep 5; done
done
echo "All files ready"