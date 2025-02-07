#!/bin/bash

# Define the output file
OUTPUT_FILE="instructions/file_structure.md"

# Create instructions directory if it doesn't exist
mkdir -p instructions

# Create or clear the file
echo "# Project File Structure" > "$OUTPUT_FILE"
echo "\`\`\`" >> "$OUTPUT_FILE"

# Use tree command if available, otherwise fall back to find
if command -v tree &> /dev/null; then
    # Using tree command with specific exclusions and ignoring venv directory completely
    tree -I 'node_modules|.git|.next|.vercel|dist|build|venv|__pycache__|*.pyc' --dirsfirst -a >> "$OUTPUT_FILE"
else
    # Fallback to using find command
    find . -type d \( -name node_modules -o -name .git -o -name .next -o -name .vercel -o -name dist -o -name build -o -name venv -o -name __pycache__ \) -prune -o -print | \
    sort | sed -e "s/[^-][^\/]*\// │   /g" -e "s/│    \([^│]\)/├── \1/" >> "$OUTPUT_FILE"
fi

echo "\`\`\`" >> "$OUTPUT_FILE"

echo "File structure updated in $OUTPUT_FILE"