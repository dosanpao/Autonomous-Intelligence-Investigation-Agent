import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_PATH = os.path.join(BASE_DIR, "JsonOutputs", "hypothesis.json")

# -----------------------------
# Gemini Client
# -----------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# Load Hypothesis Data
# -----------------------------
def load_hypothesis(path):
    with open(path, "r") as f:
        return json.load(f)

# -----------------------------
# Format Prompt
# -----------------------------
def format_prompt(hypothesis: dict) -> str:
    return f"""
You are SIGMA, a classified intelligence brief writer.

Using the hypothesis data below, generate a formal intelligence dossier.

RULES:
- Write in the style of a declassified intelligence document
- Be precise and clinical in tone
- Return ONLY valid JSON, no markdown, no explanation

=== HYPOTHESIS DATA ===
{json.dumps(hypothesis, indent=2)}

=== TASK ===
Return JSON in EXACTLY this format:

{{
  "classification": "TOP SECRET // SIGMA INTEL",
  "subject_profile": {{
    "likely_name": "",
    "username": "",
    "summary": ""
  }},
  "digital_footprint": {{
    "platforms_confirmed": [],
    "platforms_possible": [],
    "summary": ""
  }},
  "location_estimate": {{
    "region": "",
    "confidence": 0.0,
    "reasoning": ""
  }},
  "behavioral_analysis": {{
    "patterns": [],
    "summary": ""
  }},
  "confidence_metrics": {{
    "identity": 0.0,
    "location": 0.0,
    "occupation": 0.0,
    "overall": 0.0
  }},
  "analyst_note": ""
}}
"""

# -----------------------------
# Brief Agent
# -----------------------------
def run_brief_agent(hypothesis: dict) -> str:
    prompt = format_prompt(hypothesis)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

# -----------------------------
# Main
# -----------------------------
def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    hypothesis = load_hypothesis(HYPOTHESIS_PATH)
    brief = run_brief_agent(hypothesis)

    print("\n================ SIGMA INTEL BRIEF ================\n")
    print(brief)
    print("\n====================================================\n")

    # save to file for UI
    os.makedirs(os.path.join(BASE_DIR, "JsonOutputs"), exist_ok=True)
    output_path = os.path.join(BASE_DIR, "JsonOutputs", "brief.json")
    with open(output_path, "w") as f:
        f.write(brief)

    print(f"Saved to {output_path}")

# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    main()