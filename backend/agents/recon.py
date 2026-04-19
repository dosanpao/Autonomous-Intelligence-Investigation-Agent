import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from backend.tools.username_lookup import load_wmn_data, check_username
from backend.tools.image_analysis import analyze_image

def run_recon(username: str, image_input=None) -> dict:
    # --- Image-only mode ---
    # If an image is provided but no username, skip platform lookup entirely
    image_only = image_input and not username.strip()

    accounts_found = []
    if not image_only:
        wmn_data = load_wmn_data()
        accounts_found = check_username(username, wmn_data)

    # --- Image analysis ---
    image_analysis = None
    if image_input:
        try:
            image_analysis = analyze_image(image_input)
        except Exception as e:
            image_analysis = {"error": str(e)}

    report = {
        "username": username,
        "accounts_found": accounts_found,
        "similar_usernames": [],
        "name_inference": None,
        "image_analysis": image_analysis,
        "metadata": {
            "posting_times": [],
            "languages_detected": []
        }
    }

    return report

# if __name__ == "__main__":
#     import json
#     result = run_recon("I_Say_a_wut")

#     os.makedirs("backend/agents/JsonOutputs", exist_ok=True)
#     with open("backend/agents/JsonOutputs/recon.json", "w") as f:
#         json.dump(result, f, indent=2)

#     print(json.dumps(result, indent=2))
#     print("\nSaved to backend/agents/JsonOutputs/recon.json")

# test with python3 -m backend.agents.recon