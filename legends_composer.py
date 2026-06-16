import json
import sys
from random import choice, choices, shuffle

# Forcer l'encodage UTF-8 pour afficher correctement les émojis dans la console Windows
sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Chargement des données
# ---------------------------------------------------------------------------

HISTORY_FILE = "history.json"

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def get_data(path="Legends.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        legends = data.get("Legends", [])
        synergies = data.get("SPECIAL_SYNERGIES", [])
        if not legends:
            raise ValueError("Aucune légende trouvée dans le fichier.")
        return legends, synergies
    except FileNotFoundError:
        raise SystemExit(f"Erreur : '{path}' introuvable.")
    except json.JSONDecodeError:
        raise SystemExit(f"Erreur : '{path}' n'est pas un JSON valide.")


# ---------------------------------------------------------------------------
# Analyse d'une légende
# ---------------------------------------------------------------------------

def get_effects(legend):
    """Retourne un set des effets principaux d'une légende (score >= 5)."""
    effects = set()
    for stat, value in legend.get("stats", {}).items():
        if value >= 5:
            effects.add(stat)
    return effects

def has_team_movement(legend):
    """True si la légende apporte un mouvement d'équipe moyen ou long."""
    team_movers = {"Valkyrie", "Pathfinder", "Wraith", "Alter", "Mad Maggie", "Ash", "Octane", "Axel"}
    return legend["Name"] in team_movers

def has_visual_barrier(legend):
    return legend["Name"] in ("Bangalore", "Catalyst")

def has_long_scan(legend):
    """True si la légende apporte un scan à longue portée."""
    return legend["Name"] in ("Crypto", "Sparrow")


# ---------------------------------------------------------------------------
# Évaluation d'une équipe
# ---------------------------------------------------------------------------

def evaluate_team(team):
    """
    Retourne un dict décrivant les forces et les manques de la composition.
    """
    all_effects = set()
    team_has_movement = False
    team_has_visual_barrier = False
    total_mobility_score = 0
    has_low_mobility_member = False

    for legend in team:
        all_effects |= get_effects(legend)
        if has_team_movement(legend):
            team_has_movement = True
        if has_visual_barrier(legend):
            team_has_visual_barrier = True
        mob = legend.get("stats", {}).get("mobility", 0)
        total_mobility_score += mob
        if mob <= 3:
            has_low_mobility_member = True

    avg_mobility = total_mobility_score / len(team) if team else 0

    missing = []

    # Un perso none/low dans l'équipe = besoin d'un mouvement d'équipe
    if not team_has_movement and has_low_mobility_member:
        missing.append("team_movement")

    # Scanning obligatoire si fumée/barrière visuelle présente
    if team_has_visual_barrier and "scanning" not in all_effects:
        missing.append("scanning")

    # Barrière physique (zonage défensif)
    if "barrier" not in all_effects:
        missing.append("barrier")

    # Scanning en général
    if "scanning" not in all_effects and "scanning" not in missing:
        missing.append("scanning")

    # Capacité de combat
    if "damage" not in all_effects and "control" not in all_effects:
        missing.append("combat")

    # Couverture (shield ou healing)
    if "shield" not in all_effects and "healing" not in all_effects:
        missing.append("survivability")

    strengths = []
    if team_has_movement:
        strengths.append("mouvement d'équipe")
    if "scanning" in all_effects:
        strengths.append("scan ennemi")
    if "barrier" in all_effects:
        strengths.append("contrôle de zone")
    if "shield" in all_effects or "healing" in all_effects:
        strengths.append("survie")
    if "damage" in all_effects or "control" in all_effects:
        strengths.append("puissance de feu")
    if avg_mobility >= 6.5:
        strengths.append("mobilité globale élevée")

    return {
        "missing": missing,
        "strengths": strengths,
        "avg_mobility": avg_mobility,
        "effects": all_effects,
    }


# ---------------------------------------------------------------------------
# Sélection d'un coéquipier synergique
# ---------------------------------------------------------------------------

def get_historical_bonus(candidate, current_team, history):
    """Calcule un bonus ou malus basé sur les classements passés (top 1 = +9.5, top 20 = -9.5)."""
    if not history:
        return 0
        
    bonus = 0
    matches = 0
    
    for record in history:
        record_team = set(record["team"])
        placement = record["placement"]
        
        # On regarde la synergie historique entre le candidat et chaque membre actuel
        for member in current_team:
            if candidate["Name"] in record_team and member["Name"] in record_team:
                bonus += (10.5 - placement)
                matches += 1
                
    if matches > 0:
        return (bonus / matches) * 0.5  # Modérateur d'impact sur le score global
    return 0

def score_candidate(candidate, current_team, history=None):
    """
    Score un candidat selon les manques ET les synergies positives avec l'équipe actuelle.
    Plus le score est élevé, meilleur est le candidat.
    """
    eval_before = evaluate_team(current_team)
    eval_after  = evaluate_team(current_team + [candidate])

    # 1. Manques comblés (priorité absolue)
    gaps_filled = len(eval_before["missing"]) - len(eval_after["missing"])

    # 2. Bonus mobilité si l'équipe a un perso statique sans mouvement d'équipe
    mob_bonus = 0
    if "team_movement" in eval_before["missing"]:
        mob_bonus = candidate.get("stats", {}).get("mobility", 0) / 3.0

    # 3. Synergie positive : le candidat renforce ce que l'équipe fait déjà.
    #    Ex : une équipe mobile profite d'un autre perso avec repositioning/mobility.
    team_effects = eval_before["effects"]
    candidate_effects = get_effects(candidate)
    overlap = team_effects & candidate_effects

    # Effets qui se renforcent vraiment en doublant
    STACKABLE = {"scanning", "repositioning", "mobility", "damage", "control", "shield", "healing"}
    synergy_bonus = len(overlap & STACKABLE)

    # Synergie spécifique pour "barrier" : nécessite un outil de "repositioning" ou un "long scan"
    team_has_barrier = "barrier" in team_effects
    candidate_has_barrier = "barrier" in candidate_effects
    
    team_has_repo = "repositioning" in team_effects
    candidate_has_repo = "repositioning" in candidate_effects
    
    team_has_ls = any(has_long_scan(l) for l in current_team)
    candidate_has_ls = has_long_scan(candidate)
    
    if (team_has_barrier and (candidate_has_repo or candidate_has_ls)) or \
       (candidate_has_barrier and (team_has_repo or team_has_ls)):
        synergy_bonus += 1

    # 4. Malus si le candidat n'apporte rien de nouveau ni de complémentaire
    #    (tous ses effets sont déjà couverts ET aucun manque comblé)
    new_effects = candidate_effects - team_effects
    if not new_effects and gaps_filled == 0:
        return -1  # pousse ce candidat tout en bas du pool

    base_score = gaps_filled * 10 + mob_bonus + synergy_bonus
    
    if history is not None:
        base_score += get_historical_bonus(candidate, current_team, history)
        
    return base_score


def pick_synergic(current_team, legends_list, history=None):
    """Choisit une légende pour compléter l'équipe via un tirage aléatoire pondéré (aléatoire biaisé)."""
    team_names = {l["Name"] for l in current_team}
    pool = [l for l in legends_list if l["Name"] not in team_names]

    if not pool:
        return None

    # Score chaque candidat
    scored = [(score_candidate(c, current_team, history), c) for c in pool]

    # Convertir les scores en poids pour un tirage aléatoire biaisé
    # On décale les scores et on les élève au carré pour favoriser fortement les meilleures synergies
    min_score = min(s for s, _ in scored)
    weights = [(s - min_score + 1) ** 2 for s, _ in scored]
    candidates = [c for _, c in scored]

    return choices(candidates, weights=weights, k=1)[0]


# ---------------------------------------------------------------------------
# Synergies spéciales
# ---------------------------------------------------------------------------

def check_special_synergies(team, special_synergies):
    """Retourne la liste des synergies spéciales présentes dans l'équipe."""
    team_names = {l["Name"] for l in team}
    found = []
    for synergy in special_synergies:
        if set(synergy["legends"]).issubset(team_names):
            found.append(synergy)
    return found


# ---------------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------------

def legend_summary(legend, role_label):
    name     = legend["Name"]
    cls      = legend["Class"]
    stats    = legend.get("stats", {})
    mob      = stats.get("mobility", 0)
    
    top_stats = sorted([(k, v) for k, v in stats.items() if v > 0 and k != "mobility"], key=lambda x: x[1], reverse=True)
    stats_str = ", ".join([f"{k}:{v}" for k, v in top_stats])
    if not stats_str:
        stats_str = "Aucune"

    return (
        f"  {role_label} : {name} ({cls})\n"
        f"    Mobilité    : {mob}/10\n"
        f"    Stats       : {stats_str}"
    )

def print_team(team, title="COMPOSITION"):
    if len(team) == 2:
        roles = ["Joueur 1", "Joueur 2"]
    else:
        roles = ["Joueur 1", "Joueur 2", "Flex    "]
    print(f"\n{'-'*45}")
    print(f"  {title}")
    print(f"{'-'*45}")
    for legend, role in zip(team, roles):
        print(legend_summary(legend, role))
    print()

def print_evaluation(team, special_synergies):
    result = evaluate_team(team)
    special = check_special_synergies(team, special_synergies)

    # Synergie spéciale en avant si présente
    if special:
        for s in special:
            print(f"  ⚡ SUPER SYNERGIE : « {s['name']} »")
            print(f"     {s['description']}")
        print()

    print("  SYNERGIES")
    if result["strengths"]:
        for s in result["strengths"]:
            print(f"    ✅  {s}")
    else:
        print("    (aucune synergie détectée)")

    print()
    print("  MANQUES")
    if result["missing"]:
        labels = {
            "team_movement":  "Mouvement d'équipe",
            "scanning":       "Scan / information",
            "barrier":        "Contrôle de zone (barrière)",
            "combat":         "Puissance de feu",
            "survivability":  "Survie (shield/heal)",
        }
        for m in result["missing"]:
            print(f"    ⚠️   {labels.get(m, m)}")
    else:
        print("    ✅  Toutes les bases stratégiques sont couvertes !")

    mob_avg = result["avg_mobility"]
    mob_str = "élevée 🟢" if mob_avg >= 7 else "correcte 🟡" if mob_avg >= 4 else "faible 🔴"
    print(f"\n  Mobilité moyenne de l'équipe : {mob_avg:.1f}/10 ({mob_str})")
    print(f"{'-'*45}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_team(legends_list, size=3, history=None):
    """Construit une équipe de 2 ou 3 : P1 aléatoire, les suivants synergiques."""
    shuffle(legends_list)  # évite le biais lié à l'ordre du JSON
    p1 = choice(legends_list)
    p2 = pick_synergic([p1], legends_list, history)
    if size == 2:
        return [p1, p2]
    flex = pick_synergic([p1, p2], legends_list, history)
    return [p1, p2, flex]


def ask_team_size():
    """Demande la taille d'équipe souhaitée (2 ou 3)."""
    while True:
        choice_input = input("Taille de l'équipe (2 ou 3) : ").strip()
        if choice_input in ("2", "3"):
            return int(choice_input)
        print("  Entrez 2 ou 3.")


def generate_presence_stats(legends_list, iterations=100, team_size=2, history=None):
    """Lance la génération d'équipe plusieurs fois et affiche les statistiques de présence."""
    presence_counts = {legend["Name"]: 0 for legend in legends_list}
    
    for _ in range(iterations):
        team = build_team(legends_list, size=team_size, history=history)
        for legend in team:
            presence_counts[legend["Name"]] += 1
            
    print(f"\n{'-'*45}")
    print(f"  STATISTIQUES DE PRÉSENCE ({iterations} équipes de {team_size})")
    print(f"{'-'*45}")
    
    # Tri par ordre décroissant de présence
    sorted_presence = sorted(presence_counts.items(), key=lambda x: x[1], reverse=True)
    
    for name, count in sorted_presence:
        percentage = (count / iterations) * 100
        print(f"  {name:<15} : {percentage:>5.1f}% ({count} fois)")
    print(f"{'-'*45}\n")


def main():
    legends_list, special_synergies = get_data()
    history = load_history()

    print("\n"+"="*45)
    print("   APEX LEGENDS — COMPOSITION ALÉATOIRE")
    print("="*45)

    size = ask_team_size()

    team = build_team(legends_list, size, history)
    print_team(team)
    print_evaluation(team, special_synergies)

    while True:
        place = input("Classement de la partie (1-20, ou 'Entrée' pour ignorer) : ").strip()
        if place.isdigit() and 1 <= int(place) <= 20:
            history.append({
                "team": [l["Name"] for l in team],
                "placement": int(place)
            })
            save_history(history)
            print("  [+] Résultat enregistré, l'algorithme s'adapte !\n")

        again = input("Nouvelle composition (Entrée), 'stats', ou 'n' pour quitter : ").strip().lower()
        if again == "":
            team = build_team(legends_list, size, history)
            print_team(team)
            print_evaluation(team, special_synergies)
        elif again == "stats":
            try:
                iters = int(input("Nombre d'itérations ? (défaut 100) : ") or "100")
                generate_presence_stats(legends_list, iterations=iters, team_size=size, history=history)
            except ValueError:
                print("  Nombre invalide.")
        elif again == "n":
            print("Bonne chance sur le terrain !\n")
            break


if __name__ == "__main__":
    main()