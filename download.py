import os
import requests
import re

# Set up the main output folder
os.makedirs("output", exist_ok=True)

# Your explicit Gofile link details
CONTENT_ID = "a4eG302I"

# 1. Fetch Gofile website script to dynamically find the required security token
try:
    main_page = requests.get("https://gofile.io").text
    token_match = re.search(r"x-website-token\s*=\s*[\"']([^\"']+)[\"']", main_page)
    wt_token = token_match.group(1) if token_match else "4fd6sg89d7s6"
except:
    wt_token = "4fd6sg89d7s6"

# 2. Setup proper browser-mimicking headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Origin": "https://gofile.io",
    "Referer": "https://gofile.io/",
    "x-website-token": wt_token
}

def download_file(direct_link, file_name, folder_path):
    """Downloads a single file into a specified subfolder directory."""
    save_path = os.path.join(folder_path, file_name)
    print(f"--> Downloading file: {file_name}")
    try:
        with requests.get(direct_link, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except Exception as e:
        print(f"Failed to download {file_name}: {e}")

def process_gofile_id(current_id, relative_path=""):
    """Recursively crawls folders and processes contents."""
    api_url = f"https://gofile.io{current_id}"
    res = requests.get(api_url, headers=headers).json()
    
    if res.get("status") != "ok":
        print(f"Gofile API Error for ID {current_id}: {res}")
        return

    contents_data = res.get("data", {})
    children = contents_data.get("children", {})
    
    if not children:
        print(f"No contents found inside ID: {current_id}")
        return

    # Loop through items inside the current folder level
    for child_id, child_info in children.items():
        item_name = child_info.get("name", "unknown_item")
        item_type = child_info.get("type")
        
        # Clean folder names to avoid system path breaking characters
        safe_name = "".join(c for c in item_name if c.isalnum() or c in (' ', '_', '-')).strip()
        current_target_dir = os.path.join("output", relative_path, safe_name)

        if item_type == "folder":
            print(f"\n[Found Folder] Navigating into: {item_name}")
            os.makedirs(current_target_dir, exist_ok=True)
            # Recursively explore inside this subfolder level
            process_gofile_id(child_id, os.path.join(relative_path, safe_name))
            
        elif item_type == "file":
            direct_link = child_info.get("link") or child_info.get("directLink")
            if direct_link:
                # Ensure the containing folder path exists
                parent_folder = os.path.join("output", relative_path)
                os.makedirs(parent_folder, exist_ok=True)
                download_file(direct_link, item_name, parent_folder)
            else:
                print(f"No direct download URL found for file: {item_name}")

# Run the complete dynamic directory scan loop
print("Starting deep recursive contents scan for Gofile folder ID...")
process_gofile_id(CONTENT_ID)
print("\nAll scanning and downloading finished successfully!")
