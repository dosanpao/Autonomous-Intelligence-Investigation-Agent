# SIGMA — Strategic Intelligence & Graph Metadata Analyzer

---

## What is this?

SIGMA is an autonomous AI spy agent that takes a single clue (a username, image, or URL) and produces a full intelligence report — automatically. No manual Googling, no copy-pasting between tabs. The AI investigates, reasons, and writes the dossier on its own.

**One-line pitch:**
> Give SIGMA a username. It comes back with a classified intel brief.

---

## How it works (the simple version)

```
User input → Recon Agent → Hypothesis Agent → Brief Generator → Intel Report UI
```

There are three sequential AI calls, each powered by the Gemini API. The user sees a live "agent activity" feed as each step runs, then gets a final styled report at the end.

---

## Tech Stack

| Layer | Tool |
|---|---|
| AI model | Gemini 1.5 Flash (speed) + Gemini 1.5 Pro (final report) |
| Image analysis | Gemini Vision (built into the same API) |
| Backend | Python — Flask or FastAPI |
| Streaming | Server-Sent Events (SSE) so the UI updates live |
| Frontend | Plain HTML/CSS/JS styled like a spy terminal |
| Username lookup | `whatsmyname` dataset (free, open source, on GitHub) |

---

## The Three Agents

### 1. Recon Agent
**What it does:** Collects raw intelligence from the input.

- If given a **username** → checks it against known platforms using the `whatsmyname` dataset
- If given an **image** → sends it to Gemini Vision and extracts scene details, location clues, device hints, lighting/time-of-day
- If given a **URL** → scrapes visible text and metadata

---

### 2. Hypothesis Agent
**What it does:** Reasons over the recon findings and generates structured theories.

- Takes all recon output as context
- Uses Gemini's long-context window to think across everything at once
- Produces a list of hypotheses, each with a confidence score

---

### 3. Brief Generator
**What it does:** Takes everything and produces the final intel report.

- Third Gemini call with a strict output template
- Formats everything into sections: Subject Profile, Behavioral Analysis, Location Estimate, Digital Footprint, Confidence Metrics
- Styled to look like a classified document in the UI

---

## Enhanced Recon Features


### 1. Similar username detection

---

### 2. Niche platform discovery

---

### 3. Name inference from username
Use the username pattern combined with any bio text found on discovered profiles to infer a likely real name. 

---

### 4. Behavioral fingerprinting *(stretch goal)*

---

## Project File Structure

```
sigma/
├── backend/
│   ├── main.py              # Flask/FastAPI app, SSE endpoint
│   ├── agents/
│   │   ├── recon.py         # Recon agent — Gemini call #1
│   │   ├── hypothesis.py    # Hypothesis agent — Gemini call #2
│   │   └── brief.py         # Brief generator — Gemini call #3
│   └── tools/
│       ├── username_lookup.py   # Exact match via whatsmyname dataset
│       ├── similar_username.py  # Variant generation + fuzzy scoring (rapidfuzz)
│       ├── name_inference.py    # Infers real name from username + bio text
│       └── image_analysis.py    # Wraps Gemini Vision
├── frontend/
│   ├── index.html           # Input form + live dashboard
│   ├── report.html          # Final styled dossier view
│   └── style.css            # Spy terminal aesthetic
├── data/
│   └── whatsmyname.json     # Username platform dataset (downloaded from GitHub)
├── .env                     # GEMINI_API_KEY goes here
└── README.md                # This file
```

---

## Getting Started

### 1. Clone and install

```bash
git clone <your-repo>
cd sigma
pip install flask google-generativeai python-dotenv requests rapidfuzz
```

### 2. Get your Gemini API key

Go to [aistudio.google.com](https://aistudio.google.com) → Get API Key → copy it.

Create a `.env` file:
```
GEMINI_API_KEY=your_key_here
```

### 3. Download the whatsmyname dataset

```bash
curl -o data/whatsmyname.json \
  https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json
```

### 4. Run it

```bash
python backend/main.py
# Open http://localhost:5000
```

---

## Our Plan

### Get it working
- [ ] Set up Flask backend with SSE endpoint
- [ ] Wire up all three Gemini calls end-to-end
- [ ] Get exact username lookup working with whatsmyname dataset
- [ ] Get similar username detection working (variant generation + rapidfuzz scoring)
- [ ] Get image analysis working (Gemini Vision)
- [ ] Verify JSON output from each agent is structured correctly

### Make it look good + go deeper
- [ ] Build the live streaming dashboard UI
- [ ] Style the final report like a classified document
- [ ] Add confidence meters / visual indicators
- [ ] Add niche platform discovery (just expand whatsmyname iteration)
- [ ] Add name inference from username + bio text
- [ ] Polish the input form
- [ ] Rehearse the demo with a good example username + image
- [ ] Behavioral fingerprinting if time allows
