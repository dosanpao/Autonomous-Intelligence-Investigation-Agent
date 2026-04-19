import json
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Absolute path — works regardless of where you run the server from
WMN_PATH = os.path.join(os.path.dirname(__file__), "../../data/whatsmyname.json")

def load_wmn_data(path=None):
    with open(path or WMN_PATH, "r") as f:
        return json.load(f)

def scrape_profile(url: str, username: str) -> dict:
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        def get_meta(*keys):
            for key in keys:
                tag = soup.find("meta", attrs={"name": key}) or \
                      soup.find("meta", attrs={"property": key}) or \
                      soup.find("meta", attrs={"itemprop": key})
                if tag and tag.get("content"):
                    return tag["content"]
            return None

        return {
            "display_name": get_meta("og:title", "twitter:title", "title", "name", "nickname"),
            "bio": get_meta("og:description", "twitter:description", "description"),
            "location": get_meta("location", "user:location", "geo.region"),
            "profile_image_url": get_meta("og:image", "twitter:image", "image"),
            "website": get_meta("og:url", "twitter:url"),
            "occupation": get_meta("occupation", "jobtitle", "role"),
            "followers": get_meta("followers", "user:followers"),
            "following": get_meta("following", "user:following"),
            "posts": get_meta("posts", "user:posts"),
            "extra": []
        }

    except Exception:
        return {}

def scrape_github(username: str) -> dict:
    try:
        response = requests.get(
            f"https://api.github.com/users/{username}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
        data = response.json()
        return {
            "display_name": data.get("name"),
            "bio": data.get("bio"),
            "location": data.get("location"),
            "profile_image_url": data.get("avatar_url"),
            "website": data.get("blog"),
            "occupation": data.get("company"),
            "followers": data.get("followers"),
            "following": data.get("following"),
            "posts": None,
            "extra": [
                f"public_repos: {data.get('public_repos')}",
            ]
        }
    except Exception:
        return {}

def scrape_reddit(username: str) -> dict:
    try:
        response = requests.get(
            f"https://www.reddit.com/user/{username}/about.json",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5
        )
        data = response.json().get("data", {})
        return {
            "display_name": data.get("name"),
            "bio": data.get("subreddit", {}).get("public_description"),
            "location": None,
            "profile_image_url": None,
            "website": None,
            "occupation": None,
            "followers": None,
            "following": None,
            "posts": None,
            "extra": [
                f"karma: {data.get('total_karma')}",
                f"created: {data.get('created_utc')}",
            ]
        }
    except Exception:
        return {}

def check_site(site, username):
    url = site["uri_check"].format(account=username)
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        status_match = response.status_code == site.get("e_code", 200)
        string_match = site.get("e_string", "") in response.text

        if status_match and string_match:
            if "github" in site["name"].lower():
                profile_data = scrape_github(username)
            elif "reddit" in site["name"].lower():
                profile_data = scrape_reddit(username)
            else:
                profile_data = scrape_profile(url, username)

            return {
                "platform": site["name"],
                "url": url,
                "category": site.get("cat", "unknown"),
                "profile": profile_data
            }
    except requests.RequestException:
        return None

def check_username(username: str, wmn_data: dict) -> list[dict]:
    results = []
    sites = wmn_data.get("sites", [])

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_site, site, username): site for site in sites}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                print(result)

    return results

# if __name__ == "__main__":
#     data = load_wmn_data()
#     hits = check_username("I_Say_A_Wat", data)