from googlesearch import search
import time
import urllib.parse
import json

broken = [
    "https://en.wikipedia.org/wiki/Randy_Pausch_Last_Lecture",
    "https://en.wikipedia.org/wiki/Arthur_Mellon",
    "https://en.wikipedia.org/wiki/Carnegie_Mellon_University_College_of_Fine_Arts",
    "https://en.wikipedia.org/wiki/NavLab",
    "https://en.wikipedia.org/wiki/Plaid_Parliament_of_Pwning",
    "https://en.wikipedia.org/wiki/Buggy_(Carnegie_Mellon_University)",
    "https://en.wikipedia.org/wiki/Little_Italy_Days",
    "https://en.wikipedia.org/wiki/Gaucho_Parrilla_Argentina",
    "https://en.wikipedia.org/wiki/Sienna_Mercato",
    "https://en.wikipedia.org/wiki/Prantl%27s_Bakery",
    "https://en.wikipedia.org/wiki/Pusadee%27s_Garden",
    "https://en.wikipedia.org/wiki/Millie%27s_Homemade_Ice_Cream",
    "https://en.wikipedia.org/wiki/Morcilla_(restaurant)",
    "https://en.wikipedia.org/wiki/Commonplace_Coffee",
    "https://en.wikipedia.org/wiki/DiAnoia%27s_Eatery",
    "https://en.wikipedia.org/wiki/The_Eagle_(restaurant)",
    "https://en.wikipedia.org/wiki/Chengdu_Gourmet",
    "https://en.wikipedia.org/wiki/tako_(restaurant)",
    "https://en.wikipedia.org/wiki/Dish_Osteria_Bar",
    "https://en.wikipedia.org/wiki/Fet_Fisk",
    "https://en.wikipedia.org/wiki/Iron_Born_Pizza",
    "https://en.wikipedia.org/wiki/Driftwood_Oven",
    "https://en.wikipedia.org/wiki/Green_Forest_Churrascaria",
    "https://en.wikipedia.org/wiki/Mon_Aimee_Chocolat",
    "https://en.wikipedia.org/wiki/Tessaro%27s",
    "https://en.wikipedia.org/wiki/Jerry%27s_Records",
    "https://en.wikipedia.org/wiki/Pittsburgh_Cultural_District",
]

mapping = {}
print("Starting Google Search Mapping...")

for b in broken:
    entity = urllib.parse.unquote(b.split('/')[-1])
    entity = entity.replace('_', ' ')
    query = f"{entity} pittsburgh"
    
    try:
        # Get the first result from Google
        results = list(search(query))
        if results:
            new_link = results[0]
            print(f"[{entity}] -> \n  {new_link}")
            mapping[b] = new_link
        else:
            print(f"[{entity}] -> NOT FOUND")
    except Exception as e:
        print(f"[{entity}] -> ERROR: {e}")
        
    time.sleep(1)

with open("link_mapping.json", "w") as f:
    json.dump(mapping, f, indent=4)
print("Saved to link_mapping.json")
