import json
import sys
from random import choice, shuffle

# Forcer l'encodage UTF-8 pour afficher correctement les émojis dans la console Windows
sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Chargement des données
# ---------------------------------------------------------------------------

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

MOBILITY_SCORE = {"high": 3, "medium": 2, "low": 1, "none": 0}

def get_effects(legend):
    """Retourne un set des effets principaux d'une légende (primary + secondary)."""
    effects = set()
    for val in [legend.get("primary_value", []), legend.get("secondary_value", [])]:
        if val:
            effects.add(val[0])
    return effects

def has_team_movement(legend):
    """True si la légende apporte un mouvement d'équipe moyen ou long."""
    for val in [legend.get("primary_value", []), legend.get("secondary_value", [])]:
        if val and val[0] in ("repositioning", "mobility"):
            if "team" in val and ("medium" in val or "long" in val):
                return True
    return False

def has_visual_barrier(legend):
    for val in [legend.get("primary_value", []), legend.get("secondary_value", [])]:
        if val and val[0] == "barrier" and "visual" in val:
            return True
    return False


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
        mob = legend.get("mobility", "none")
        total_mobility_score += MOBILITY_SCORE.get(mob, 0)
        if mob in ("none", "low"):
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
    if avg_mobility >= 2:
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

def score_candidate(candidate, current_team):
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
        mob_bonus = MOBILITY_SCORE.get(candidate.get("mobility", "none"), 0)

    # 3. Synergie positive : le candidat renforce ce que l'équipe fait déjà.
    #    Ex : une équipe avec "barrier" gagne à avoir un 2e perso "barrier".
    #    Ex : une équipe mobile profite d'un autre perso avec repositioning/mobility.
    team_effects = eval_before["effects"]
    candidate_effects = get_effects(candidate)
    overlap = team_effects & candidate_effects

    # Effets qui se renforcent vraiment en doublant
    STACKABLE = {"barrier", "scanning", "repositioning", "mobility", "damage", "control", "shield", "healing"}
    synergy_bonus = len(overlap & STACKABLE)

    # 4. Malus si le candidat n'apporte rien de nouveau ni de complémentaire
    #    (tous ses effets sont déjà couverts ET aucun manque comblé)
    new_effects = candidate_effects - team_effects
    if not new_effects and gaps_filled == 0:
        return -1  # pousse ce candidat tout en bas du pool

    return gaps_filled * 10 + mob_bonus + synergy_bonus


def pick_synergic(current_team, legends_list):
    """Choisit la meilleure légende pour compléter l'équipe, avec un peu d'aléatoire."""
    team_names = {l["Name"] for l in current_team}
    pool = [l for l in legends_list if l["Name"] not in team_names]

    if not pool:
        return None

    # Score chaque candidat
    scored = [(score_candidate(c, current_team), c) for c in pool]
    max_score = max(s for s, _ in scored)

    # Parmi les meilleurs, on tire au sort (évite la déterminisme total)
    best = [c for s, c in scored if s == max_score]
    return choice(best)


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

MOBILITY_LABEL = {"high": "🟢 haute", "medium": "🟡 moyenne", "low": "🟠 faible", "none": "🔴 aucune"}

def legend_summary(legend, role_label):
    name     = legend["Name"]
    cls      = legend["Class"]
    mob      = MOBILITY_LABEL.get(legend.get("mobility", "none"), "?")
    prim     = legend.get("primary_value", [])
    sec      = legend.get("secondary_value", [])
    prim_str = "/".join(prim) if prim else "-"
    sec_str  = "/".join(sec)  if sec  else "-"
    return (
        f"  {role_label} : {name} ({cls})\n"
        f"    Mobilité    : {mob}\n"
        f"    Primaire    : {prim_str}\n"
        f"    Secondaire  : {sec_str}"
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
    mob_str = "élevée 🟢" if mob_avg >= 2.5 else "correcte 🟡" if mob_avg >= 1.5 else "faible 🔴"
    print(f"\n  Mobilité moyenne de l'équipe : {mob_avg:.1f}/3 ({mob_str})")
    print(f"{'-'*45}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_team(legends_list, size=3):
    """Construit une équipe de 2 ou 3 : P1 aléatoire, les suivants synergiques."""
    shuffle(legends_list)  # évite le biais lié à l'ordre du JSON
    p1 = choice(legends_list)
    p2 = pick_synergic([p1], legends_list)
    if size == 2:
        return [p1, p2]
    flex = pick_synergic([p1, p2], legends_list)
    return [p1, p2, flex]


def ask_team_size():
    """Demande la taille d'équipe souhaitée (2 ou 3)."""
    while True:
        choice_input = input("Taille de l'équipe (2 ou 3) : ").strip()
        if choice_input in ("2", "3"):
            return int(choice_input)
        print("  Entrez 2 ou 3.")


def main():
    legends_list, special_synergies = get_data()

    print("\n"+"="*45)
    print("   APEX LEGENDS — COMPOSITION ALÉATOIRE")
    print("="*45)

    size = ask_team_size()

    team = build_team(legends_list, size)
    print_team(team)
    print_evaluation(team, special_synergies)

    while True:
        again = input("Nouvelle composition ? : ").strip().lower()
        if again == "":
            team = build_team(legends_list, size)
            print_team(team)
            print_evaluation(team, special_synergies)
        elif again == "n":
            print("Bonne chance sur le terrain !\n")
            break


if __name__ == "__main__":
    main()