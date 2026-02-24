from scraper import fetch_html
from parser import parse_html_to_text
from chunker import chunk_text

def test():
    print("--- Testing Data Pipeline ---")
    url = "https://en.wikipedia.org/wiki/Pittsburgh"
    print(f"1. Fetching Wikipedia page for {url}...")
    html = fetch_html(url)
    print(f"   Fetched {len(html)} characters of HTML.")
    
    print("2. Parsing HTML to text...")
    text = parse_html_to_text(html)
    print(f"   Parsed {len(text)} characters of text.")
    print(f"   Preview: {text[:150]}...\n")
    
    print("3. Chunking text...")
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    print(f"   Created {len(chunks)} chunks.")
    if chunks:
        print(f"   Preview of first chunk: {chunks[0]}...\n")
        print(f"   Preview of second chunk: {chunks[1]}...\n")
        
    print("--- Pipeline Test Complete ---")

if __name__ == "__main__":
    test()
