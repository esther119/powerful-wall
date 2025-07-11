# Photo Transcription with Gemini AI

A powerful tool to transcribe text from photos using Google's Gemini AI, specifically designed for analyzing personal reflection texts and powerful feeling notes.

## 🚀 Quick Start

1. **Activate virtual environment:**

   ```bash
   source venv/bin/activate
   ```

2. **Get your Gemini API Key:**

   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key

3. **Set up your API key:**

   ```bash
   # Edit .env file and replace with your actual API key
   nano .env
   ```

4. **Run the transcription:**
   ```bash
   python transcribe_photos.py
   ```

## 📁 What You'll Get

- **Structured JSON output** with transcribed text, confidence levels, and metadata
- **Batch processing** of multiple images
- **Error handling** and progress tracking
- **Metadata extraction** (dates, file sizes, dimensions)
- **Confidence scoring** for transcription quality

## 🎯 Next Steps

After transcription, you can use the JSON output for:

- Theme analysis and pattern recognition
- Sentiment analysis over time
- Visualization of your powerful feeling journey
- AI-powered insights into your personal growth

## 📊 Output Structure

Each transcription includes:

- **Original text** exactly as found in the image
- **Text type** (handwritten/typed/mixed)
- **Context** about the setting or situation
- **Confidence level** of the transcription
- **File metadata** (dates, sizes, formats)

Ready to discover patterns in your powerful feelings! 🌟
