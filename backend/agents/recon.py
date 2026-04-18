import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from backend.tools.username_lookup import load_wmn_data, check_username

def run_recon(username: str) -> dict:
    wmn_data = load_wmn_data()
    accounts_found = check_username(username, wmn_data)

    report = {
        "accounts_found": accounts_found,
        "image_observations": None,
        "metadata": {
            "posting_times": [],
            "languages_detected": []
        }
    }

    return report

if __name__ == "__main__":
    import json
    result = run_recon("I_Say_a_wut")
    
    # save to file for hypothesis agent
    os.makedirs("backend/agents/JsonOutputs", exist_ok=True)
    with open("backend/agents/JsonOutputs/recon.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    print("\nSaved to backend/agents/JsonOutputs/recon.json")

# test with python3 -m backend.agents.recon