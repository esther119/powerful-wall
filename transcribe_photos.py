import google.generativeai as genai
import os
import json
import pandas as pd
from pathlib import Path
from PIL import Image
import time
from tqdm import tqdm
from datetime import datetime
import re
from typing import Dict, List, Optional, Tuple
from config import Config


class PhotoTranscriber:
    """Elegant photo transcription system for confidence tracking."""
    
    def __init__(self):
        """Initialize the transcriber with Gemini API."""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file")

        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        # Create output directory
        self.output_dir = Path(Config.OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        
        self.results = []

    def is_valid_image(self, file_path: Path) -> bool:
        """Check if file is a valid image."""
        try:
            # Check file extension and size
            if file_path.suffix.lower() not in Config.SUPPORTED_FORMATS:
                return False
            
            if file_path.stat().st_size > Config.MAX_IMAGE_SIZE:
                print(f"Warning: {file_path.name} is too large ({file_path.stat().st_size / 1024 / 1024:.1f}MB)")
                return False
            
            # Verify image can be opened
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False

    def transcribe_image(self, image_path: Path) -> Dict:
        """Transcribe text from a single image using Gemini."""
        try:
            image = Image.open(image_path)
            response = self.model.generate_content([Config.TRANSCRIPTION_PROMPT, image])
            
            transcription_text = response.text if response.text else ""
            parsed_data = self._parse_json_response(transcription_text)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "filename": image_path.name,
                "parsed_data": parsed_data,
                "success": True,
                "error": None,
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "filename": image_path.name,
                "parsed_data": {},
                "success": False,
                "error": str(e),
            }

    def _parse_json_response(self, text: str) -> Dict:
        """Parse JSON response from Gemini API."""
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in text:
                json_match = re.search(r'```json\s*(\[.*?\])\s*```', text, re.DOTALL)
                if json_match:
                    text = json_match.group(1)
            
            # Parse the JSON entries
            entries = json.loads(text)
            if not isinstance(entries, list):
                return {}
            
            # Group entries by date and calculate metrics
            date_groups = {}
            for entry in entries:
                if not self._is_valid_entry(entry):
                    continue
                
                date = self._normalize_date(entry["date"])
                if date not in date_groups:
                    date_groups[date] = {"entries": []}
                
                # Add entry with all required fields
                formatted_entry = {
                    "text": entry["text"],
                    "category": entry["category"],
                    "confidence_type": entry["confidence_type"],
                    "power_level": int(entry["power_level"])
                }
                date_groups[date]["entries"].append(formatted_entry)
            
            # Calculate daily metrics
            for date, data in date_groups.items():
                entries = data["entries"]
                power_levels = [entry["power_level"] for entry in entries]
                confidence_types = [entry["confidence_type"] for entry in entries]
                
                # Calculate daily average
                data["daily_confidence_average"] = round(sum(power_levels) / len(power_levels), 1)
                
                # Determine dominant confidence area
                data["dominant_confidence_area"] = self._get_dominant_type(confidence_types)
            
            return date_groups
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse JSON response: {e}")
            return {}

    def _is_valid_entry(self, entry: Dict) -> bool:
        """Check if entry has all required fields."""
        required_fields = ["date", "text", "category", "confidence_type", "power_level"]
        return all(field in entry and entry[field] for field in required_fields)

    def _normalize_date(self, date_str: str) -> str:
        """Convert date string to ISO format (YYYY-MM-DD)."""
        month_map = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12",
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05",
            "jun": "06", "jul": "07", "aug": "08", "sep": "09", "oct": "10",
            "nov": "11", "dec": "12"
        }
        
        # Extract month and day from various formats
        match = re.search(r'(\w+)\s+(\d+)', date_str.lower())
        if match:
            month_str, day_str = match.groups()
            month = month_map.get(month_str, "01")
            day = day_str.zfill(2)
            current_year = datetime.now().year
            return f"{current_year}-{month}-{day}"
        
        return date_str

    def _get_dominant_type(self, confidence_types: List[str]) -> str:
        """Get the most common confidence type."""
        if not confidence_types:
            return "personal"
        
        type_counts = {}
        for conf_type in confidence_types:
            type_counts[conf_type] = type_counts.get(conf_type, 0) + 1
        
        return max(type_counts, key=lambda x: type_counts[x])

    def transcribe_folder(self, folder_path: str) -> List[Dict]:
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
        
        # Process images with progress bar
        all_results = []
        for image_path in tqdm(image_files, desc="Transcribing images"):
            if not self.is_valid_image(image_path):
                print(f"Skipping invalid image: {image_path}")
                continue
            
            result = self.transcribe_image(image_path)
            all_results.append(result)
            
            # Respect API limits
            time.sleep(0.5)
        
        self.results = all_results
        return all_results

    def save_results(self, results: Optional[List[Dict]] = None, suffix: str = "") -> Path:
        """Save transcription results in the target format."""
        if results is None:
            results = self.results
        
        # Merge all parsed data into single output format
        consolidated_data = {}
        
        for result in results:
            if result["success"] and result["parsed_data"]:
                for date, data in result["parsed_data"].items():
                    if date in consolidated_data:
                        # Merge entries for the same date
                        consolidated_data[date]["entries"].extend(data["entries"])
                        
                        # Recalculate daily average
                        all_power_levels = [entry["power_level"] for entry in consolidated_data[date]["entries"]]
                        consolidated_data[date]["daily_confidence_average"] = round(
                            sum(all_power_levels) / len(all_power_levels), 1
                        )
                        
                        # Recalculate dominant area
                        all_confidence_types = [entry["confidence_type"] for entry in consolidated_data[date]["entries"]]
                        consolidated_data[date]["dominant_confidence_area"] = self._get_dominant_type(all_confidence_types)
                    else:
                        consolidated_data[date] = data
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcriptions_{timestamp}{suffix}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to: {filepath}")
        return filepath

    def get_summary(self) -> Dict:
        """Get a summary of transcription results."""
        if not self.results:
            return {"total": 0, "successful": 0, "failed": 0, "entries": 0}
        
        successful = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - successful
        
        total_entries = 0
        for result in self.results:
            if result["success"]:
                for date_data in result["parsed_data"].values():
                    total_entries += len(date_data.get("entries", []))
        
        return {
            "total": len(self.results),
            "successful": successful,
            "failed": failed,
            "entries": total_entries
        }


def main():
    """Main function to run transcription."""
    transcriber = PhotoTranscriber()
    
    folder_path = "input_photos"
    print(f"Using input folder: {folder_path}")
    
    try:
        results = transcriber.transcribe_folder(folder_path)
        output_file = transcriber.save_results(results)
        
        # Show summary
        summary = transcriber.get_summary()
        print(f"\n🎉 Transcription complete!")
        print(f"📊 Summary:")
        print(f"   • Total images: {summary['total']}")
        print(f"   • ✅ Successful: {summary['successful']}")
        print(f"   • ❌ Failed: {summary['failed']}")
        print(f"   • 📝 Total entries: {summary['entries']}")
        print(f"   • 💾 Output: {output_file}")
        
        # Show sample if available
        if summary['successful'] > 0:
            print(f"\n📋 Sample output format:")
            sample_data = {}
            for result in results:
                if result["success"] and result["parsed_data"]:
                    sample_data = result["parsed_data"]
                    break
            
            if sample_data:
                sample_date = list(sample_data.keys())[0]
                sample_entry = sample_data[sample_date]
                print(f"  \"{sample_date}\": {{")
                print(f"    \"entries\": [")
                if sample_entry["entries"]:
                    entry = sample_entry["entries"][0]
                    print(f"      {{")
                    print(f"        \"text\": \"{entry['text'][:50]}...\",")
                    print(f"        \"category\": \"{entry['category']}\",")
                    print(f"        \"confidence_type\": \"{entry['confidence_type']}\",")
                    print(f"        \"power_level\": {entry['power_level']}")
                    print(f"      }}")
                print(f"    ],")
                print(f"    \"daily_confidence_average\": {sample_entry['daily_confidence_average']},")
                print(f"    \"dominant_confidence_area\": \"{sample_entry['dominant_confidence_area']}\"")
                print(f"  }}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
