#!/bin/bash
# Script to package and prepare dataset for download

DATASET_DIR="${1:-sofc_dataset}"
OUTPUT_TAR="${DATASET_DIR}.tar.gz"

echo "Packaging dataset from $DATASET_DIR..."
tar -czf "$OUTPUT_TAR" "$DATASET_DIR" 2>/dev/null || {
    echo "Error: Dataset directory '$DATASET_DIR' not found."
    echo "Usage: $0 [dataset_directory]"
    exit 1
}

echo "Dataset packaged successfully!"
echo "File: $OUTPUT_TAR"
echo "Size: $(du -h "$OUTPUT_TAR" | cut -f1)"

# Create checksum
if command -v md5sum &> /dev/null; then
    md5sum "$OUTPUT_TAR" > "${OUTPUT_TAR}.md5"
    echo "MD5 checksum saved to: ${OUTPUT_TAR}.md5"
fi