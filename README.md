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

**Output (JSON):**
```json
{
  "accounts_found": ["github.com/...", "reddit.com/u/..."],
  "image_observations": "Urban European setting, morning light, café context",
  "metadata": { "posting_times": [...], "languages_detected": [...] }
}
```

---

### 2. Hypothesis Agent
**What it does:** Reasons over the recon findings and generates structured theories.

- Takes all recon output as context
- Uses Gemini's long-context window to think across everything at once
- Produces a list of hypotheses, each with a confidence score

**Output (JSON):**
```json
{
  "hypotheses": [
    {
      "claim": "Subject is likely located in a Western European timezone",
      "confidence": 0.74,
      "evidence": ["posting hours cluster 8am–11pm CET", "café imagery consistent with European urban environment"]
    },
    {
      "claim": "Subject works in a technical field",
      "confidence": 0.61,
      "evidence": ["GitHub account active", "language in posts includes technical terminology"]
    }
  ]
}
```

---

### 3. Brief Generator
**What it does:** Takes everything and produces the final intel report.

- Third Gemini call with a strict output template
- Formats everything into sections: Subject Profile, Behavioral Analysis, Location Estimate, Digital Footprint, Confidence Metrics
- Styled to look like a classified document in the UI

---

## Enhanced Recon Features

These are built on top of the base recon agent — implement them in order, each one is independent so you can skip any that run out of time.

### 1. Similar username detection
Instead of only checking exact username matches, generate likely variations and score them by similarity. People reuse the same handle with small tweaks across platforms.

**Variant generation patterns:**
```python
# input: "john_doe"
# generates: johndoe, john.doe, jdoe, doe_john, john_doe99, xjohndoe, realjohndoe ...

from rapidfuzz import fuzz

def similar_usernames(username):
    variants = [
        username.replace("_", ""),       # john_doe → johndoe
        username.replace("_", "."),      # john_doe → john.doe
        username.split("_")[0],          # john_doe → john
        "x" + username,                  # john_doe → xjohn_doe
        "real" + username,               # john_doe → realjohn_doe
        username + "_",                  # john_doe → john_doe_
        username + "99",                 # john_doe → john_doe99
    ]
    return variants

score = fuzz.ratio("john_doe", "johndoe")  # returns 0–100, anything 80+ is worth flagging
```

**How it surfaces in the dashboard:**
```
[RECON] Exact match:   github.com/john_doe        (100%)
[RECON] Likely alias:  reddit.com/u/johndoe        (91%)
[RECON] Possible alias: twitter.com/jdoe_          (74%)
```

Install: `pip install rapidfuzz`

---

### 2. Niche platform discovery
The whatsmyname dataset includes hundreds of platforms beyond the obvious ones — gaming sites, developer forums, art communities, regional social networks. By default, check all of them. This is free — it's just iterating over more entries in the same JSON file.

The niche hits are often more revealing than Twitter or Instagram because people are less guarded on smaller platforms. A hit on a hobby forum tells you something about the person that a Twitter account doesn't.

---

### 3. Name inference from username
Use the username pattern combined with any bio text found on discovered profiles to infer a likely real name. This stays in "public data" territory since you're only reading what's already on the profile page.

Pass both to Gemini in the hypothesis step with a specific instruction:

```python
prompt = """
Given this username and any profile bio text found across platforms,
infer the subject's likely real name if possible. Return null if there
is not enough signal. Explain your reasoning.

Username: {username}
Bio samples: {bio_texts}
"""
```

Example output:
```
[HYPOTHESIS] Username pattern 'jsmith_dev' + bio mentions 'software engineer'
             → Likely real name: J. Smith (confidence: 0.58)
```

This feeds directly into the final brief as a "Subject Identity" field.

---

### 4. Behavioral fingerprinting *(stretch goal — add this last)*
Cluster posting times, writing style, and topic patterns across platforms to build a behavioral profile. Only attempt this if the core pipeline is solid and you have time on day two.

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

## The Demo Flow 

1. User types a username (or uploads an image) into the input box
2. The dashboard streams live activity:
   ```
   [RECON]      Scanning platforms... found GitHub account
   [RECON]      Analyzing profile image... urban environment detected
   [HYPOTHESIS] Generating theories... confidence 74%
   [BRIEF]      Compiling intelligence dossier...
   [COMPLETE]   Report ready ✓
   ```
3. Final report appears — styled like a redacted classified document with confidence meters

The streaming is the magic. Even though it's three sequential API calls, the live feed makes it feel like a real autonomous system working in real time.

---

## The Wow Moment

**Use an image with location clues.** Upload any photo that has a background — a street, a café, a campus. Gemini Vision will identify contextual details (architecture style, signage language, vegetation type, lighting angle) and the hypothesis agent will turn those into intelligence findings like:

> "Subject likely photographed in Northern Europe. Photo taken in late morning based on shadow angle. Environment consistent with university campus."

This is the moment that lands with judges. Lead with it.

---

## What We're NOT Building For Now

To keep this doable in hackathon time, we cut:

| Feature from original doc | Why we cut it |
|---|---|
| Verification agent | Adds complexity; low demo value |
| Graph database (Neo4j etc.) | Store state in a simple Python dict instead |
| Multi-agent concurrency | Sequential calls work fine and are easier to debug |
| Correlation agent (identity linking) | Gemini does this well enough in the hypothesis prompt |
| Downloadable PDF report | Nice to have; add it last if time permits |

---

## Gemini API — Key Things to Know

- **Model to use:** `gemini-1.5-flash` for recon + hypothesis (fast, cheap), `gemini-1.5-pro` for the final brief (better writing)
- **Vision:** Pass images directly in the API call — no separate endpoint needed
- **Long context:** Gemini 1.5 has a 1M token context window, so dumping all recon findings into the hypothesis call is totally fine
- **Function calling:** Gemini supports tool/function calling natively — useful if you want to make the username lookup a proper tool call instead of hardcoding it

### Basic call pattern

```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

response = model.generate_content([
    "You are a recon intelligence agent. Given this username, identify likely platforms and behavioral patterns.",
    f"Username: {username}"
])

print(response.text)
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

---

## Notes

Start in `backend/agents/recon.py` — that's where the first Gemini call lives and it's the easiest to understand. Get that working before touching anything else.