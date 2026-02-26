import requests
import re

with open("data_pipeline/scrape_websites.py", "r") as f:
    content = f.read()

# Extract urls list
urls_text = re.search(r'urls = \[(.*?)\]', content, re.DOTALL)
if urls_text:
    urls_str = urls_text.group(1)
    urls = re.findall(r'"(https?://.*?)"', urls_str)
    
    broken = []
    print("Checking links...")
    for url in urls:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
            if r.status_code >= 400:
                print(f"BROKEN ({r.status_code}): {url}")
                broken.append(url)
        except Exception as e:
            print(f"ERROR for {url}: {e}")
            broken.append(url)
            
    print(f"Found {len(broken)} broken links:")
    for b in broken:
        print(b)
