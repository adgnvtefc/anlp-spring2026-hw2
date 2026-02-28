import os
import time
import urllib.parse
from data_pipeline.scraper import fetch_html, download_pdf

SCRAPED_DIR = "scraped_data"

def get_safe_filename(url):
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
        "https://acrisurestadium.com/events/",
        "https://arcadecomedytheater.com/events/",
        "https://awaacc.org/about/",
        "https://awaacc.org/events/",
        "https://carnegieart.org/",
        "https://carnegieart.org/about/",
        "https://carnegieart.org/collection/architecture/",
        "https://carnegieart.org/visit/",
        "https://carnegiemnh.org/about/",
        "https://carnegiemnh.org/explore/dinosaurs-in-their-time/",
        "https://carnegiemnh.org/explore/polar-world/",
        "https://carnegiemuseums.org/about/history/",
        "https://carnegiemuseums.org/carnegie-magazine/",
        "https://carnegiemuseums.org/events/",
        "https://carnegiesciencecenter.org/about/contact-us/",
        "https://carnegiesciencecenter.org/attractions/rangos-giant-cinema/",
        "https://carnegiesciencecenter.org/exhibits/mars-the-next-giant-leap/",
        "https://carnegiesciencecenter.org/exhibits/miniature-railroad/",
        "https://carnegiesciencecenter.org/exhibits/roboworld/",
        "https://carnegiesciencecenter.org/programs/",
        "https://carnegiesciencecenter.org/programs/21-plus-night/",
        "https://carnegiesciencecenter.org/visit/",
        "https://chucknollfoundation.org/",
        "https://clementemuseum.com/",
        "https://downtownpittsburgh.com/dining/",
        "https://en.wikipedia.org/wiki/1909_World_Series",
        "https://en.wikipedia.org/wiki/1947_Pittsburgh_Steelers_season",
        "https://en.wikipedia.org/wiki/1976_Pittsburgh_Panthers_football_team",
        "https://en.wikipedia.org/wiki/2013_Pittsburgh_Pirates_season",
        "https://en.wikipedia.org/wiki/2015%E2%80%9316_Pittsburgh_Penguins_season",
        "https://en.wikipedia.org/wiki/2025_Pittsburgh_Pirates_season",
        "https://en.wikipedia.org/wiki/2026_NFL_draft",
        "https://en.wikipedia.org/wiki/Acrisure_Stadium",
        "https://en.wikipedia.org/wiki/Allegheny_County,_Pennsylvania",
        "https://en.wikipedia.org/wiki/Allegheny_Portage_Railroad",
        "https://en.wikipedia.org/wiki/American_Jewish_Museum",
        "https://en.wikipedia.org/wiki/Art_Rooney",
        "https://en.wikipedia.org/wiki/Benedum_Center",
        "https://en.wikipedia.org/wiki/Bill_Cowher",
        "https://en.wikipedia.org/wiki/Boulevard_of_the_Allies",
        "https://en.wikipedia.org/wiki/Bridges_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Buhl_Planetarium_and_Institute_of_Popular_Science",
        "https://en.wikipedia.org/wiki/Carnegie_Mellon_School_of_Computer_Science",
        "https://en.wikipedia.org/wiki/Carnegie_Mellon_University",
        "https://en.wikipedia.org/wiki/Carnegie_Mellon_University_traditions",
        "https://en.wikipedia.org/wiki/Carnegie_Museums_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Cathedral_of_Learning",
        "https://en.wikipedia.org/wiki/Charles_Harris_%28photographer%29",
        "https://en.wikipedia.org/wiki/Chuck_Noll",
        "https://en.wikipedia.org/wiki/David_Creswell",
        "https://en.wikipedia.org/wiki/Duquesne_Incline",
        "https://en.wikipedia.org/wiki/Ed_Gainey",
        "https://en.wikipedia.org/wiki/Exposition_Park_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/Forbes_Field",
        "https://en.wikipedia.org/wiki/Fort_Pitt_(Pennsylvania)",
        "https://en.wikipedia.org/wiki/Frick_Park",
        "https://en.wikipedia.org/wiki/Great_Fire_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Greg_Brown_(sportscaster)",
        "https://en.wikipedia.org/wiki/Heinz_History_Center",
        "https://en.wikipedia.org/wiki/Here_We_Go_(Steelers_song)",
        "https://en.wikipedia.org/wiki/Highmark_Stadium_(Pennsylvania)",
        "https://en.wikipedia.org/wiki/History_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Idlewild_and_Soak_Zone",
        "https://en.wikipedia.org/wiki/Jack_Rabbit_(Kennywood)",
        "https://en.wikipedia.org/wiki/Jock_tax",
        "https://en.wikipedia.org/wiki/John_Forbes_(British_Army_officer)",
        "https://en.wikipedia.org/wiki/Lawrenceville_(Pittsburgh)",
        "https://en.wikipedia.org/wiki/List_of_Pittsburgh_Steelers_Pro_Bowl_selections",
        "https://en.wikipedia.org/wiki/List_of_Pittsburgh_Steelers_first-round_draft_picks",
        "https://en.wikipedia.org/wiki/List_of_corporations_in_Pittsburgh",
        "https://en.wikipedia.org/wiki/Logos_and_uniforms_of_the_Pittsburgh_Steelers",
        "https://en.wikipedia.org/wiki/Mike_Sullivan_(ice_hockey)",
        "https://en.wikipedia.org/wiki/Monongahela_River",
        "https://en.wikipedia.org/wiki/Myron_Cope",
        "https://en.wikipedia.org/wiki/Oakmont_Country_Club",
        "https://en.wikipedia.org/wiki/Ohio_River",
        "https://en.wikipedia.org/wiki/Orin_O%27Brien",
        "https://en.wikipedia.org/wiki/PNC_Financial_Services",
        "https://en.wikipedia.org/wiki/PNC_Park",
        "https://en.wikipedia.org/wiki/PPG_Paints_Arena",
        "https://en.wikipedia.org/wiki/Phipps_Conservatory_and_Botanical_Gardens",
        "https://en.wikipedia.org/wiki/Pierogi",
        "https://en.wikipedia.org/wiki/Pittsburgh",
        "https://en.wikipedia.org/wiki/Pittsburgh_Bureau_of_Fire",
        "https://en.wikipedia.org/wiki/Pittsburgh_City-County_Building",
        "https://en.wikipedia.org/wiki/Pittsburgh_City_Council",
        "https://en.wikipedia.org/wiki/Pittsburgh_Maulers_(1984)",
        "https://en.wikipedia.org/wiki/Pittsburgh_Mills",
        "https://en.wikipedia.org/wiki/Pittsburgh_Panthers",
        "https://en.wikipedia.org/wiki/Pittsburgh_Passion",
        "https://en.wikipedia.org/wiki/Pittsburgh_Penguins",
        "https://en.wikipedia.org/wiki/Pittsburgh_Penguins_records",
        "https://en.wikipedia.org/wiki/Pittsburgh_Pirates",
        "https://en.wikipedia.org/wiki/Pittsburgh_Post-Gazette",
        "https://en.wikipedia.org/wiki/Pittsburgh_Produce_Terminal",
        "https://en.wikipedia.org/wiki/Pittsburgh_Riverhounds_SC",
        "https://en.wikipedia.org/wiki/Pittsburgh_Steelers",
        "https://en.wikipedia.org/wiki/Pittsburgh_Symphony_Orchestra",
        "https://en.wikipedia.org/wiki/Pittsburgh_Thunderbirds",
        "https://en.wikipedia.org/wiki/Pittsburgh_flood_of_1936",
        "https://en.wikipedia.org/wiki/Pittsburgh_synagogue_shooting",
        "https://en.wikipedia.org/wiki/Prothonotary",
        "https://en.wikipedia.org/wiki/Renegade_(Styx_song)",
        "https://en.wikipedia.org/wiki/Richard_S._Caliguiri_City_of_Pittsburgh_Great_Race",
        "https://en.wikipedia.org/wiki/Roberto_Clemente",
        "https://en.wikipedia.org/wiki/Roberto_Clemente_Bridge",
        "https://en.wikipedia.org/wiki/Soldiers_and_Sailors_Memorial_Hall_and_Museum",
        "https://en.wikipedia.org/wiki/Sports_%26_Exhibition_Authority_of_Pittsburgh_and_Allegheny_County",
        "https://en.wikipedia.org/wiki/Sports_in_Pittsburgh",
        "https://en.wikipedia.org/wiki/Steelmark",
        "https://en.wikipedia.org/wiki/Strip_District,_Pittsburgh",
        "https://en.wikipedia.org/wiki/Super_Bowl_XLIII",
        "https://en.wikipedia.org/wiki/Terrible_Towel",
        "https://en.wikipedia.org/wiki/The_Maybe_Man",
        "https://en.wikipedia.org/wiki/Three_Rivers_Arts_Festival",
        "https://en.wikipedia.org/wiki/Three_Rivers_Stadium",
        "https://en.wikipedia.org/wiki/University_of_Pittsburgh",
        "https://en.wikipedia.org/wiki/Wilkes-Barre/Scranton_Penguins",
        "https://en.wikipedia.org/wiki/William_Pitt,_1st_Earl_of_Chatham",
        "https://en.wikipedia.org/wiki/Women%27s_Center_%26_Shelter_of_Greater_Pittsburgh",
        "https://firstnightpgh.trustarts.org/",
        "https://improv.com/pittsburgh/calendar/",
        "https://mattress.org/about/",
        "https://pbt.org/performances/",
        "https://peterseneventscenter.com/events",
        "https://pittsburghpanthers.com/calendar",
        "https://pittsburghpanthers.com/sports/mens-soccer/schedule",
        "https://pittsburghpanthers.com/sports/softball/schedule",
        "https://pittsburghparks.org/frick-environmental-center/",
        "https://promowestlive.com/our-venues/stage-ae",
        "https://pvgp.org/charities/",
        "https://pvgp.org/schenley-park/",
        "https://randyland.club/",
        "https://steelcityrollerderby.org/",
        "https://trustarts.org/pct_home/about",
        "https://trustarts.org/pct_home/about/history",
        "https://trustarts.org/pct_home/events",
        "https://www.cmu.edu/hub/calendar/",
        "https://www.gatewayclipper.com/",
        "https://www.heinzhistorycenter.org/",
        "https://www.heinzhistorycenter.org/about/",
        "https://www.heinzhistorycenter.org/about/history/",
        "https://www.heinzhistorycenter.org/about/smithsonian-affiliation/",
        "https://www.heinzhistorycenter.org/exhibitions/mister-rogers-neighborhood/",
        "https://www.heinzhistorycenter.org/fort-pitt/",
        "https://www.heinzhistorycenter.org/visit/",
        "https://www.livenation.com/venue/KovZ917AJa7/roxian-theatre-events",
        "https://www.mlb.com/pirates/fans/city-connect",
        "https://www.mlb.com/pirates/schedule/2026-04",
        "https://www.mlb.com/pirates/tickets/promotions",
        "https://www.nhl.com/penguins/fans/hall-of-fame",
        "https://www.nhl.com/penguins/news/",
        "https://www.nhl.com/penguins/news/penguins-radio-network-announces-new-broadcast-team",
        "https://www.nhl.com/penguins/schedule",
        "https://www.nhl.com/penguins/tickets/promotions",
        "https://www.phipps.conservatory.org/calendar/",
        "https://www.picklesburgh.com/",
        "https://www.pittsburghopera.org/about/",
        "https://www.pittsburghopera.org/season/",
        "https://www.pittsburghopera.org/tickets/",
        "https://www.pittsburghsavoyards.org/",
        "https://www.ppgpaintsarena.com/events",
        "https://www.rungreatrace.com/",
        "https://www.springcarnival.org/about.shtml",
        "https://www.steelers.com/community/",
        "https://www.steelers.com/schedule/",
        "https://www.steelers.com/team/coaches-roster/",
        "https://www.thefrickpittsburgh.org/about-us",
        "https://www.thefrickpittsburgh.org/visit",
        "https://www.warhol.org/",
        "https://www.warhol.org/andy-warhols-life/",
        "https://www.warhol.org/collection/",
        "https://www.warhol.org/contact/",
        "https://www.warhol.org/the-pop-district/",
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
