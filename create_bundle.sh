#!/bin/bash
#
# Create deployment bundle for Deception Engine
#

BUNDLE_NAME="deception-engine-$(date +%Y%m%d).tar.gz"

echo "Creating deployment bundle: $BUNDLE_NAME"

# Core Python files
PYTHON_FILES=(
    "sys_core.py"
    "LLM_Provider.py"
    "ContentManager.py"
    "StrategyManager.py"
    "ActiveDefense.py"
)

# Configuration files
CONFIG_FILES=(
    "worker-spec.json"
    "config.json"
    "templates.json"
    "triggers.json"
    "monthly_plan.json"
)

# Deployment files
DEPLOY_FILES=(
    "setup_linux.sh"
    "requirements.txt"
    "DEPLOYMENT.md"
)

# Check all files exist
echo "Checking files..."
all_files=("${PYTHON_FILES[@]}" "${CONFIG_FILES[@]}" "${DEPLOY_FILES[@]}")
missing=0

for file in "${all_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "  [MISSING] $file"
        missing=1
    else
        echo "  [OK] $file"
    fi
done

if [[ $missing -eq 1 ]]; then
    echo "ERROR: Some files are missing. Aborting."
    exit 1
fi

# Create bundle
echo ""
echo "Creating archive..."
tar -czvf "$BUNDLE_NAME" "${all_files[@]}"

echo ""
echo "Bundle created: $BUNDLE_NAME"
echo "Size: $(du -h "$BUNDLE_NAME" | cut -f1)"
echo ""
echo "Transfer to server with:"
echo "  scp $BUNDLE_NAME user@server:/tmp/"
