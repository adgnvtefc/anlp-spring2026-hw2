import json

with open("link_mapping.json", "r") as f:
    mapping = json.load(f)

with open("data_pipeline/scrape_websites.py", "r") as f:
    content = f.read()

for bad_url, good_url in mapping.items():
    content = content.replace(f'"{bad_url}"', f'"{good_url}"')

with open("data_pipeline/scrape_websites.py", "w") as f:
    f.write(content)

print("Applied mapping successfully.")
