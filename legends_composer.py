import json
from random import choice

MEMO = {
    "Effect": {
        # ability to creates a barrier, can be used for area control or to block a doorway, can be visual or physical
        "barrier": [["area", "doorway"], ["visual", "physical"]],
        # ability to boosts the stats of the user or their team
        "boost": ["team", "personal"],
        # ability to control an enemy, can be AOE or personal
        "control": ["AOE", "personal"],
        # ability to deal damage, can be AOE or gun, can be used for poke or area denial
        "damage": [["AOE", "gun"], ["poke", "denial"]],
        # ability to heal the user or their team
        "healing": ["personal", "team"],
        # ability to get more loot than normal, can be high, medium or low
        "looting": ["high", "medium", "low"],
        # ability to move instantly, agressively, defensively or repositionally, can be used for personal movement or to move the team
        "mobility": [["long", "medium", "short"], ["personal", "team"]],
        # ability to move with thought, can be used for personal movement or to move the team, can be long, medium or short range
        "repositioning": [["long", "medium", "short"], ["personal", "team"]],
        # ability to scan enemies for medium short range, for long is to get map information
        "scanning": ["long", "medium", "short"],
        # ability to create a shield, AOE: physical or personal: legend shield, can be used for the team or just for the user
        "shield": [["AOE", "personal"], ["team", "personal"]],
        # ability to be independent of the categories, can be used for anything
        "wildcard": ["wildcard"]
    }
}

def get_legends():
    """Récupère la liste des légendes à partir du fichier JSON."""
    try:
        with open("Legends.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            legends_list = data.get("Legends", [])
            if not legends_list:
                print("Erreur : Aucune legende trouvee dans le fichier.")
                return []
            return legends_list
    except FileNotFoundError:
        print("Erreur : Le fichier 'Legends.json' est introuvable.")
        return []
    except json.JSONDecodeError:
        print("Erreur : Le fichier 'Legends.json' n'est pas un JSON valide.")
        return []
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
        return []

def get_effects_from_legend(legend):
    """Récupère les effets (valeurs) d'une légende à partir de ses valeurs primaires et secondaires."""
    effects = set()
    
    for val in [legend.get('primary_value', []), legend.get('secondary_value', [])]:
        if not val: continue
        effects.add(val[0])
        
    return effects

def display_effects(effect):
    """Compte le nombre d'effets présents dans le roster."""
    legends_list = get_legends()
    count_effects = 0
    list_effects = []
    for legend in legends_list:
        for key in ["primary_value", "secondary_value"]:
            val = legend.get(key, [])
            if val and val[0] == effect:
                count_effects += 1
                list_effects.append(legend)

    print(f"Nombre de legendes avec l'effet '{effect}': {count_effects}")
    for legend in list_effects:
        print(f"- {legend.get('Name')} ({legend.get('Class')})")




def evaluate_team_composition(team):
    """Évalue les valeurs (effets) directes présentes dans l'équipe pour déduire les manques."""
    effects = set()
    has_visual_barrier = False
    has_team_movement = False
    all_have_mobility = True
    
    for legend in team:
        legend_has_mobility = False
        for val in [legend.get('primary_value', []), legend.get('secondary_value', [])]:
            if not val: continue
            effect = val[0]
            effects.add(effect)
            
            if effect == "barrier" and "visual" in val:
                has_visual_barrier = True
            if effect in ["repositioning", "mobility"]:
                legend_has_mobility = True
                if "team" in val and ("medium" in val or "long" in val):
                    has_team_movement = True
                    
        if not legend_has_mobility:
            all_have_mobility = False
                
    missing_values = []
    
    # 1. Mouvement d'équipe prioritaire (sauf si tout le monde a déjà une mobilité personnelle)
    if not has_team_movement and not all_have_mobility:
        missing_values.append("team_movement")
        
    # 2. Info vitale si l'équipe compte boucher la vision
    if has_visual_barrier and "scanning" not in effects:
        missing_values.append("scanning")
        
    # 3. Sécurisation : On veut de vraies barrières, les shields sont ignorés
    if "barrier" not in effects:
        missing_values.append("barrier")
        
    # 4. Info classique
    if "scanning" not in effects and "scanning" not in missing_values:
        missing_values.append("scanning")
        
    # 5. Capacité de combat (dégâts ou contrôle)
    if "damage" not in effects and "control" not in effects:
        missing_values.append("combat")
        
    return missing_values

def get_candidates_for_missing_value(missing_value, legends_list, current_team):
    """Trouve les légendes qui apportent exactement la valeur qui manque à l'équipe."""
    team_names = [l.get("Name") for l in current_team]
    candidates = []
    
    for legend in legends_list:
        if legend.get("Name") in team_names:
            continue
            
        is_match = False
        for val in [legend.get('primary_value', []), legend.get('secondary_value', [])]:
            if not val: continue
            effect = val[0]
            
            if missing_value == "scanning" and effect == "scanning":
                is_match = True
            elif missing_value == "team_movement" and effect in ["repositioning", "mobility"] and "team" in val and ("medium" in val or "long" in val):
                is_match = True
            elif missing_value == "barrier" and effect == "barrier":
                is_match = True
            elif missing_value == "combat" and effect in ["damage", "control"]:
                is_match = True
                
        if is_match:
            candidates.append(legend)
            
    # Règle de priorité : si on cherche du mouvement d'équipe, le "repositioning" l'emporte sur la "mobility"
    if missing_value == "team_movement" and candidates:
        best_candidates = []
        for c in candidates:
            for val in [c.get('primary_value', []), c.get('secondary_value', [])]:
                if val and val[0] == "repositioning" and "team" in val and ("medium" in val or "long" in val):
                    best_candidates.append(c)
                    break
        if best_candidates:
            return best_candidates
            
    return candidates



def main():
    legends_list = get_legends()

    

    display_effects("control")
    print("--- EQUIPE COMPLETE SYNERGIQUE (3 LEGENDES) ---")
    
    # 1. Le Leader est tiré au hasard
    team = [choice(legends_list)]
    
    # 2. On complète l'équipe intelligemment
    while len(team) < 3:
        missing = evaluate_team_composition(team)
        
        # S'il ne manque plus rien d'essentiel, on prend un bon flex (différent de l'équipe)
        if not missing:
            pool = [l for l in legends_list if l.get("Name") not in [t.get("Name") for t in team]]
            team.append(choice(pool))
            continue
            
        candidates = get_candidates_for_missing_value(missing[0], legends_list, team)
        
        if candidates:
            team.append(choice(candidates))
        else:
            pool = [l for l in legends_list if l.get("Name") not in [t.get("Name") for t in team]]
            team.append(choice(pool))
            
    # 3. Affichage
    for i, legend in enumerate(team):
        prim = legend.get('primary_value', [])
        sec = legend.get('secondary_value', [])
        print(f"[{i+1}] {legend.get('Name')} ({legend.get('Class')}) -> Apporte : {prim[0] if prim else ''}, {sec[0] if sec else ''}")
        
    final_missing = evaluate_team_composition(team)
    if not final_missing:
        print("\n=> Composition d'elite : toutes les bases strategiques sont couvertes !")
    else:
        print(f"\n=> Composition correcte. Manque encore : {', '.join(final_missing)}")

if __name__ == "__main__":
    main()