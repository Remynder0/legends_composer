import requests
from bs4 import BeautifulSoup
import json
import time

all_seasons_data = {}

# On utilise un User-Agent classique pour ne pas être bloqué par le site
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

for season in range(1, 19):
    print(f"Récupération de la Saison {season}...")
    url = f"https://apexlegends.fandom.com/wiki/Season_{season}"
    
    try:
        response = requests.get(url, headers=headers)
        season_rewards = []
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Recherche de tous les tableaux de la page
            tables = soup.find_all('table')
            bp_table = None
            
            # On identifie le tableau du Passe de Combat (il contient "Premium" ou "Free" et "Level")
            for table in tables:
                text_content = table.get_text().lower()
                if 'level' in text_content and ('premium' in text_content or 'free' in text_content):
                    bp_table = table
                    break
            
            if bp_table:
                rows = bp_table.find_all('tr')
                # Extraction des en-têtes (Niveau, Récompenses gratuites, etc.)
                headers_cells = rows[0].find_all(['th', 'td'])
                col_names = [h.get_text(strip=True) for h in headers_cells]
                
                # S'il n'y a pas d'en-tête clair, on force un format standard
                if not col_names:
                    col_names = ["Level", "Premium Rewards", "Free Rewards"]
                
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
                    
                    if row_data:
                        season_rewards.append(row_data)
                        
            all_seasons_data[f"Season_{season}"] = season_rewards
            
        else:
            print(f"Erreur HTTP {response.status_code} pour la saison {season}")
            all_seasons_data[f"Season_{season}"] = {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"Erreur lors de la récupération de la saison {season} : {e}")
        all_seasons_data[f"Season_{season}"] = {"error": str(e)}
        
    # Petite pause pour ne pas surcharger les serveurs de Fandom
    time.sleep(1)

# Sauvegarde dans un fichier JSON
output_filename = "apex_battle_pass.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(all_seasons_data, f, indent=4, ensure_ascii=False)

print(f"\nTerminé ! Les données ont été sauvegardées dans le fichier : {output_filename}")