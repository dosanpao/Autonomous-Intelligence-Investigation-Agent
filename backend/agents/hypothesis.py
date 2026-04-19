import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
RECON_PATH = os.path.join(BASE_DIR, "JsonOutputs", "recon.json")

# -----------------------------
# Gemini Client (NEW SDK)
# -----------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def load_recon(path):
    with open(path, "r") as f:
        return json.load(f)

# -----------------------------
# Format Prompt — routes by mode
# -----------------------------
def format_recon_for_prompt(recon):
    mode = recon.get("mode", "username")
    if mode == "url":
        return _format_url_prompt(recon)
    elif mode == "image":
        return _format_image_prompt(recon)
    else:
        return _format_username_prompt(recon)


def _format_username_prompt(recon):
    image_section = _format_image_section(recon.get("image_analysis"))
    return f"""
You are SIGMA, an OSINT intelligence hypothesis engine.

You are analyzing structured reconnaissance data about a digital identity.

RULES:
- Only use provided evidence
- Do NOT invent facts
- All outputs must be probabilistic
- Return ONLY valid JSON (no markdown, no explanation)

=== RECON DATA ===

Username: {recon.get("username")}

Platform Accounts:
{json.dumps(recon.get("accounts_found"), indent=2)}

Similar Usernames:
{json.dumps(recon.get("similar_usernames"), indent=2)}

Name Inference:
{json.dumps(recon.get("name_inference"), indent=2)}

{image_section}

Metadata:
{json.dumps(recon.get("metadata"), indent=2)}

=== TASK ===
Generate structured intelligence hypotheses. Return JSON in this exact format:

{{
  "identity_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "occupation_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "location_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "behavioral_analysis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "cross_platform_linking": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "summary": ""
}}
"""


def _format_image_prompt(recon):
    image_section = _format_image_section(recon.get("image_analysis"))
    return f"""
You are SIGMA, an OSINT intelligence hypothesis engine.

You are analyzing the results of a forensic image analysis.

RULES:
- Only use provided evidence
- Do NOT invent facts
- All outputs must be probabilistic
- Return ONLY valid JSON (no markdown, no explanation)

=== IMAGE ANALYSIS DATA ===

{image_section}

=== TASK ===
Generate structured intelligence hypotheses from the image evidence only.
Return JSON in this exact format:

{{
  "identity_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "occupation_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "location_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "behavioral_analysis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "cross_platform_linking": {{ "claim": "Insufficient data for cross-platform analysis from image alone.", "confidence": 0.0, "evidence": [] }},
  "summary": ""
}}
"""


def _format_url_prompt(recon):
    url_data = recon.get("url_analysis", {})
    return f"""
You are SIGMA, an OSINT intelligence hypothesis engine.

You are analyzing a structured intelligence report about a website.

RULES:
- Only use provided evidence
- Do NOT invent facts
- All outputs must be probabilistic
- Return ONLY valid JSON (no markdown, no explanation)

=== URL INTELLIGENCE DATA ===

{json.dumps(url_data, indent=2)}

=== TASK ===
Generate structured intelligence hypotheses about the website operator and purpose.
Return JSON in this exact format:

{{
  "identity_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "occupation_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "location_hypothesis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "behavioral_analysis": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "cross_platform_linking": {{ "claim": "", "confidence": 0.0, "evidence": [] }},
  "summary": ""
}}
"""


def _format_image_section(image_data):
    if not image_data or "error" in image_data:
        return "Image Analysis: None provided."
    return f"""Image Analysis:
  Location Clues:  {json.dumps(image_data.get("location_clues"), indent=4)}
  Time Clues:      {json.dumps(image_data.get("time_clues"), indent=4)}
  Subject Clues:   {json.dumps(image_data.get("subject_clues"), indent=4)}
  Device Clues:    {json.dumps(image_data.get("device_and_metadata_clues"), indent=4)}
  Visual Summary:  {image_data.get("visual_description", "")}
  Intel Summary:   {image_data.get("intelligence_summary", "")}"""


# -----------------------------
# Hypothesis Agent
# -----------------------------
def run_hypothesis_agent(recon):
    prompt = format_recon_for_prompt(recon)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


# -----------------------------
# Standalone test
# -----------------------------
def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("Missing GEMINI_API_KEY")
    recon = load_recon(RECON_PATH)
    result = run_hypothesis_agent(recon)

    clean = result.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1]
    if clean.endswith("```"):
        clean = clean.rsplit("```", 1)[0]
    clean = clean.strip()

    print("\n================ SIGMA HYPOTHESIS ================\n")
    print(clean)

    os.makedirs(os.path.join(BASE_DIR, "JsonOutputs"), exist_ok=True)
    with open(os.path.join(BASE_DIR, "JsonOutputs", "hypothesis.json"), "w") as f:
        f.write(clean)
    print(f"\nSaved to JsonOutputs/hypothesis.json")

# if __name__ == "__main__":
#     main()