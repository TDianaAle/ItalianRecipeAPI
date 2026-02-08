import re
from typing import Dict


class IngredientTranslator:
    """
    Traduttore deterministico EN → IT per ingredienti culinari.
    Produce frasi italiane naturali con accordi automatici.
    """

    # ==================================================
    # UNITÀ DI MISURA
    # ==================================================
    UNITS = {
        "tsp": "cucchiaino",
        "tsps": "cucchiaini",
        "tbsp": "cucchiaio",
        "tbsps": "cucchiai",
        "cup": "tazza",
        "cups": "tazze",
        "g": "g",
        "kg": "kg",
        "ml": "ml",
        "oz": "oz",
        "lb": "lb",
        "can": "barattolo",
        "jar": "vasetto",
        "container": "contenitore",
    }

    # ==================================================
    # BASE INGREDIENTI (con numero grammaticale)
    # ==================================================
    # value = (traduzione, numero)
    # numero: "singular" | "plural"
    BASE_INGREDIENTS = {
        "green bell pepper": ("peperone verde", "singular"),
        "red bell pepper": ("peperone rosso", "singular"),
        "yellow bell pepper": ("peperone giallo", "singular"),
        "bell pepper": ("peperone", "singular"),

        "black beans": ("fagioli neri", "plural"),
        "beans": ("fagioli", "plural"),
        "bean": ("fagiolo", "singular"),

        "whole kernel corn": ("mais in chicchi", "singular"),
        "kernel corn": ("mais in chicchi", "singular"),

        "garlic salt": ("sale all'aglio", "singular"),

        "extra-firm tofu": ("tofu extra compatto", "singular"),
        "firm tofu": ("tofu compatto", "singular"),
        "tofu": ("tofu", "singular"),

        "avocados": ("avocado", "plural"),
        "avocado": ("avocado", "singular"),

        "onions": ("cipolle", "plural"),
        "onion": ("cipolla", "singular"),

        "zucchini": ("zucchina", "singular"),
    }

    # ==================================================
    # STATI (forma maschile singolare → accordata dopo)
    # ==================================================
    STATES = {
        "drained": "scolato",
        "undrained": "non scolato",
        "peeled": "sbucciato",
        "pitted": "denocciolato",
        "seeded": "privato dei semi",
        "pat dry": "asciugato",
        "to taste": "q.b.",
    }

    # ==================================================
    # AZIONI
    # ==================================================
    ACTIONS = {
        "cut into thin strips": "tagliato a striscioline sottili",
        "cut into strips": "tagliato a strisce",
        "cut into thin 1-inch segments": "tagliato in segmenti sottili da 2,5 cm",
        "cut into cubes": "tagliato a cubetti",
        "cut into 1/2 inch cubes": "tagliato a cubetti da 1,5 cm",
        "julienned": "a julienne",
        "sliced": "affettato",
        "chopped": "tritato",
        "minced": "tritato finemente",
    }

    # ==================================================
    # API PUBBLICA
    # ==================================================
    @classmethod
    def translateFullIngredient(cls, name: str, measure: str) -> Dict[str, str]:
        return {
            "name": cls.translate_ingredient(name),
            "measure": cls.translate_measure(measure),
        }

    # ==================================================
    # TRADUZIONE INGREDIENTE
    # ==================================================
    @classmethod
    def translate_ingredient(cls, ingredient: str) -> str:
        if not ingredient:
            return ""

        text = ingredient.lower()
        text = re.sub(r"\(.*?\)", "", text)
        text = text.replace("-", " ")
        text = text.strip()

        data = cls._parse_semantics(text)
        phrase = cls._build_italian_phrase(data)

        return phrase.capitalize() if phrase else ingredient.capitalize()

    # ==================================================
    # PARSING SEMANTICO
    # ==================================================
    @classmethod
    def _parse_semantics(cls, text: str) -> dict:
        data = {
            "base": None,
            "number": "singular",
            "states": [],
            "actions": [],
        }

        # base ingrediente (frasi lunghe prima)
        for key, (value, number) in sorted(
            cls.BASE_INGREDIENTS.items(), key=lambda x: -len(x[0])
        ):
            if key in text:
                data["base"] = value
                data["number"] = number
                break

        # stati
        for key, value in cls.STATES.items():
            if key in text:
                data["states"].append(value)

        # azioni
        for key, value in sorted(cls.ACTIONS.items(), key=lambda x: -len(x[0])):
            if key in text:
                data["actions"].append(value)

        return data

    # ==================================================
    # COSTRUZIONE FRASE + ACCORDI
    # ==================================================
    @classmethod
    def _build_italian_phrase(cls, data: dict) -> str:
        if not data["base"]:
            return ""

        parts = [data["base"]]

        # stati con accordo
        if data["states"]:
            agreed_states = [
                cls._agree(state, data["number"])
                for state in data["states"]
            ]
            parts.append(", ".join(agreed_states))

        # azioni con accordo
        if data["actions"]:
            agreed_actions = [
                cls._agree(action, data["number"])
                for action in data["actions"]
            ]
            parts.append(" ".join(agreed_actions))

        return " ".join(parts)

    # ==================================================
    # ACCORDO SINGOLARE / PLURALE
    # ==================================================
    @staticmethod
    def _agree(text: str, number: str) -> str:
        """
        Applica accordo grammaticale semplice
        maschile singolare → maschile plurale
        """
        if number == "singular":
            return text

        # regole minime per participi
        replacements = {
            "ato": "ati",
            "uto": "uti",
            "ito": "iti",
            "o": "i",
        }

        for sing, plur in replacements.items():
            if text.endswith(sing):
                return text[:-len(sing)] + plur

        return text

    # ==================================================
    # TRADUZIONE MISURA
    # ==================================================
    @classmethod
    def translate_unit(cls, unit: str, quantity: float = 1) -> str:
        if not unit:
            return ""

        unit = unit.lower().strip()
        translated = cls.UNITS.get(unit, unit)

        if quantity == 1:
            translated = translated.replace("cucchiai", "cucchiaio")
            translated = translated.replace("cucchiaini", "cucchiaino")
            translated = translated.replace("tazze", "tazza")

        return translated

    @classmethod
    def translate_measure(cls, measure: str) -> str:
        if not measure or measure.strip() == "":
            return ""

        parts = measure.strip().lower().split(" ", 1)

        try:
            qty = float(parts[0])
            unit = parts[1] if len(parts) > 1 else ""

            unit_it = cls.translate_unit(unit, qty)

            if qty.is_integer():
                qty = int(qty)

            return f"{qty} {unit_it}".strip()
        except Exception:
            return measure
