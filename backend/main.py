from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# ----------------------------
# Serve Frontend
# ----------------------------

FRONTEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

@app.route("/")
def index():
    return send_from_directory(FRONTEND_PATH, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_PATH, path)


# ----------------------------
# Test Route (sanity check)
# ----------------------------

@app.route("/ping")
def ping():
    return {"message": "SIGMA backend running 🚀"}


# ----------------------------
# Main Investigate Endpoint
# ----------------------------

@app.route("/investigate", methods=["POST"])
def investigate():
    text = request.form.get("text")
    image = request.files.get("image")

    print("\n=== NEW REQUEST ===")
    print("Text:", text)
    print("Image:", image.filename if image else "None")

    # ----------------------------
    # Placeholder "agent" logic
    # ----------------------------

    recon_result = {
        "accounts_found": [],
        "image_observations": None,
        "metadata": {}
    }

    if text:
        recon_result["accounts_found"].append(f"example.com/{text}")

    if image:
        recon_result["image_observations"] = "Image received. (analysis not implemented yet)"

    hypothesis_result = {
        "hypotheses": [
            {
                "claim": "Test hypothesis — system is working",
                "confidence": 0.99,
                "evidence": ["Backend received input successfully"]
            }
        ]
    }

    brief = {
        "subject": text if text else "Unknown",
        "summary": "This is a test intelligence report.",
        "recon": recon_result,
        "analysis": hypothesis_result,
        "status": "complete"
    }

    return jsonify(brief)


# ----------------------------
# Run Server
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)