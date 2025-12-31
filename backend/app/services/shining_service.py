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

    while pl > 0:
        tag = tag_maker(config)
        tag = tag_module(tag, tag_list, pl)
        if tag_checker(tag, tag_list, pl):
            tag_list.append(tag)
            pl -= tag[0]

    tag_list = order_tags(tag_list)
    return [convert_tag(t, config) for t in tag_list]
