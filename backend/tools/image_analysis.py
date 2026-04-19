import os
import base64
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# Image Loader
# -----------------------------
def load_image(image_input: str) -> tuple[bytes, str]:
    """
    Accepts a file path or a base64-encoded string.
    Returns (raw_bytes, mime_type).
    Supports: jpg, jpeg, png, webp, gif
    """
    ext_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    path = Path(image_input)
    if path.exists():
        ext = path.suffix.lower()
        mime = ext_map.get(ext, "image/jpeg")
        with open(path, "rb") as f:
            return f.read(), mime

    # Treat as raw base64 string (strip data URI prefix if present)
    if "," in image_input:
        header, data = image_input.split(",", 1)
        # Extract mime from header like "data:image/png;base64"
        mime = header.split(":")[1].split(";")[0] if ":" in header else "image/jpeg"
    else:
        data = image_input
        mime = "image/jpeg"

    return base64.b64decode(data), mime


# -----------------------------
# Core Analysis Function
# -----------------------------
def analyze_image(image_input: str) -> dict:
    """
    Sends image to Gemini Vision for strict visual + metadata analysis.
    No web scraping, no cross-referencing — only what can be inferred from the image itself.

    Args:
        image_input: file path (str) OR base64-encoded image string

    Returns:
        dict with location_clues, visual_description, and metadata_clues
    """
    image_bytes, mime_type = load_image(image_input)

    prompt = """You are a forensic image analyst for an intelligence system named SIGMA.

Your task is to perform strict visual analysis of the provided image.

STRICT RULES:
- Analyze ONLY what is visible in the image itself
- Do NOT search the web, cross-reference databases, or use external knowledge about specific people/events
- Do NOT identify real individuals by name
- Report only factual visual observations and reasonable inferences
- Use probabilistic language ("likely", "consistent with", "suggests") for inferences
- If something cannot be determined, say so explicitly

ANALYZE AND RETURN A JSON OBJECT with this exact structure:

{
  "location_clues": {
    "country_region": "<inferred country or region, or null>",
    "urban_rural": "<'urban', 'suburban', 'rural', or null>",
    "environment_type": "<e.g. 'café', 'university campus', 'street', 'park', etc., or null>",
    "architectural_style": "<describe style if buildings visible, or null>",
    "signage_language": "<language(s) on any visible signs, or null>",
    "vegetation": "<visible plant types that suggest climate/region, or null>",
    "confidence": <float 0.0–1.0>
  },
  "time_clues": {
    "time_of_day": "<'morning', 'midday', 'afternoon', 'evening', 'night', or null>",
    "season": "<'spring', 'summer', 'autumn', 'winter', or null>",
    "estimated_year_range": "<e.g. '2010–2020' based on technology/fashion visible, or null>",
    "confidence": <float 0.0–1.0>
  },
  "subject_clues": {
    "people_present": <true or false>,
    "approximate_age_range": "<e.g. '20s–30s', or null if no people>",
    "apparent_gender": "<observations only, or null>",
    "clothing_style": "<describe style/formality if people visible, or null>",
    "activity": "<what subjects appear to be doing, or null>",
    "confidence": <float 0.0–1.0>
  },
  "device_and_metadata_clues": {
    "photo_style": "<'professional', 'casual/phone', 'security camera', 'screenshot', etc.>",
    "visible_devices": "<list any phones, laptops, screens visible with observable brand/model hints>",
    "exif_indicators": "<any in-image clues about capture device, e.g. watermarks, UI overlays>",
    "compression_artifacts": "<'high', 'medium', 'low', or null — indicates platform re-upload history>",
    "confidence": <float 0.0–1.0>
  },
  "visual_description": "<2–4 sentence neutral summary of the full image>",
  "intelligence_summary": "<2–3 sentence synthesis of the most useful intelligence clues for an OSINT investigation>"
}

Return ONLY the JSON object. No markdown fences, no explanation outside the JSON.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            types.Part.from_text(text=prompt),
        ],
    )

    raw = response.text.strip()

    # Strip markdown fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    import json
    return json.loads(raw)


# -----------------------------
# Standalone Entry Point
# -----------------------------
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python image_analysis.py <image_path_or_base64>")
        sys.exit(1)

    result = analyze_image(sys.argv[1])
    print(json.dumps(result, indent=2))