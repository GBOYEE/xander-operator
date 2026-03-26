#!/bin/bash
set -e
echo "Installing Playwright OS dependencies..."
playwright install-deps
echo "Installing Chromium browser..."
playwright install chromium
echo "Done. You can now run: python3 operator.py"
