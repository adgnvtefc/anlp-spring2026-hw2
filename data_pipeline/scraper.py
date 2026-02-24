import requests
import os

def fetch_html(url: str) -> str:
    """Fetches the raw HTML content from a given URL."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

def download_pdf(url: str, save_path: str):
    """Downloads a PDF from a URL to the local file system."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True, timeout=10)
    response.raise_for_status()
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_path

if __name__ == "__main__":
    pass
