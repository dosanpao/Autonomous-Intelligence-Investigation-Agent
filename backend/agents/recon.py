import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from backend.tools.username_lookup import load_wmn_data, check_username
from backend.tools.image_analysis import analyze_image
from backend.tools.url_analysis import analyze_url

def detect_mode(text: str, image_input=None) -> str:
    """
    Determines investigation mode based on inputs.
    Returns: 'image', 'url', or 'username'
    """
    if image_input and not text.strip():
        return "image"
    if text.strip().startswith("http://") or text.strip().startswith("https://"):
        return "url"
    return "username"

def run_recon(text: str, image_input=None) -> dict:
    mode = detect_mode(text, image_input)

    report = {
        "mode": mode,
        "username": text,
        "accounts_found": [],
        "similar_usernames": [],
        "name_inference": None,
        "image_analysis": None,
        "url_analysis": None,
        "metadata": {
            "posting_times": [],
            "languages_detected": []
        }
    }

    if mode == "username":
        wmn_data = load_wmn_data()
        report["accounts_found"] = check_username(text, wmn_data)

    elif mode == "image":
        try:
            report["image_analysis"] = analyze_image(image_input)
        except Exception as e:
            report["image_analysis"] = {"error": str(e)}

    elif mode == "url":
        try:
            report["url_analysis"] = analyze_url(text)
        except Exception as e:
            report["url_analysis"] = {"error": str(e)}

        # Also run image analysis if an image was attached alongside the URL
        if image_input:
            try:
                report["image_analysis"] = analyze_image(image_input)
            except Exception as e:
                report["image_analysis"] = {"error": str(e)}

    return report

# if __name__ == "__main__":
#     import json
#     result = run_recon("https://example.com")
#     print(json.dumps(result, indent=2))

# test with python3 -m backend.agents.recon