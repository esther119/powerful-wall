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
        """Parse the structured transcription response and organize by date."""
        import re
        from datetime import datetime

        date_entries = {}

        # Try JSON format first (what AI actually returns)
        if text.strip().startswith("```json") or (
            '"DATE"' in text and '"ENTRY"' in text
        ):
            try:
                # Extract JSON from markdown code block if present
                if text.strip().startswith("```json"):
                    json_text = text.split("```json")[1].split("```")[0].strip()
                else:
                    json_text = text

                import json

                entries_list = json.loads(json_text)

                for entry_data in entries_list:
                    date_str = entry_data.get("DATE", "")
                    text_content = entry_data.get("ENTRY", "")
                    category = entry_data.get("CATEGORY", "unknown")
                    confidence_type = entry_data.get("TYPE", "personal")

                    if date_str and text_content:
                        iso_date = self._convert_to_iso_date(date_str)
                        entry = {
                            "date": iso_date,
                            "text": text_content,
                            "category": category,
                            "confidence_type": confidence_type,
                        }
                        self._add_entry_to_date(date_entries, entry)

            except (json.JSONDecodeError, KeyError, IndexError) as e:
# JSON parsing failed, trying fallback methods
                # Fall through to other parsing methods

        # Try the structured format
        elif "**DATE:**" in text and "**ENTRY:**" in text:
            # New structured format
            current_entry = {}
            lines = text.split("\n")

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("**DATE:**"):
                    # Save previous entry if exists
                    if current_entry and "date" in current_entry:
                        self._add_entry_to_date(date_entries, current_entry)

                    # Start new entry
                    date_str = line.replace("**DATE:**", "").strip()
                    iso_date = self._convert_to_iso_date(date_str)
                    current_entry = {"date": iso_date}

                elif line.startswith("**ENTRY:**"):
                    current_entry["text"] = line.replace("**ENTRY:**", "").strip()

                elif line.startswith("**CATEGORY:**"):
                    current_entry["category"] = line.replace(
                        "**CATEGORY:**", ""
                    ).strip()

                elif line.startswith("**TYPE:**"):
                    current_entry["confidence_type"] = line.replace(
                        "**TYPE:**", ""
                    ).strip()

            # Don't forget the last entry
            if current_entry and "date" in current_entry:
                self._add_entry_to_date(date_entries, current_entry)

        else:
            # Fallback to old format parsing with auto-categorization
# Using fallback parsing for old format
            sections = re.split(r"\*\*TEXT \d+:\*\*", text)

            for section in sections[1:]:  # Skip the first empty section
                lines = section.strip().split("\n")
                if not lines:
                    continue

                date_line = lines[0].strip()

                # Extract date from first line
                date_match = re.search(
                    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d+(?:st|nd|rd|th)?)",
                    date_line,
                )
                if date_match:
                    current_date = self._convert_to_iso_date(date_match.group(1))

                    # Extract text entries
                    texts = []
                    for line in lines[1:]:
                        line = line.strip()
                        if (
                            line.startswith("①")
                            or line.startswith("②")
                            or line.startswith("③")
                            or line.startswith("④")
                        ):
                            clean_text = re.sub(r"^[①②③④]\s*", "", line).strip()
                            if clean_text:
                                texts.append(clean_text)
                        elif (
                            line
                            and not line.startswith("**")
                            and not line.startswith("CONTEXT:")
                            and not line.startswith("CONFIDENCE:")
                        ):
                            if line and not line.startswith("A collection"):
                                texts.append(line)

                    # Auto-categorize and create entries
                    if current_date and texts:
                        for text in texts:
                            entry = {
                                "text": text,
                                "category": self._auto_categorize(text),
                                "confidence_type": self._determine_confidence_type(
                                    text
                                ),
                            }
                            self._add_entry_to_date(
                                date_entries, {"date": current_date, **entry}
                            )

        # Calculate daily summaries
        for date, data in date_entries.items():
            if "entries" in data:
                categories = [
                    entry.get("category", "unknown") for entry in data["entries"]
                ]
                if categories:
                    dominant_category = max(set(categories), key=categories.count)
                    data["dominant_confidence_area"] = dominant_category


        return date_entries

    def _auto_categorize(self, text):
        """Auto-categorize text based on keywords."""
        text_lower = text.lower()

        # Technical skills
        if any(
            word in text_lower
            for word in [
                "frontend",
                "backend",
                "coding",
                "code",
                "js",
                "javascript",
                "react",
                "python",
                "bug",
                "pipeline",
                "sentry",
            ]
        ):
            return "technical_skills"

        # Professional presentation
        if any(
            word in text_lower
            for word in [
                "present",
                "demo",
                "cursor",
                "laugh",
                "confidently",
                "playfully",
            ]
        ):
            return "professional_presentation"

        # Self image
        if any(
            word in text_lower
            for word in ["mirror", "powerful", "growth", "mood", "perfect"]
        ):
            return "self_image"

        # Social interactions
        if any(
            word in text_lower
            for word in ["talk", "therapist", "ethan", "friends", "annie"]
        ):
            return "social_interactions"

        # Creative work
        if any(
            word in text_lower
            for word in ["video", "pomodoro", "ocean", "curiosity", "meditation"]
        ):
            return "creative_work"

        # Career development
        if any(
            word in text_lower for word in ["recruiter", "email", "interview", "job"]
        ):
            return "career_development"

        # Physical wellness
        if any(
            word in text_lower for word in ["teeth", "recovery", "dentist", "health"]
        ):
            return "physical_wellness"

        # Default to personal growth
        return "personal_growth"

    def _determine_confidence_type(self, text):
        """Determine if this is personal or professional confidence."""
        text_lower = text.lower()

        # Professional indicators
        if any(
            word in text_lower
            for word in [
                "work",
                "frontend",
                "backend",
                "demo",
                "cursor",
                "interview",
                "recruiter",
                "pipeline",
            ]
        ):
            return "professional"

        # Personal indicators
        if any(
            word in text_lower
            for word in [
                "mirror",
                "feel",
                "growth",
                "meditation",
                "personal",
                "therapist",
            ]
        ):
            return "personal"

        # Default to personal
        return "personal"

    def _add_entry_to_date(self, date_entries, entry):
        """Helper method to add an entry to the appropriate date."""
        date = entry["date"]
        if date not in date_entries:
            date_entries[date] = {"entries": []}

        # Only add if we have the required fields
        if all(key in entry for key in ["text", "category", "confidence_type"]):
            entry_data = {
                "text": entry["text"],
                "category": entry["category"],
                "confidence_type": entry["confidence_type"],
            }
            date_entries[date]["entries"].append(entry_data)

    def _convert_to_iso_date(self, date_str):
        """Convert various date formats to ISO format (YYYY-MM-DD)."""
        import re
        from datetime import datetime

        # Handle formats like "June 7th", "May 14th", "Apr 22nd"
        month_map = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }

        # Extract month and day
        match = re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d+)", date_str
        )
        if match:
            month_abbr = match.group(1)
            day = match.group(2).zfill(2)  # Zero pad day
            month = month_map.get(month_abbr, "01")

            # Default to current year (you can modify this logic)
            current_year = datetime.now().year
            return f"{current_year}-{month}-{day}"

        # Fallback: return original if can't parse
        return date_str

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

        # Create simplified format for output
        simplified_results = {}

        for result in results:
            if result["success"] and result["parsed_data"]:
                parsed_data = result["parsed_data"]

                # Handle the new structured format
                for date, data in parsed_data.items():
                    if date in simplified_results:
                        # Merge entries if date already exists
                        if "entries" in data:
                            simplified_results[date]["entries"].extend(data["entries"])
                    else:
                        simplified_results[date] = data

        # Save the simplified format
        if Config.OUTPUT_FORMAT == "json":
            filename = f"transcriptions_{timestamp}{suffix}.json"
            filepath = self.output_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(simplified_results, f, indent=2, ensure_ascii=False)

        elif Config.OUTPUT_FORMAT == "csv":
            filename = f"transcriptions_{timestamp}{suffix}.csv"
            filepath = self.output_dir / filename

            # Flatten the new structured results for CSV
            flat_results = []
            for date, data in simplified_results.items():
                if "entries" in data:
                    for entry in data["entries"]:
                        flat_results.append(
                            {
                                "date": date,
                                "text": entry["text"],
                                "category": entry["category"],
                                "confidence_type": entry["confidence_type"],
                                "dominant_area": data.get(
                                    "dominant_confidence_area", "unknown"
                                ),
                            }
                        )

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
                if result["success"] and result["parsed_data"]:
                    print(f"File: {result['metadata']['filename']}")
                    # Show first few dates and texts
                    parsed_data = result["parsed_data"]
                    if isinstance(parsed_data, dict):
                        for date, data in list(parsed_data.items())[
                            :2
                        ]:  # Show first 2 dates
                            print(f"Date: {date}")
                            if "entries" in data:
                                for i, entry in enumerate(
                                    data["entries"][:2]
                                ):  # Show first 2 entries per date
                                    print(f"  Entry {i+1}: {entry['text'][:100]}...")
                                    print(f"    Category: {entry['category']}")
                                    print(f"    Type: {entry['confidence_type']}")
                    break

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
