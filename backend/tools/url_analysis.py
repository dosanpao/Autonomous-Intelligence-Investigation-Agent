import os
import requests
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv
import json

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# Scrape raw page data
# -----------------------------
def scrape_url(url: str) -> dict:
    """Fetches and parses a URL, extracting all useful surface data."""
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        def get_meta(*keys):
            for key in keys:
                tag = soup.find("meta", attrs={"name": key}) or \
                      soup.find("meta", attrs={"property": key}) or \
                      soup.find("meta", attrs={"itemprop": key})
                if tag and tag.get("content"):
                    return tag["content"]
            return None

        # Extract all visible text (truncated to avoid token overflow)
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        visible_text = " ".join(soup.get_text(separator=" ").split())[:6000]

        # Extract all links
        links = list(set([
            a["href"] for a in soup.find_all("a", href=True)
            if a["href"].startswith("http")
        ]))[:30]

        return {
            "status_code": response.status_code,
            "final_url": response.url,
            "title": soup.title.string.strip() if soup.title else None,
            "description": get_meta("description", "og:description", "twitter:description"),
            "og_title": get_meta("og:title", "twitter:title"),
            "og_site_name": get_meta("og:site_name"),
            "og_type": get_meta("og:type"),
            "og_image": get_meta("og:image", "twitter:image"),
            "author": get_meta("author", "article:author"),
            "keywords": get_meta("keywords"),
            "canonical": soup.find("link", rel="canonical")["href"] if soup.find("link", rel="canonical") else None,
            "visible_text": visible_text,
            "outbound_links": links,
        }

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# Gemini Analysis
# -----------------------------
def analyze_url(url: str) -> dict:
    """
    Scrapes a URL and sends the raw data to Gemini for intelligence analysis.
    Returns a structured dict.
    """
    raw = scrape_url(url)

    if "error" in raw:
        return {"error": raw["error"]}

    prompt = f"""You are SIGMA, an OSINT intelligence analyst.

You have been given scraped data from a website. Your job is to analyze it and produce a structured intelligence report about the website and its operator/purpose.

RULES:
- Only use the provided data
- Do NOT invent facts
- Use probabilistic language for inferences
- Return ONLY valid JSON (no markdown, no explanation)

=== SCRAPED DATA ===

URL: {url}
Final URL (after redirects): {raw.get("final_url")}
Status Code: {raw.get("status_code")}
Page Title: {raw.get("title")}
Meta Description: {raw.get("description")}
OG Title: {raw.get("og_title")}
OG Site Name: {raw.get("og_site_name")}
OG Type: {raw.get("og_type")}
Author: {raw.get("author")}
Keywords: {raw.get("keywords")}
Canonical URL: {raw.get("canonical")}

Visible Page Text (truncated):
{raw.get("visible_text", "")}

Outbound Links (sample):
{json.dumps(raw.get("outbound_links", []), indent=2)}

=== TASK ===
Produce a structured intelligence report about this website.

Return JSON in this exact format:

{{
  "site_overview": {{
    "name": "<site or organization name>",
    "url": "<canonical or final URL>",
    "purpose": "<what the site does in 1-2 sentences>",
    "site_type": "<e.g. 'blog', 'e-commerce', 'news outlet', 'government', 'forum', 'corporate', 'personal portfolio', etc.>",
    "primary_language": "<detected language>",
    "confidence": <float 0.0-1.0>
  }},
  "operator_profile": {{
    "likely_operator": "<person, organization, or entity running the site, or null>",
    "operator_type": "<'individual', 'organization', 'government', 'unknown'>",
    "location_clues": "<any geographic signals from content, domain, or links>",
    "contact_info": "<any emails, addresses, or contact details found, or null>",
    "confidence": <float 0.0-1.0>
  }},
  "content_analysis": {{
    "main_topics": ["<topic1>", "<topic2>"],
    "tone": "<'professional', 'casual', 'propaganda', 'academic', 'commercial', etc.>",
    "target_audience": "<who this site appears to be aimed at>",
    "notable_content": "<anything unusual, notable, or intelligence-relevant>",
    "confidence": <float 0.0-1.0>
  }},
  "technical_indicators": {{
    "redirects": <true or false>,
    "outbound_link_patterns": "<description of where the site links to>",
    "suspicious_indicators": "<anything technically suspicious, or null>",
    "confidence": <float 0.0-1.0>
  }},
  "threat_assessment": {{
    "risk_level": "<'none', 'low', 'medium', 'high'>",
    "flags": ["<any red flags, or empty list>"],
    "assessment": "<1-2 sentence overall threat/credibility assessment>"
  }},
  "intelligence_summary": "<3-4 sentence synthesis of the most actionable intelligence findings>"
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("```", 1)[0]
    raw_text = raw_text.strip()

    return json.loads(raw_text)


# -----------------------------
# Standalone test
# -----------------------------
if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    result = analyze_url(url)
    print(json.dumps(result, indent=2))
