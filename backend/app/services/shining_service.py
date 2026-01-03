import random
from typing import List, Dict, Optional


def touch_probability(probabilidad: float = 1.0) -> bool:
    """Define la probabilidad de tener el resplandor (0-100)"""
    return random.random() < probabilidad / 100


def tag_maker(abilities_config: List[Dict] = None) -> List:
    """Crea de forma aleatoria una etiqueta de habilidad basándose en config opcional."""
    # Logic from chosseTouches.py
    rank_roll = random.randint(1, 5)
    match rank_roll:
        case 1:
            rank = 1
        case 2:
            rank = 4
        case 3:
            rank = 8
        case 4:
            rank = 12
        case 5:
            if random.randint(1, 10) == 1:
                rank = 18
            else:
                rank = 8

    category = random.randint(1, 10)
    index = random.randint(1, 10)
    return [rank, category, index]


def tag_checker(tag, tag_list, pl):
    if tag_list:
        if tag[0] <= pl:
            for tags in tag_list:
                if tag[1] == tags[1] and tag[2] == tags[2]:
                    return False
            return True
    else:
        if tag[0] <= pl:
            return True
    return False


def tag_module(tag, tag_list, pl):
    if tag_list:
        last_tag = tag_list[-1]
        x = last_tag[1]
        new_tag = [tag[0], x, tag[2]]
        if tag_checker(new_tag, tag_list, pl):
            return new_tag
    return tag


def power_level(max_pl: int = 50) -> int:
    """Genera nivel de poder, escalando si supera ciertos umbrales."""
    pl = random.randint(1, max_pl)
    # Threshold logic from original script, scales based on max_pl
    if pl >= (max_pl * 0.9):
        pl += random.randint(1, max_pl)
        if pl >= (max_pl * 1.9):
            pl += random.randint(1, max_pl * 2)
            if pl >= (max_pl * 3.9):
                pl += random.randint(1, 999)
    return pl


def convert_tag(tag, abilities_config: List[Dict] = None) -> Dict:
    """Convierte el tag numérico a un objeto descriptivo."""
    rank_map = {1: "D", 4: "C", 8: "B", 12: "A", 18: "S"}
    rank_letter = rank_map.get(tag[0], "F")

    # Try to find in config
    tag_name = f"Tag {tag[1]}-{tag[2]}"
    effect = "Intuición residual"

    if abilities_config:
        for ability in abilities_config:
            if ability.get("category") == tag[1] and ability.get("index") == tag[2]:
                tag_name = ability.get("name", tag_name)
                effect = ability.get("effect", effect)
                break

    return {"rank": rank_letter, "tag": tag_name, "effect": effect, "raw": tag}


def order_tags(tag_list):
    # Simplified ordering logic
    return sorted(tag_list, key=lambda x: (x[1], x[2]))


def generate_shining_abilities(settings: Dict) -> Optional[List[Dict]]:
    """Función principal que orquesta la generación basado en settings de campaña."""
    prob = settings.get("shining_prob", 1.0)
    max_pl = settings.get("max_power", 50)
    config = settings.get("abilities_config", [])

    if not touch_probability(prob):
        return None

    tag_list = []
    pl = power_level(max_pl)

    MAX_SKILLS = 50

    # OPTIMIZATION: Create a "deck" of all possible valid tags (category 1-10, index 1-10)
    # This prevents the "Coupon Collector Problem" entirely.
    deck = []
    for c in range(1, 11):
        for i in range(1, 11):
            deck.append((c, i))

    random.shuffle(deck)  # Shuffle once

    deck_idx = 0

    while pl > 0 and len(tag_list) < MAX_SKILLS and deck_idx < len(deck):
        # Pick next unique tag from deck
        cat, idx = deck[deck_idx]
        deck_idx += 1

        # Determine rank based on cost (try high rank first, then fit to PL)
        # Original logic had random ranks. Let's roll a rank preferred by logic
        rank_roll = random.randint(1, 100)

        # Simplified rank selection that favors fitting the PL
        # Ranks: S=18, A=12, B=8, C=4, D=1
        cost = 1
        if pl >= 18 and rank_roll <= 5:
            cost = 18  # 5% chance for S if affordable
        elif pl >= 12 and rank_roll <= 20:
            cost = 12  # 15% chance for A
        elif pl >= 8 and rank_roll <= 50:
            cost = 8  # 30% chance for B
        elif pl >= 4 and rank_roll <= 90:
            cost = 4  # 40% chance for C
        else:
            cost = 1  # Remainder D

        # Double check it fits (redundant but safe)
        if cost > pl:
            # Downgrade to max possible
            if pl >= 12:
                cost = 12
            elif pl >= 8:
                cost = 8
            elif pl >= 4:
                cost = 4
            else:
                cost = 1

        # If even D (1) is too expensive (pl=0), loop terminates via while condition
        if cost > pl:
            break

        # Check tag module logic (linking to previous tag) - simplified for performance
        # The original `tag_module` force-changed the category to match the last one under some conditions.
        # But since we are iterating a unique deck, forcing a change might create duplicates.
        # For performance/stability, we skip the `tag_module` recursive linking here
        # OR we accept the random deck pull as-is which is cleaner.
        # We will stick to the deck pull as it guarantees uniqueness and is fast.

        tag = [cost, cat, idx]
        tag_list.append(tag)
        pl -= cost

    tag_list = order_tags(tag_list)
    return [convert_tag(t, config) for t in tag_list]
