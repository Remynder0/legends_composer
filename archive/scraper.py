import cloudscraper
from bs4 import BeautifulSoup
import json
import time
import re

all_seasons_data = {}

# Création du scraper capable de contourner les protections de Cloudflare
scraper = cloudscraper.create_scraper(browser={
    'browser': 'chrome',
    'platform': 'windows',
    'desktop': True
})

for season in range(1, 23): # Jusqu'à 22
    print(f"Récupération de la Saison {season}...")
    url = f"https://apexlegends.fandom.com/wiki/Season_{season}"
    
    try:
        response = scraper.get(url)
        season_rewards = []
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Recherche de tous les tableaux de la page
            tables = soup.find_all('table')
            bp_table = None
            
            # Détection du tableau du passe de combat
            for table in tables:
                text_content = table.get_text().lower()
                # On cherche si le tableau contient Premium/Free ET (Level ou Obtained?)
                if ('premium' in text_content or 'free' in text_content) and ('level' in text_content or 'obtained?' in text_content):
                    bp_table = table
                    break
            
            if bp_table:
                rows = bp_table.find_all('tr')
                
                # Extraction des en-têtes
                headers_cells = rows[0].find_all(['th', 'td'])
                col_names = [h.get_text(strip=True) for h in headers_cells]
                
                # S'il n'y a pas d'en-tête clair, on force un format standard
                if not col_names or len(col_names) < 3:
                    col_names = ["Level", "Premium Rewards", "Free Rewards"]
                else:
                    if col_names[0] == "Obtained?":
                        col_names[0] = "Level"
                
                # Extraction des récompenses niveau par niveau
                for row in rows[1:]:
                    cells = row.find_all(['th', 'td'])
                    row_data = {}
                    
                    for i, cell in enumerate(cells):
                        if i < len(col_names):
                            # On récupère le texte en enlevant les espaces inutiles
                            text = ' '.join(cell.stripped_strings)
                            if text:
                                row_data[col_names[i]] = text
                    
                    # Correction pour les saisons 15 à 21 : 
                    # On s'assure de récupérer le numéro même s'il y a des espaces invisibles
                    if "Level" in row_data:
                        match = re.match(r'^(\d+)', row_data["Level"].strip())
                        if match:
                            row_data["Level"] = match.group(1) # On remplace par le numéro propre
                            season_rewards.append(row_data)
                        
            all_seasons_data[f"Season_{season}"] = season_rewards
            
            if not season_rewards:
                print(f" -> ⚠️ Avertissement : Tableau trouvé mais vide pour la saison {season}.")
            else:
                print(f" -> ✅ {len(season_rewards)} niveaux récupérés.")
                
        else:
            print(f" -> ❌ Erreur HTTP {response.status_code} pour la saison {season}")
            all_seasons_data[f"Season_{season}"] = {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f" -> ❌ Erreur lors de la récupération de la saison {season} : {e}")
        all_seasons_data[f"Season_{season}"] = {"error": str(e)}
        
    # Pause longue (5 secondes) OBLIGATOIRE pour ne pas subir l'erreur 403 de Cloudflare
    time.sleep(5)

# Sauvegarde dans un fichier JSON
output_filename = "apex_battle_pass.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(all_seasons_data, f, indent=4, ensure_ascii=False)

print(f"\nTerminé ! Les données ont été sauvegardées dans le fichier : {output_filename}")