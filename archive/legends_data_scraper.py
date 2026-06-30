import os
import json
import sys
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://apexlegends.wiki.gg"
DATA_FILE = "public/Legends.json"
OUT_DIR = "public/data/legends"

os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://apexlegends.wiki.gg/'
}

def scrape_legends_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        legends = json.load(f)['Legends']
        
    for idx, legend in enumerate(legends):
        name = legend['Name']
        print(f"[{idx+1}/{len(legends)}] Processing Data for {name}...")
        
        url_name = name.replace(' ', '_')
        url = f"{BASE_URL}/wiki/{url_name}"
        
        try:
            r = requests.get(url, headers=HEADERS)
            html = r.text
        except Exception as e:
            print(f"Failed to get HTML for {name}: {e}")
            continue
            
        soup = BeautifulSoup(html, 'html.parser')
        infobox = soup.find(class_='infobox')
        
        data_extracted = {}
        if infobox:
            for tr in infobox.find_all('tr'):
                th = tr.find('th')
                td = tr.find('td')
                if th and td:
                    data_extracted[th.text.strip()] = td.text.strip()
        
        # Build the JSON object
        legend_data = {
            "name": name,
            "lore": {
                "real_name": data_extracted.get("Real Name", ""),
                "age": data_extracted.get("Age", ""),
                "home_world": data_extracted.get("Homeworld", ""),
                "gender": data_extracted.get("Gender", ""),
                "bio": "" 
            },
            "abilities": {
                "passive": { 
                    "name": data_extracted.get("Passive Ability", ""), 
                    "description": "" 
                },
                "tactical": { 
                    "name": data_extracted.get("Tactical Ability", ""), 
                    "description": "", 
                    "cooldown": "" 
                },
                "ultimate": { 
                    "name": data_extracted.get("Ultimate Ability", ""), 
                    "description": "", 
                    "cooldown": "" 
                }
            },
            "patch_history": []
        }
        
        out_file = os.path.join(OUT_DIR, f"{name.lower().replace(' ', '_')}.json")
        with open(out_file, 'w', encoding='utf-8') as out_f:
            json.dump(legend_data, out_f, indent=2, ensure_ascii=False)
            
        print(f"  Saved {out_file}")

if __name__ == "__main__":
    scrape_legends_data()
    print("Scraping Data complete.")
