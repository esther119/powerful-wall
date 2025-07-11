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
    Analyze this image and extract all handwritten text content about feelings, emotions, and personal reflections.
    
    For each date found, provide:
    1. The date in a clear format
    2. Each separate text entry 
    3. Categorize each entry into one of these categories:
       - technical_skills (coding, development, technical work)
       - professional_presentation (presentations, demos, work interactions)
       - self_image (personal reflections, self-perception)
       - social_interactions (conversations, relationships, social activities)
       - creative_work (videos, projects, artistic endeavors)
       - personal_growth (learning, development, insights)
       - physical_wellness (health, body, recovery)
       - career_development (job search, networking, career moves)
    4. Classify confidence type as either "personal" or "professional"
    
    Please provide the transcription in this JSON-like format:
    **DATE:** [Date in Month Day format]
    **ENTRY:** [Text content]
    **CATEGORY:** [One of the categories above]
    **TYPE:** [personal or professional]
    
    Continue for all entries found.
    """
