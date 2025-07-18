#!/bin/bash

# Simple project cleanup script
# Quick cleanup for __pycache__, temp, empty files, empty folders

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Project Cleanup Script ==="
echo "Cleaning project: $PROJECT_ROOT"
echo ""

# Clean __pycache__
echo "1. Removing __pycache__ directories..."
find "$PROJECT_ROOT" -type d -name "__pycache__" -print -exec rm -rf {} + 2>/dev/null || true

# Clean .pyc and .pyo files
echo "2. Removing Python cache files..."
find "$PROJECT_ROOT" -type f \( -name "*.pyc" -o -name "*.pyo" \) -print -delete 2>/dev/null || true

# Clean temp directory contents
echo "3. Cleaning temp directories..."
find "$PROJECT_ROOT" -type d -name "temp" -exec sh -c 'echo "  Cleaning: $1"; find "$1" -mindepth 1 -delete 2>/dev/null || true' _ {} \; 2>/dev/null || true

# Clean empty files (except __init__.py)
echo "4. Removing empty files..."
find "$PROJECT_ROOT" -type f -empty ! -name "__init__.py" -print -delete 2>/dev/null || true

# Clean empty directories
echo "5. Removing empty directories..."
find "$PROJECT_ROOT" -type d -empty -print -delete 2>/dev/null || true

# Clean common temporary files
echo "6. Removing temporary files..."
find "$PROJECT_ROOT" -type f \( -name "*.tmp" -o -name "*.temp" -o -name "*~" -o -name ".DS_Store" -o -name "Thumbs.db" -o -name "*.log" \) -print -delete 2>/dev/null || true

echo ""
echo "=== Cleanup completed! ==="
