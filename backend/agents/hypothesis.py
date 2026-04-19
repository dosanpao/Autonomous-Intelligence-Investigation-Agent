import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECON_PATH = os.path.join(BASE_DIR, "JsonOutputs", "recon.json")

# -----------------------------
# Gemini Client
# -----------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# Load Recon Data
# -----------------------------
def load_recon(path):
    with open(path, "r") as f:
        return json.load(f)

# -----------------------------
# Format Prompt
# -----------------------------
def format_recon_for_prompt(recon):
    image_section = ""
    image_data = recon.get("image_analysis")
    if image_data and "error" not in image_data:
        image_section = f"""
Image Analysis:
  Location Clues:    {json.dumps(image_data.get("location_clues"), indent=4)}
  Time Clues:        {json.dumps(image_data.get("time_clues"), indent=4)}
  Subject Clues:     {json.dumps(image_data.get("subject_clues"), indent=4)}
  Device Clues:      {json.dumps(image_data.get("device_and_metadata_clues"), indent=4)}
  Visual Summary:    {image_data.get("visual_description", "")}
  Intel Summary:     {image_data.get("intelligence_summary", "")}
"""
    else:
        image_section = "Image Analysis: None provided."

    return f"""
You are SIGMA, an OSINT intelligence hypothesis engine.

You are analyzing structured reconnaissance data about a digital identity.

RULES:
- Only use provided evidence
- Do NOT invent facts
- All outputs must be probabilistic
- Return ONLY valid JSON (no markdown, no explanation)

=== RECON DATA ===

Username:
{recon.get("username")}

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
Generate structured intelligence hypotheses based on ALL available evidence above,
including image analysis if present. Location hypotheses should incorporate image
location clues when available.

Return JSON in this exact format:

{{
  "identity_hypothesis": {{
    "claim": "",
    "confidence": 0.0,
    "evidence": []
  }},
  "occupation_hypothesis": {{
    "claim": "",
    "confidence": 0.0,
    "evidence": []
  }},
  "location_hypothesis": {{
    "claim": "",
    "confidence": 0.0,
    "evidence": []
  }},
  "behavioral_analysis": {{
    "claim": "",
    "confidence": 0.0,
    "evidence": []
  }},
  "cross_platform_linking": {{
    "claim": "",
    "confidence": 0.0,
    "evidence": []
  }},
  "summary": ""
}}
"""

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
# Main (standalone test)
# -----------------------------
def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    recon = load_recon(RECON_PATH)
    hypothesis = run_hypothesis_agent(recon)

    clean = hypothesis.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1]
    if clean.endswith("```"):
        clean = clean.rsplit("```", 1)[0]
    clean = clean.strip()

    print("\n================ SIGMA HYPOTHESIS ================\n")
    print(clean)
    print("\n==================================================\n")

    os.makedirs(os.path.join(BASE_DIR, "JsonOutputs"), exist_ok=True)
    output_path = os.path.join(BASE_DIR, "JsonOutputs", "hypothesis.json")
    with open(output_path, "w") as f:
        f.write(clean)

    print(f"Saved to {output_path}")

# if __name__ == "__main__":
#     main()

# python3 -m backend.agents.hypothesis