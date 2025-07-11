import google.generativeai as genai
import os
import json
import pandas as pd
from pathlib import Path
from PIL import Image
import time
from tqdm import tqdm
from datetime import datetime
from config import Config


class PhotoTranscriber:
    def __init__(self):
        """Initialize the transcriber with Gemini API."""
        if not Config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in your .env file"
            )

        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

        # Create output directory
        self.output_dir = Path(Config.OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)

        self.results = []

    def is_valid_image(self, file_path):
        """Check if file is a valid image."""
        path = Path(file_path)

        # Check file extension
        if path.suffix.lower() not in Config.SUPPORTED_FORMATS:
            return False

        # Check file size
        if path.stat().st_size > Config.MAX_IMAGE_SIZE:
            print(
                f"Warning: {path.name} is too large ({path.stat().st_size / 1024 / 1024:.1f}MB)"
            )
            return False

        # Try to open with PIL
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False

    def get_image_metadata(self, file_path):
        """Extract metadata from image."""
        path = Path(file_path)
        stat = path.stat()

        metadata = {
            "filename": path.name,
            "filepath": str(path),
            "file_size": stat.st_size,
            "modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created_date": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }

        # Try to get image dimensions
        try:
            with Image.open(file_path) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["format"] = img.format
        except Exception:
            pass

        return metadata

    def transcribe_image(self, image_path):
        """Transcribe text from a single image using Gemini."""
        try:
            # Load and prepare image
            image = Image.open(image_path)

            # Generate transcription
            response = self.model.generate_content([Config.TRANSCRIPTION_PROMPT, image])

            # Get metadata
            metadata = self.get_image_metadata(image_path)

            # Parse response
            transcription_text = response.text if response.text else ""

            result = {
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata,
                "raw_response": transcription_text,
                "parsed_data": self.parse_transcription(transcription_text),
                "success": True,
                "error": None,
            }

            return result

        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "metadata": self.get_image_metadata(image_path),
                "raw_response": "",
                "parsed_data": {},
                "success": False,
                "error": str(e),
            }

    def parse_transcription(self, text):
        """Parse the structured transcription response."""
        parsed = {"text": "", "type": "", "context": "", "confidence": ""}

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("TEXT:"):
                parsed["text"] = line[5:].strip()
            elif line.startswith("TYPE:"):
                parsed["type"] = line[5:].strip()
            elif line.startswith("CONTEXT:"):
                parsed["context"] = line[8:].strip()
            elif line.startswith("CONFIDENCE:"):
                parsed["confidence"] = line[11:].strip()

        # If parsing failed, put everything in text field
        if not parsed["text"] and text:
            parsed["text"] = text
            parsed["type"] = "unknown"
            parsed["confidence"] = "unknown"

        return parsed

    def transcribe_batch(self, image_paths):
        """Transcribe a batch of images."""
        results = []

        for image_path in tqdm(image_paths, desc="Transcribing images"):
            if not self.is_valid_image(image_path):
                print(f"Skipping invalid image: {image_path}")
                continue

            result = self.transcribe_image(image_path)
            results.append(result)

            # Small delay to respect API limits
            time.sleep(0.5)

        return results

    def transcribe_folder(self, folder_path):
        """Transcribe all images in a folder."""
        folder = Path(folder_path)

        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        # Find all image files
        image_files = []
        for ext in Config.SUPPORTED_FORMATS:
            image_files.extend(folder.glob(f"*{ext}"))
            image_files.extend(folder.glob(f"*{ext.upper()}"))

        print(f"Found {len(image_files)} images to transcribe")

        # Process in batches
        all_results = []
        for i in range(0, len(image_files), Config.BATCH_SIZE):
            batch = image_files[i : i + Config.BATCH_SIZE]
            batch_results = self.transcribe_batch(batch)
            all_results.extend(batch_results)

            # Save intermediate results
            self.save_results(all_results, suffix=f"_batch_{i//Config.BATCH_SIZE + 1}")

        self.results = all_results
        return all_results

    def save_results(self, results=None, suffix=""):
        """Save transcription results to file."""
        if results is None:
            results = self.results

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if Config.OUTPUT_FORMAT == "json":
            filename = f"transcriptions_{timestamp}{suffix}.json"
            filepath = self.output_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

        elif Config.OUTPUT_FORMAT == "csv":
            filename = f"transcriptions_{timestamp}{suffix}.csv"
            filepath = self.output_dir / filename

            # Flatten results for CSV
            flat_results = []
            for result in results:
                flat_result = {
                    "timestamp": result["timestamp"],
                    "filename": result["metadata"]["filename"],
                    "filepath": result["metadata"]["filepath"],
                    "file_size": result["metadata"]["file_size"],
                    "modified_date": result["metadata"]["modified_date"],
                    "transcribed_text": result["parsed_data"].get("text", ""),
                    "text_type": result["parsed_data"].get("type", ""),
                    "context": result["parsed_data"].get("context", ""),
                    "confidence": result["parsed_data"].get("confidence", ""),
                    "success": result["success"],
                    "error": result["error"],
                }
                flat_results.append(flat_result)

            df = pd.DataFrame(flat_results)
            df.to_csv(filepath, index=False)

        print(f"Results saved to: {filepath}")
        return filepath


def main():
    """Main function to run transcription."""
    transcriber = PhotoTranscriber()

    # Use fixed input folder path
    folder_path = "input_photos"
    print(f"Using input folder: {folder_path}")

    try:
        results = transcriber.transcribe_folder(folder_path)
        output_file = transcriber.save_results(results)

        print(f"\nTranscription complete!")
        print(f"Processed {len(results)} images")
        print(f"Results saved to: {output_file}")

        # Show summary
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful

        print(f"\nSummary:")
        print(f"✅ Successfully transcribed: {successful}")
        print(f"❌ Failed: {failed}")

        if successful > 0:
            print(f"\nSample transcription:")
            for result in results:
                if result["success"] and result["parsed_data"]["text"]:
                    print(f"File: {result['metadata']['filename']}")
                    print(f"Text: {result['parsed_data']['text'][:200]}...")
                    break

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
