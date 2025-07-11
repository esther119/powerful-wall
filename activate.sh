#!/bin/bash

# Photo Transcription Environment Activation Script

echo "🚀 Activating Photo Transcription Environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📁 Current directory: $(pwd)"
echo "🐍 Python version: $(python --version)"
echo "📦 pip version: $(pip --version)"

echo ""
echo "🎯 Available commands:"
echo "  python test_setup.py        - Test the setup"
echo "  python transcribe_photos.py - Run transcription"
echo "  deactivate                   - Exit virtual environment"
echo ""

# Run test if requested
if [ "$1" == "test" ]; then
    echo "🧪 Running setup test..."
    python test_setup.py
fi

# Start bash in the virtual environment
exec bash 