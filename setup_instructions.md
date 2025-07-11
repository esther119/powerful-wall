# Photo Transcription Setup

## Quick Start

1. **Activate virtual environment:**

   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Get Gemini API Key:**

   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key

4. **Set up environment:**

   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

5. **Run transcription:**
   ```bash
   python transcribe_photos.py
   ```

## Features

- ✅ Batch processing of multiple images
- ✅ Support for JPG, PNG, WEBP, HEIC formats
- ✅ Structured output (JSON or CSV)
- ✅ Error handling and progress tracking
- ✅ Metadata extraction (dates, file info)
- ✅ Confidence scoring
- ✅ Intermediate save points

## Configuration

Edit `config.py` to customize:

- Output format (JSON/CSV)
- Batch size
- Supported file formats
- Transcription prompt

## Output Structure

JSON output includes:

- Original image metadata
- Transcribed text
- Text type (handwritten/typed)
- Context information
- Confidence level
- Processing timestamp

## Usage Tips

1. **Organize your photos** in a single folder before running
2. **Check file sizes** - images over 4MB will be skipped
3. **Monitor API usage** - Gemini has rate limits
4. **Review results** - Check the confidence levels for accuracy
5. **Save intermediate results** - The system saves progress in batches

## Troubleshooting

- **API Key Error**: Make sure your `.env` file has the correct API key
- **Import Error**: Ensure virtual environment is activated
- **File Format Error**: Check that your images are in supported formats
- **Rate Limit**: Add delays between API calls if needed
