#!/usr/bin/env python3
"""
Test script to verify the photo transcription setup is working correctly.
This script checks all dependencies, configuration, and API connectivity.
"""

import os
import sys
from pathlib import Path


def test_imports():
    """Test that all required packages can be imported."""
    print("🔍 Testing imports...")

    try:
        import google.generativeai as genai

        print("✅ google-generativeai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google-generativeai: {e}")
        return False

    try:
        from PIL import Image

        print("✅ Pillow imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Pillow: {e}")
        return False

    try:
        import pandas as pd

        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pandas: {e}")
        return False

    try:
        from dotenv import load_dotenv

        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import python-dotenv: {e}")
        return False

    try:
        from tqdm import tqdm

        print("✅ tqdm imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import tqdm: {e}")
        return False

    return True


def test_config():
    """Test that the configuration can be loaded."""
    print("\n🔧 Testing configuration...")

    try:
        from config import Config

        print("✅ Config module imported successfully")

        # Check if .env file exists
        if Path(".env").exists():
            print("✅ .env file found")
        else:
            print("⚠️  .env file not found - you'll need to create it with your API key")

        # Check API key (without revealing it)
        if (
            Config.GEMINI_API_KEY
            and Config.GEMINI_API_KEY != "your_actual_api_key_here"
        ):
            print("✅ API key appears to be set")
        else:
            print("⚠️  API key not set - please add your Gemini API key to .env file")

        print(f"✅ Model configured: {Config.GEMINI_MODEL}")
        print(f"✅ Output directory: {Config.OUTPUT_DIR}")
        print(f"✅ Supported formats: {Config.SUPPORTED_FORMATS}")

        return True

    except ImportError as e:
        print(f"❌ Failed to import config: {e}")
        return False
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False


def test_transcriber():
    """Test that the transcriber class can be instantiated."""
    print("\n📱 Testing transcriber...")

    try:
        from transcribe_photos import PhotoTranscriber

        print("✅ PhotoTranscriber class imported successfully")

        # Try to create instance (this will fail if API key is missing)
        try:
            transcriber = PhotoTranscriber()
            print("✅ PhotoTranscriber instance created successfully")
            print("✅ Gemini API connection appears to be working")
            return True
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                print("⚠️  API key not configured - please set it in .env file")
                return False
            else:
                print(f"❌ Transcriber error: {e}")
                return False

    except ImportError as e:
        print(f"❌ Failed to import PhotoTranscriber: {e}")
        return False
    except Exception as e:
        print(f"❌ Transcriber error: {e}")
        return False


def test_directories():
    """Test that required directories exist or can be created."""
    print("\n📁 Testing directories...")

    try:
        from config import Config

        # Test output directory creation
        output_dir = Path(Config.OUTPUT_DIR)
        if output_dir.exists():
            print(f"✅ Output directory exists: {output_dir}")
        else:
            try:
                output_dir.mkdir(exist_ok=True)
                print(f"✅ Output directory created: {output_dir}")
            except Exception as e:
                print(f"❌ Cannot create output directory: {e}")
                return False

        return True

    except Exception as e:
        print(f"❌ Directory test error: {e}")
        return False


def test_api_key_format():
    """Test if API key looks valid (basic format check)."""
    print("\n🔑 Testing API key format...")

    try:
        from config import Config

        if not Config.GEMINI_API_KEY:
            print("⚠️  No API key found")
            return False

        api_key = Config.GEMINI_API_KEY

        # Basic validation
        if api_key == "your_actual_api_key_here":
            print("⚠️  API key is still the placeholder value")
            return False

        if len(api_key) < 10:
            print("⚠️  API key seems too short")
            return False

        if not api_key.replace("-", "").replace("_", "").isalnum():
            print("⚠️  API key contains unexpected characters")
            return False

        print("✅ API key format looks valid")
        return True

    except Exception as e:
        print(f"❌ API key test error: {e}")
        return False


def show_instructions():
    """Show next steps if setup is not complete."""
    print("\n📋 Setup Instructions:")
    print("=" * 30)
    print("1. Get your Gemini API key:")
    print("   - Go to: https://makersuite.google.com/app/apikey")
    print("   - Create a new API key")
    print("   - Copy the key")
    print("")
    print("2. Set up your .env file:")
    print("   - Edit .env file")
    print("   - Replace 'your_actual_api_key_here' with your real API key")
    print("")
    print("3. Test again:")
    print("   - Run: python test_setup.py")
    print("")
    print("4. Start transcribing:")
    print("   - Run: python transcribe_photos.py")


def main():
    """Run all tests."""
    print("🧪 Photo Transcription Setup Test")
    print("=" * 40)

    # Run all tests
    imports_ok = test_imports()
    config_ok = test_config()
    directories_ok = test_directories()
    api_key_format_ok = test_api_key_format()
    transcriber_ok = test_transcriber()

    # Summary
    print("\n📋 Test Summary")
    print("=" * 20)

    all_tests = [imports_ok, config_ok, directories_ok]
    basic_setup_ok = all(all_tests)

    if basic_setup_ok:
        print("✅ Basic setup is working correctly!")

        if api_key_format_ok and transcriber_ok:
            print("✅ API key is configured and working!")
            print("✅ Ready to transcribe photos!")
            print("\nNext steps:")
            print("1. Run: python transcribe_photos.py")
            print("2. Point it to your photos folder")
            print("3. Wait for transcription to complete")
            print("4. Check results in transcribed_data/ folder")
            return 0
        else:
            print("⚠️  API key needs configuration")
            show_instructions()
            return 1
    else:
        print("❌ Setup has issues - please check the errors above")
        if not imports_ok:
            print("\n💡 Try running: pip install -r requirements.txt")
        show_instructions()
        return 1


if __name__ == "__main__":
    sys.exit(main())
