import os
import time
import urllib.parse
from data_pipeline.scraper import fetch_html, download_pdf

SCRAPED_DIR = "scraped_data"

def get_safe_filename(url):
    # Parse the URL to get the path and query string, replace non-alphanumeric chars
    parsed = urllib.parse.urlparse(url)
    name = parsed.netloc + parsed.path
    if parsed.query:
        name += "_" + parsed.query
    safe_name = "".join([c if c.isalnum() else "_" for c in name])
    
    if url.endswith('.pdf'):
        return safe_name + ".pdf"
    else:
        return safe_name + ".htm"

def main():
    urls = [
        # CMU People & Culture
        "https://en.wikipedia.org/wiki/Andy_Warhol",
        "https://en.wikipedia.org/wiki/Randy_Pausch",
        "https://en.wikipedia.org/wiki/The_Last_Lecture",
        "https://en.wikipedia.org/wiki/Scott_Fahlman",
        "https://en.wikipedia.org/wiki/Zachary_Quinto",
        "https://en.wikipedia.org/wiki/Andy_Bechtolsheim",
        "https://en.wikipedia.org/wiki/James_Gosling",
        "https://en.wikipedia.org/wiki/Ivan_Sutherland",
        "https://en.wikipedia.org/wiki/Richard_B._Mellon",
        "https://en.wikipedia.org/wiki/College_of_Fine_Arts_(Carnegie_Mellon_University)",
        
        # CMU Projects / Robotics
        "https://en.wikipedia.org/wiki/Alice_(software)",
        "https://en.wikipedia.org/wiki/Deep_Thought_(chess_computer)",
        "https://en.wikipedia.org/wiki/Libratus",
        "https://en.wikipedia.org/wiki/Navlab",
        "https://en.wikipedia.org/wiki/DARPA_Grand_Challenge#2007_Urban_Challenge",
        "https://en.wikipedia.org/wiki/Andrew_File_System",
        "https://pwning.net/",
        
        # CMU Life
        "https://en.wikipedia.org/wiki/The_Tartans",
        "https://en.wikipedia.org/wiki/Sweepstakes_(Carnegie_Mellon_University)",
        "https://en.wikipedia.org/wiki/The_Tartan_(Carnegie_Mellon_University)",
        
        # Pittsburgh Restaurants, Food & Festivals
        "https://en.wikipedia.org/wiki/Primanti_Brothers",
        "https://en.wikipedia.org/wiki/Pamela%27s_Diner",
        "https://en.wikipedia.org/wiki/Picklesburgh",
        "https://littleitalydays.com/",
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
        "https://en.wikipedia.org/wiki/Alcoa",
        "https://en.wikipedia.org/wiki/Heinz",
        "https://en.wikipedia.org/wiki/Acrisure_Stadium",
        "https://en.wikipedia.org/wiki/Pittsburgh_Steelers",
        "https://en.wikipedia.org/wiki/1979_Pittsburgh_Steelers_season",
        "https://en.wikipedia.org/wiki/1979_Pittsburgh_Pirates_season",
        
        # New General Info and History
        "https://en.wikipedia.org/wiki/Pittsburgh",
        "https://www.pittsburghpa.gov/Home",
        "https://www.britannica.com/place/Pittsburgh",
        "https://www.visitpittsburgh.com",
        "https://pittsburghpa.gov/finance/tax-forms",
        "https://www.pittsburghpa.gov/files/assets/city/v/4/omb/documents/operating-budgets/2025-operating-budget.pdf",
        "https://www.cmu.edu/about/",
        
        # Events
        "https://pittsburgh.events",
        "https://downtownpittsburgh.com/events/",
        "https://www.pghcitypaper.com/pittsburgh/EventSearch?v=d",
        "https://events.cmu.edu",
        "https://www.cmu.edu/engage/alumni/events/campus/index.html",
        
        # Music and Culture
        "https://www.pittsburghsymphony.org",
        "https://pittsburghopera.org",
        "https://trustarts.org",
        "https://carnegiemuseums.org",
        "https://www.heinzhistorycenter.org",
        "https://www.thefrickpittsburgh.org",
        "https://en.wikipedia.org/wiki/List_of_museums_in_Pittsburgh",
        
        # Food-related events
        "https://www.visitpittsburgh.com/events-festivals/food-festivals/",
        "https://www.picklesburgh.com/",
        "https://www.pghtacofest.com/",
        "https://pittsburghrestaurantweek.com/",
        "https://littleitalydays.com",
        "https://bananasplitfest.com",
        
        # Sports
        "https://www.visitpittsburgh.com/things-to-do/pittsburgh-sports-teams/",
        "https://www.mlb.com/pirates",
        "https://www.steelers.com",
        "https://www.nhl.com/penguins/",
        
        # -------------------------------------------------------------
        # MORE SPECIFIC DIVERSE SOURCES based on leaderboard questions
        # -------------------------------------------------------------
        
        # Restaurants & Specific Foods
        "https://eatgaucho.com/",
        "https://siennamercato.com/",
        "https://prantlsbakery.com/", # burnt almond torte
        "https://pusadeesgarden.com/",
        "https://millieshomemade.com/", # Salty caramel
        "https://morcillapittsburgh.com/",
        "https://commonplacecoffee.com/",
        "https://en.wikipedia.org/wiki/La_Prima_Espresso_Company",
        "https://dianoiaseatery.com/",
        "https://www.eaglerestaurant.com/",
        "https://chengdugourmetpa.com/",
        "https://en.wikipedia.org/wiki/Apteka", # Vegan
        "https://en.wikipedia.org/wiki/Noodlehead",
        "https://takopgh.com/",
        "https://dishosteria.com/",
        "https://fetfisk.net/", # Best fish fry? Pop up?
        "https://ironbornpizza.com/",
        "https://en.wikipedia.org/wiki/The_Vandal",
        "https://www.driftwoodoven.com/",
        "https://en.wikipedia.org/wiki/Grand_Concourse",
        "https://en.wikipedia.org/wiki/Texas_de_Brazil", # Station square brazilian
        "https://greenforestdining.com/", # Penn hills brazilian
        "https://en.wikipedia.org/wiki/Fogo_de_Chao", # Downtown brazilian
        "https://monaimeechocolat.com/",
        "https://tessaros.com/", 
        "https://jerrysrecords.com/", # Vintage vinyl records
        
        # More Specific Shopping/Places
        "https://en.wikipedia.org/wiki/Walnut_Street_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Waterworks_Mall",
        "https://culturaldistrict.org/",
        
        # Adding more coverage from visitpittsburgh where wikipedia might fail
        "https://www.visitpittsburgh.com/restaurants-bars/",
        "https://www.visitpittsburgh.com/neighborhoods/",
        "https://www.visitpittsburgh.com/things-to-do/shopping/",
        "https://www.visitpittsburgh.com/events-festivals/",
        
        # Additional Neighborhoods
        "https://en.wikipedia.org/wiki/Squirrel_Hill_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Oakland_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Lawrenceville_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Bloomfield_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/South_Side_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Shadyside_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/East_Liberty_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/North_Shore_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Mount_Washington_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Highland_Park_(Pittsburgh)",
        
        # New Verified 70 Restaurants and General Sites
        "https://en.wikipedia.org/wiki/Church_Brew_Works",
        "https://en.wikipedia.org/wiki/Primanti_Brothers",
        "https://en.wikipedia.org/wiki/Vincent%27s_Pizza_Park",
        "https://en.wikipedia.org/wiki/Eat%27n_Park",
        "https://en.wikipedia.org/wiki/Hoss%27s_Steak_and_Sea_House",
        "https://en.wikipedia.org/wiki/Mad_Mex",
        "https://en.wikipedia.org/wiki/Conflict_Kitchen",
        "https://en.wikipedia.org/wiki/City_of_Bridges",
        "https://en.wikipedia.org/wiki/List_of_bridges_in_Pittsburgh",
        "https://en.wikipedia.org/wiki/Three_Rivers_Stadium",
        "https://en.wikipedia.org/wiki/Forbes_Field",
        "https://en.wikipedia.org/wiki/PPG_Paints_Arena",
        "https://en.wikipedia.org/wiki/PNC_Park",
        "https://en.wikipedia.org/wiki/Mellon_Arena",
        "https://en.wikipedia.org/wiki/Heinz_Field",
        "https://en.wikipedia.org/wiki/Schenley_Park",
        "https://en.wikipedia.org/wiki/Frick_Park",
        "https://en.wikipedia.org/wiki/National_Aviary",
        "https://en.wikipedia.org/wiki/Children%27s_Museum_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Senator_John_Heinz_History_Center",
        "https://en.wikipedia.org/wiki/Carnegie_Museum_of_Natural_History",
        "https://en.wikipedia.org/wiki/Carnegie_Museum_of_Art",
        "https://en.wikipedia.org/wiki/Mattress_Factory",
        "https://en.wikipedia.org/wiki/Bicycle_Heaven",
        "https://en.wikipedia.org/wiki/Cathedral_of_Learning",
        "https://en.wikipedia.org/wiki/Heinz_Memorial_Chapel",
        "https://en.wikipedia.org/wiki/Stephen_Foster_Memorial",
        "https://en.wikipedia.org/wiki/Soldiers_and_Sailors_Memorial_Hall_and_Museum",
        "https://en.wikipedia.org/wiki/University_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Duquesne_University",
        "https://en.wikipedia.org/wiki/Chatham_University",
        "https://en.wikipedia.org/wiki/Carlow_University",
        "https://en.wikipedia.org/wiki/Point_Park_University",
        "https://en.wikipedia.org/wiki/Robert_Morris_University",
        "https://en.wikipedia.org/wiki/Kennywood",
        "https://en.wikipedia.org/wiki/Sandcastle_Waterpark",
        "https://en.wikipedia.org/wiki/Idlewild_and_Soak_Zone",
        "https://en.wikipedia.org/wiki/Fort_Pitt_Museum",
        "https://en.wikipedia.org/wiki/Carrie_Furnace",
        "https://en.wikipedia.org/wiki/Rivers_Casino_Pittsburgh",
        "https://en.wikipedia.org/wiki/Benedum_Center",
        "https://en.wikipedia.org/wiki/Heinz_Hall_for_the_Performing_Arts",
        "https://en.wikipedia.org/wiki/Byham_Theater",
        "https://en.wikipedia.org/wiki/O%27Reilly_Theater",
        "https://en.wikipedia.org/wiki/August_Wilson_African_American_Cultural_Center",
        "https://en.wikipedia.org/wiki/Pittsburgh_Playhouse",
        "https://en.wikipedia.org/wiki/Roberto_Clemente",
        "https://en.wikipedia.org/wiki/Mario_Lemieux",
        "https://en.wikipedia.org/wiki/Sidney_Crosby",
        "https://en.wikipedia.org/wiki/Franco_Harris",
        "https://en.wikipedia.org/wiki/Willie_Stargell",
        "https://en.wikipedia.org/wiki/Bill_Mazeroski",
        "https://en.wikipedia.org/wiki/Honus_Wagner",
        "https://en.wikipedia.org/wiki/Evgeni_Malkin",
        "https://en.wikipedia.org/wiki/Jaromir_Jagr",
        "https://en.wikipedia.org/wiki/Fred_Rogers",
        "https://en.wikipedia.org/wiki/Gene_Kelly",
        "https://en.wikipedia.org/wiki/Rachel_Carson",
        "https://en.wikipedia.org/wiki/George_Westinghouse",
        "https://en.wikipedia.org/wiki/Henry_Clay_Frick",
        "https://en.wikipedia.org/wiki/Pittsburgh_Penguins",
        "https://en.wikipedia.org/wiki/Pittsburgh_Pirates",
        "https://en.wikipedia.org/wiki/Economy_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Geography_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Mount_Washington_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Pittsburgh_Light_Rail",
        "https://en.wikipedia.org/wiki/Squirrel_Hill_Tunnel",
        "https://en.wikipedia.org/wiki/Fort_Pitt_Tunnel",
        "https://en.wikipedia.org/wiki/Liberty_Tunnels"
    ]

    print(f"Beginning scraping/caching for {len(urls)} URLs...")
    os.makedirs(SCRAPED_DIR, exist_ok=True)
    added_files = 0
    
    for url in urls:
        filename = get_safe_filename(url)
        filepath = os.path.join(SCRAPED_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"Skipping {url} (already downloaded)")
            continue
            
        print(f"Downloading: {url} -> {filename}")
        try:
            if url.endswith('.pdf'):
                download_pdf(url, filepath)
            else:
                html = fetch_html(url)
                # Save raw HTML
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
            
            added_files += 1
            time.sleep(1.0) # Polite crawling
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            
    print(f"\n--- Scraping Complete ---")
    print(f"Successfully downloaded {added_files} new files to {SCRAPED_DIR}.")

if __name__ == "__main__":
    main()
