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
# Gemini Client (NEW SDK)
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

Image Analysis:
{json.dumps(recon.get("image_analysis"), indent=2)}

Metadata:
{json.dumps(recon.get("metadata"), indent=2)}

=== TASK ===
Generate structured intelligence hypotheses:

Return JSON in this format:

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
# Main
# -----------------------------
def main():
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("Missing GEMINI_API_KEY environment variable")

    recon = load_recon(RECON_PATH)
    hypothesis = run_hypothesis_agent(recon)

    print("\n================ SIGMA HYPOTHESIS ================\n")
    print(hypothesis)
    print("\n==================================================\n")

    # save to file for brief agent
    os.makedirs(os.path.join(BASE_DIR, "JsonOutputs"), exist_ok=True)
    output_path = os.path.join(BASE_DIR, "JsonOutputs", "hypothesis.json")
    with open(output_path, "w") as f:
        f.write(hypothesis)

    print(f"Saved to {output_path}")

# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    main()


# python3 -m backend.agents.hypothesis