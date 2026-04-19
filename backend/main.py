from flask import Flask, request, jsonify, send_from_directory, Response
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.recon import run_recon
from agents.hypothesis import run_hypothesis_agent, format_recon_for_prompt
from agents.brief import run_brief_agent

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

@app.route("/ping")
def ping():
    return {"message": "SIGMA backend running 🚀"}

# ----------------------------
# Main Investigate Endpoint
# ----------------------------
@app.route("/investigate", methods=["POST"])
def investigate():
    text = request.form.get("text", "").strip()

    def generate():
        # STEP 1 - RECON
        yield f"data: {json.dumps({'agent': 'RECON', 'message': 'Scanning platforms...'})}\n\n"
        recon = run_recon(text)

        os.makedirs(os.path.join(os.path.dirname(__file__), "agents/JsonOutputs"), exist_ok=True)
        with open("backend/agents/JsonOutputs/recon.json", "w") as f:
            json.dump(recon, f, indent=2)

        found = len(recon.get("accounts_found", []))
        yield f"data: {json.dumps({'agent': 'RECON', 'message': f'Found {found} platform(s). Building profile...'})}\n\n"

        # STEP 2 - HYPOTHESIS
        yield f"data: {json.dumps({'agent': 'HYPOTHESIS', 'message': 'Analyzing patterns and generating theories...'})}\n\n"
        hypothesis_raw = run_hypothesis_agent({**recon, "username": text})

        clean = hypothesis_raw.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1]
        if clean.endswith("```"):
            clean = clean.rsplit("```", 1)[0]
        clean = clean.strip()

        with open("backend/agents/JsonOutputs/hypothesis.json", "w") as f:
            f.write(clean)

        hypothesis = json.loads(clean)
        yield f"data: {json.dumps({'agent': 'HYPOTHESIS', 'message': 'Hypotheses generated. Writing brief...'})}\n\n"

        # STEP 3 - BRIEF
        yield f"data: {json.dumps({'agent': 'BRIEF', 'message': 'Compiling intelligence dossier...'})}\n\n"
        brief_raw = run_brief_agent(hypothesis)

        clean_brief = brief_raw.strip()
        if clean_brief.startswith("```"):
            clean_brief = clean_brief.split("\n", 1)[1]
        if clean_brief.endswith("```"):
            clean_brief = clean_brief.rsplit("```", 1)[0]
        clean_brief = clean_brief.strip()

        with open("backend/agents/JsonOutputs/brief.json", "w") as f:
            f.write(clean_brief)

        brief = json.loads(clean_brief)
        yield f"data: {json.dumps({'agent': 'COMPLETE', 'message': 'Report ready.', 'report': brief})}\n\n"

    return Response(generate(), mimetype="text/event-stream")

# ----------------------------
# Run Server
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)