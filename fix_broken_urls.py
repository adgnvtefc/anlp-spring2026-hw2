import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import time
import re

input_file = "verified_urls.json"
output_file = "final_urls_to_scrape.json"

def fetch_search_results(query):
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query + " site:wikipedia.org OR site:pittsburghpa.gov OR site:cmu.edu")
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        html = urllib.request.urlopen(req, timeout=5).read()
        soup = BeautifulSoup(html, 'html.parser')
        
        for a in soup.find_all('a', class_='result__url'):
            href = a.get('href', '')
            if href.startswith('//duckduckgo.com/l/?uddg='):
                real_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                return real_url
    except Exception as e:
        pass
    return None

def verify_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        return urllib.request.urlopen(req, timeout=3).getcode() == 200
    except Exception:
        return False

def search_wikipedia(query):
    try:
        keywords = " ".join([w for w in query.replace("?", "").replace("/", " ").replace("-", " ").split() if len(w) > 3])
        api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(keywords)}&utf8=&format=json"
        
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = json.loads(urllib.request.urlopen(req, timeout=5).read())
        
        if resp['query']['search']:
            title = resp['query']['search'][0]['title']
            url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
            return url
    except Exception:
        pass
    return None

def main():
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    working = data.get('working', [])
    broken = data.get('broken', [])
    
    print(f"Starting with {len(working)} working URLs and {len(broken)} broken URLs to fix.")
    
    new_working = set(working)
    
    for i, old_url in enumerate(broken):
        print(f"[{i+1}/{len(broken)}] Fixing: {old_url}")
        
        search_term = old_url.split('/')[-1]
        if not search_term or len(search_term) < 3:
            search_term = old_url.split('/')[-2]
            
        search_term = urllib.parse.unquote(search_term).replace('-', ' ').replace('_', ' ')
        print(f"  -> Generated queries: '{search_term}'")
        
        url_found = search_wikipedia(search_term + " Pittsburgh")
        
        if not url_found or not verify_url(url_found):
            time.sleep(1)
            url_found = fetch_search_results(search_term + " Pittsburgh")
            
        if url_found and verify_url(url_found):
            print(f"  -> Found replacement: {url_found}")
            new_working.add(url_found)
        else:
            print("  -> Could not find working alternative.")
            
    final_list = sorted(list(new_working))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=4)
        
    print(f"\nSaved {len(final_list)} total verified URLs to {output_file}")
    
    with open('urls_to_paste.txt', 'w', encoding='utf-8') as f:
        for url in final_list:
            f.write(f'        "{url}",\n')

if __name__ == '__main__':
    main()
