import os
import json
from data_pipeline.scraper import fetch_html
from data_pipeline.parser import parse_html_to_text
from data_pipeline.chunker import chunk_text
import time

OUTPUT_DB = "data/knowledge_base.jsonl"

def append_to_db(chunk_record):
    with open(OUTPUT_DB, 'a', encoding='utf-8') as f:
        f.write(json.dumps(chunk_record, ensure_ascii=False) + '\n')

def main():
    urls = [
        # CMU People & Culture
        "https://en.wikipedia.org/wiki/Andy_Warhol",
        "https://en.wikipedia.org/wiki/Randy_Pausch",
        "https://en.wikipedia.org/wiki/Randy_Pausch_Last_Lecture",
        "https://en.wikipedia.org/wiki/Scott_Fahlman",
        "https://en.wikipedia.org/wiki/Zachary_Quinto",
        "https://en.wikipedia.org/wiki/Andy_Bechtolsheim",
        "https://en.wikipedia.org/wiki/James_Gosling", # Java/Sun Micro
        "https://en.wikipedia.org/wiki/Ivan_Sutherland", # VR pioneer
        "https://en.wikipedia.org/wiki/Arthur_Mellon",
        "https://en.wikipedia.org/wiki/Carnegie_Mellon_University_College_of_Fine_Arts",
        
        # CMU Projects / Robotics
        "https://en.wikipedia.org/wiki/Alice_(software)",
        "https://en.wikipedia.org/wiki/Deep_Thought_(chess_computer)",
        "https://en.wikipedia.org/wiki/Libratus",
        "https://en.wikipedia.org/wiki/NavLab",
        "https://en.wikipedia.org/wiki/DARPA_Grand_Challenge#2007_Urban_Challenge",
        "https://en.wikipedia.org/wiki/Andrew_File_System",
        "https://en.wikipedia.org/wiki/Plaid_Parliament_of_Pwning",
        
        # CMU Life
        "https://en.wikipedia.org/wiki/The_Tartans",
        "https://en.wikipedia.org/wiki/Buggy_(Carnegie_Mellon_University)",
        "https://en.wikipedia.org/wiki/The_Tartan_(Carnegie_Mellon_University)",
        
        # Pittsburgh Restaurants, Food & Festivals
        "https://en.wikipedia.org/wiki/Primanti_Brothers",
        "https://en.wikipedia.org/wiki/Pamela%27s_Diner",
        "https://en.wikipedia.org/wiki/Picklesburgh",
        "https://en.wikipedia.org/wiki/Little_Italy_Days",
        "https://en.wikipedia.org/wiki/Strip_District,_Pittsburgh",
        "https://en.wikipedia.org/wiki/Market_Square_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Wholey%27s",
        "https://en.wikipedia.org/wiki/Station_Square",
        
        # Pittsburgh Places & Architecture
        "https://en.wikipedia.org/wiki/Cathedral_of_Learning",
        "https://en.wikipedia.org/wiki/Point_State_Park",
        "https://en.wikipedia.org/wiki/Phipps_Conservatory_and_Botanical_Gardens",
        "https://en.wikipedia.org/wiki/Carnegie_Science_Center",
        "https://en.wikipedia.org/wiki/Pittsburgh_Zoo_%26_Aquarium",
        "https://en.wikipedia.org/wiki/Duquesne_Incline",
        "https://en.wikipedia.org/wiki/Monongahela_Incline",
        "https://en.wikipedia.org/wiki/Allegheny_County_Courthouse",
        "https://en.wikipedia.org/wiki/Roberto_Clemente_Bridge",
        "https://en.wikipedia.org/wiki/Smithfield_Street_Bridge",
        "https://en.wikipedia.org/wiki/Golden_Triangle_(Pittsburgh)",
        
        # Pittsburgh History & Sports
        "https://en.wikipedia.org/wiki/History_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Pittsburgh_Renaissance",
        "https://en.wikipedia.org/wiki/Great_Fire_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Homestead_strike",
        "https://en.wikipedia.org/wiki/Fort_Pitt_Blockhouse",
        "https://en.wikipedia.org/wiki/Alcoa", # Aluminum products
        "https://en.wikipedia.org/wiki/Heinz", # Founded 1869 in Sharpsburg
        "https://en.wikipedia.org/wiki/Acrisure_Stadium", # Steelers
        "https://en.wikipedia.org/wiki/Pittsburgh_Steelers",
        "https://en.wikipedia.org/wiki/1979_Pittsburgh_Steelers_season",
        "https://en.wikipedia.org/wiki/1979_Pittsburgh_Pirates_season"  # "We Are Family" championship
    ]

    print(f"Beggining scraping for {len(urls)} URLs...")
    added_chunks = 0
    
    for url in urls:
        print(f"Scraping: {url}")
        try:
            html = fetch_html(url)
            text = parse_html_to_text(html)
            chunks = chunk_text(text, chunk_size=200, overlap=50)
            
            source_name = url.split("/")[-1]
            
            for i, chunk in enumerate(chunks):
                record = {
                    "id": f"{source_name}_chunk_{i}",
                    "source": url,
                    "text": chunk
                }
                append_to_db(record)
                added_chunks += 1
                
            time.sleep(1.0)
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            
    print(f"\n--- Scraping Complete ---")
    print(f"Successfully added {added_chunks} new chunks to the database.")

if __name__ == "__main__":
    main()
