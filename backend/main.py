from flask import Flask, request, send_from_directory, Response
import os
import json
import sys
import tempfile

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.recon import run_recon
from agents.hypothesis import run_hypothesis_agent
from agents.brief import run_brief_agent

app = Flask(__name__)

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
FRONTEND_PATH = os.path.abspath(os.path.join(BASE_DIR, "../frontend"))
JSON_DIR      = os.path.join(BASE_DIR, "agents", "JsonOutputs")

# ----------------------------
# Serve Frontend
# ----------------------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_PATH, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_PATH, path)

@app.route("/ping")
def ping():
    return {"message": "SIGMA backend running 🚀"}

# ----------------------------
# Main Investigate Endpoint
# ----------------------------
@app.route("/investigate", methods=["POST"])
def investigate():
    text = request.form.get("text", "").strip()

    image_path = None
    image_file = request.files.get("image")
    if image_file and image_file.filename:
        suffix = os.path.splitext(image_file.filename)[1] or ".jpg"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        image_file.save(tmp.name)
        image_path = tmp.name

    # Detect mode
    if image_path and not text:
        mode = "image"
    elif text.startswith("http://") or text.startswith("https://"):
        mode = "url"
    else:
        mode = "username"

    def generate():
        try:
            os.makedirs(JSON_DIR, exist_ok=True)

            # STEP 1 - RECON
            yield f"data: {json.dumps({'agent': 'AGENT RECON', 'message': 'Initializing target acquisition...'})}\n\n"
            yield f"data: {json.dumps({'agent': 'AGENT RECON', 'message': 'Scanning global platform database...'})}\n\n"
            recon = run_recon(text, image_input=image_path)

            with open(os.path.join(JSON_DIR, "recon.json"), "w") as f:
                json.dump(recon, f, indent=2)

            if mode == "image":
                img_ok = recon.get("image_analysis") and "error" not in recon["image_analysis"]
                status = "Image analyzed. Generating intelligence report..." if img_ok else "Image analysis failed."
            elif mode == "url":
                url_ok = recon.get("url_analysis") and "error" not in recon["url_analysis"]
                status = "URL analyzed. Building intelligence profile..." if url_ok else "URL analysis failed."
            else:
                found  = len(recon.get("accounts_found", []))
                status = f"Platform sweep complete — {found} account(s) identified."

            yield f"data: {json.dumps({'agent': 'AGENT RECON', 'message': status})}\n\n"
            yield f"data: {json.dumps({'agent': 'AGENT RECON', 'message': 'Extracting profile metadata and digital artifacts...'})}\n\n"
            yield f"data: {json.dumps({'agent': 'AGENT RECON', 'message': 'Recon package sealed. Passing to hypothesis engine.'})}\n\n"

            # STEP 2 - HYPOTHESIS
            yield f"data: {json.dumps({'agent': 'AGENT HYPOTHESIS', 'message': 'Receiving intelligence package...'})}\n\n"
            yield f"data: {json.dumps({'agent': 'AGENT HYPOTHESIS', 'message': 'Cross-referencing platform data for behavioral patterns...'})}\n\n"
            yield f"data: {json.dumps({'agent': 'AGENT HYPOTHESIS', 'message': 'Running probabilistic identity analysis...'})}\n\n"
            hypothesis_raw = run_hypothesis_agent({**recon, "username": text})

            clean = hypothesis_raw.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1]
            if clean.endswith("```"):
                clean = clean.rsplit("```", 1)[0]
            clean = clean.strip()

            with open(os.path.join(JSON_DIR, "hypothesis.json"), "w") as f:
                f.write(clean)

            hypothesis = json.loads(clean)
            yield f"data: {json.dumps({'agent': 'AGENT HYPOTHESIS', 'message': 'Confidence scores calculated. Hypotheses locked in.'})}\n\n"
            yield f"data: {json.dumps({'agent': 'AGENT HYPOTHESIS', 'message': 'Forwarding intelligence package to brief writer...'})}\n\n"

            # STEP 3 - BRIEF
            yield f"data: {json.dumps({'agent': 'AGENT BRIEF', 'message': 'Receiving hypothesis package...'})}\n\n"
            yield f"data: {json.dumps({'agent': 'AGENT BRIEF', 'message': 'Structuring classified intelligence dossier...'})}\n\n"
            yield f"data: {json.dumps({'agent': 'AGENT BRIEF', 'message': 'Applying redaction protocols and confidence metrics...'})}\n\n"
            brief_raw = run_brief_agent(hypothesis)

            clean_brief = brief_raw.strip()
            if clean_brief.startswith("```"):
                clean_brief = clean_brief.split("\n", 1)[1]
            if clean_brief.endswith("```"):
                clean_brief = clean_brief.rsplit("```", 1)[0]
            clean_brief = clean_brief.strip()

            with open(os.path.join(JSON_DIR, "brief.json"), "w") as f:
                f.write(clean_brief)

            brief = json.loads(clean_brief)
            yield f"data: {json.dumps({'agent': 'AGENT BRIEF', 'message': 'Dossier compiled. Classification stamp applied.'})}\n\n"
            yield f"data: {json.dumps({'agent': 'COMPLETE', 'message': 'Intel report ready.', 'report': brief})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'agent': 'ERROR', 'message': str(e)})}\n\n"

        finally:
            if image_path and os.path.exists(image_path):
                os.unlink(image_path)

    return Response(generate(), mimetype="text/event-stream")

# ----------------------------
# Run Server
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)