import os
import requests
import re

# Ensure the output directory exists
os.makedirs("output", exist_ok=True)

link = "https://gofile.io/d/a4eG302I"
content_id = link.rstrip('/').split("/")[-1]

# 1. Fetch Gofile website script to dynamically find the token
try:
    main_page = requests.get("https://gofile.io").text
    token_match = re.search(r"x-website-token\s*=\s*[\"']([^\"']+)[\"']", main_page)
    wt_token = token_match.group(1) if token_match else "4fd6sg89d7s6"
except:
    wt_token = "4fd6sg89d7s6"

# 2. Setup proper headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Origin": "https://gofile.io",
    "Referer": "https://gofile.io",
    "x-website-token": wt_token
}

# 3. Call Gofile Content API
api_url = f"https://gofile.io{content_id}"
res = requests.get(api_url, headers=headers).json()

if res.get("status") == "ok":
    # Drill down to find file data inside folders or solo items
    contents_data = res.get("data", {})
    children = contents_data.get("children", {})
    
    if children:
        # Pull the first available file inside the folder link
        first_child_id = list(children.keys())[0]
        file_data = children[first_child_id]
    else:
        file_data = contents_data

    direct_link = file_data.get("link") or file_data.get("directLink")
    file_name = file_data.get("name", "downloaded_file")

    if direct_link:
        print(f"Downloading: {file_name}")
        # Save file directly inside the output folder
        save_path = os.path.join("output", file_name)
        with requests.get(direct_link, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Download complete!")
    else:
        print("Could not find a direct download URL in the API data.")
else:
    print(f"Gofile API Error: {res}")
