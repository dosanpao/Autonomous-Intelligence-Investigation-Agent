import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_wmn_data(path="data/whatsmyname.json"):
    with open(path, "r") as f:
        return json.load(f)

def check_site(site, username):
    url = site["uri_check"].format(account=username)
    try:
        response = requests.get(url, timeout=5)
        status_match = response.status_code == site.get("e_code", 200)
        string_match = site.get("e_string", "") in response.text
        if status_match and string_match:
            return {
                "platform": site["name"],
                "url": url,
                "category": site.get("cat", "unknown")
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
                print(result)  # live feedback as hits come in

    return results

if __name__ == "__main__":
    data = load_wmn_data()
    hits = check_username("dosanpao", data)


# run python3 -m backend.tools.username_lookup to test