#!/bin/bash

# LinkedIn Profile Crawler using crawl4ai CLI
# This script crawls the specified LinkedIn profiles and saves the results

echo "LinkedIn Profile Crawler (CLI Version)"
echo "======================================"

# Create timestamp for file naming
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# LinkedIn URLs to crawl
URLS=(
    "https://www.linkedin.com/in/sharanjm"
    "https://www.linkedin.com/in/addis-olujohungbe/"
)

# Create output directory
OUTPUT_DIR="linkedin_crawl_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "Created output directory: $OUTPUT_DIR"
echo "Starting to crawl ${#URLS[@]} LinkedIn profiles..."
echo ""

# Counter for successful crawls
SUCCESS_COUNT=0
FAIL_COUNT=0

# Crawl each URL
for i in "${!URLS[@]}"; do
    URL="${URLS[$i]}"
    echo "[$((i+1))/${#URLS[@]}] Crawling: $URL"
    
    # Extract profile name from URL for filename
    PROFILE_NAME=$(echo "$URL" | sed 's|.*/||' | sed 's|/$||')
    
    # Output files
    MARKDOWN_FILE="${OUTPUT_DIR}/linkedin_${PROFILE_NAME}_${TIMESTAMP}.md"
    JSON_FILE="${OUTPUT_DIR}/linkedin_${PROFILE_NAME}_${TIMESTAMP}.json"
    
    # Crawl with markdown output
    echo "  → Extracting markdown content..."
    if crwl "$URL" -o markdown > "$MARKDOWN_FILE" 2>/dev/null; then
        echo "  ✓ Markdown saved to: $MARKDOWN_FILE"
        
        # Also get JSON output with metadata
        echo "  → Extracting JSON metadata..."
        if crwl "$URL" -o json > "$JSON_FILE" 2>/dev/null; then
            echo "  ✓ JSON saved to: $JSON_FILE"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo "  ✗ Failed to extract JSON metadata"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    else
        echo "  ✗ Failed to crawl: $URL"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    
    echo ""
    
    # Add delay between requests to be respectful
    if [ $i -lt $((${#URLS[@]} - 1)) ]; then
        echo "  Waiting 3 seconds before next request..."
        sleep 3
    fi
done

# Summary
echo "Crawling Summary"
echo "==============="
echo "Total URLs: ${#URLS[@]}"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAIL_COUNT"
echo "Output directory: $OUTPUT_DIR"
echo ""

# List generated files
echo "Generated files:"
ls -la "$OUTPUT_DIR"

echo ""
echo "Crawling completed!" 