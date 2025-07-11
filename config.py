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
    
    For each text entry found, provide:
    1. The date in a clear format (Month Day format like "June 7" or "May 14")
    2. The text content
    3. Categorize into one of these categories:
       - technical_skills (coding, development, technical work)
       - professional_presentation (presentations, demos, work interactions)
       - self_image (personal reflections, self-perception)
       - social_interactions (conversations, relationships, social activities)
       - creative_work (videos, projects, artistic endeavors)
       - personal_growth (learning, development, insights)
       - physical_wellness (health, body, recovery)
       - career_development (job search, networking, career moves)
    4. Classify confidence type as either "personal" or "professional"
    5. Rate the power level from 1-10 (how confident/powerful the person felt)
    
    Return ONLY valid JSON in this exact format:
    ```json
    [
      {
        "date": "June 7",
        "text": "Feel powerful when looking in the mirror",
        "category": "self_image",
        "confidence_type": "personal",
        "power_level": 8
      },
      {
        "date": "June 7", 
        "text": "Confidently & Playfully presents cursor to Roma",
        "category": "professional_presentation",
        "confidence_type": "professional", 
        "power_level": 9
      }
    ]
    ```
    
    Important: Return ONLY the JSON array, no other text or explanations.
    """
