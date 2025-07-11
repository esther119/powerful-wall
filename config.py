import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-1.5-flash"  # or 'gemini-1.5-pro' for higher quality

    # Image Processing Settings
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB max file size
    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}

    # Output Settings
    OUTPUT_DIR = "transcribed_data"
    OUTPUT_FORMAT = "json"  # 'json' or 'csv'
    BATCH_SIZE = 10  # Number of images to process in one batch

    # Transcription Settings
    TRANSCRIPTION_PROMPT = """
    Analyze this image and extract all text content. Focus on:
    1. Any handwritten or typed text about feelings, emotions, or personal reflections
    2. Preserve the original tone and meaning
    3. If there are multiple text elements, separate them clearly
    4. All the text are handwritten
    5. Include any context about the setting if relevant to the text
    
    Please provide the transcription in this format:
    TEXT: [extracted text]
    CONTEXT: [brief description of setting/context if relevant]
    CONFIDENCE: [high/medium/low based on text clarity]
    """
