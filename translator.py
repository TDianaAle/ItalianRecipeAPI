class IngredientTranslator:
    """Traduttore italiano per ingredienti e unità di misura"""
    
    # Dizionario ingredienti (versione ridotta, aggiungeremo tutti dopo)
    INGREDIENTS = {
        # Verdure
        'tomato': 'pomodoro',
        'tomatoes': 'pomodori',
        'cherry tomatoes': 'pomodorini',
        'onion': 'cipolla',
        'onions': 'cipolle',
        'garlic': 'aglio',
        'garlic clove': 'spicchio d\'aglio',
        'carrot': 'carota',
        'carrots': 'carote',
        'potato': 'patata',
        'potatoes': 'patate',
        'zucchini': 'zucchina',
        'eggplant': 'melanzana',
        'bell pepper': 'peperone',
        'mushroom': 'fungo',
        'mushrooms': 'funghi',
        'spinach': 'spinaci',
        'lettuce': 'lattuga',
        'cucumber': 'cetriolo',
        'broccoli': 'broccoli',
        'cauliflower': 'cavolfiore',
        'celery': 'sedano',
        
        # Erbe
        'basil': 'basilico',
        'parsley': 'prezzemolo',
        'oregano': 'origano',
        'thyme': 'timo',
        'rosemary': 'rosmarino',
        'sage': 'salvia',
        
        # Legumi e cereali
        'rice': 'riso',
        'pasta': 'pasta',
        'bread': 'pane',
        'flour': 'farina',
        'beans': 'fagioli',
        'chickpeas': 'ceci',
        'lentils': 'lenticchie',
        
        # Condimenti
        'olive oil': 'olio d\'oliva',
        'salt': 'sale',
        'pepper': 'pepe',
        'vinegar': 'aceto',
        'lemon': 'limone',
        'cheese': 'formaggio',
        'butter': 'burro',
        'milk': 'latte',
        'egg': 'uovo',
        'eggs': 'uova',
        'sugar': 'zucchero',
        'honey': 'miele',
        'water': 'acqua',
        
        # Spezie
        'cinnamon': 'cannella',
        'ginger': 'zenzero',
        'cumin': 'cumino',
        'paprika': 'paprika',
        'chili': 'peperoncino',
    }
    
    UNITS = {
        'tsp': 'cucchiaino',
        'tsps': 'cucchiaini',
        'tbsp': 'cucchiaio',
        'tbsps': 'cucchiai',
        'cup': 'tazza',
        'cups': 'tazze',
        'ml': 'ml',
        'l': 'litro',
        'g': 'g',
        'kg': 'kg',
        'oz': 'oz',
        'lb': 'lb',
        'clove': 'spicchio',
        'cloves': 'spicchi',
        'pinch': 'pizzico',
        'dash': 'pizzico',
    }
    
    @classmethod
    def translate_ingredient(cls, ingredient: str) -> str:
        """Traduce un ingrediente in italiano"""
        if not ingredient:
            return ''
        
        lower = ingredient.lower().strip()
        
        # Cerca traduzione esatta
        if lower in cls.INGREDIENTS:
            return cls.INGREDIENTS[lower]
        
        # Cerca traduzione parziale
        for eng, ita in cls.INGREDIENTS.items():
            if eng in lower:
                return lower.replace(eng, ita)
        
        # Capitalizza se non trovato
        return ingredient.capitalize()
    
    @classmethod
    def translate_unit(cls, unit: str, quantity: float = 1) -> str:
        """Traduce unità di misura con singolare/plurale"""
        if not unit:
            return ''
        
        lower = unit.lower().strip()
        translated = cls.UNITS.get(lower, unit)
        
        # Singolare/plurale
        if quantity == 1.0:
            translated = translated.replace('cucchiai', 'cucchiaio')
            translated = translated.replace('cucchiaini', 'cucchiaino')
            translated = translated.replace('tazze', 'tazza')
            translated = translated.replace('spicchi', 'spicchio')
        
        return translated
    
    @classmethod
    def translate_measure(cls, measure: str) -> str:
        """Traduce misura completa (numero + unità)"""
        if not measure or measure.strip() == '':
            return ''
        
        parts = measure.strip().split(' ', 1)
        if len(parts) == 1:
            return measure
        
        try:
            quantity = float(parts[0])
            unit = parts[1] if len(parts) > 1 else ''
            translated_unit = cls.translate_unit(unit, quantity)
            
            # Formatta numero
            if quantity == int(quantity):
                num_str = str(int(quantity))
            else:
                num_str = str(quantity)
            
            return f"{num_str} {translated_unit}".strip()
        except ValueError:
            return measure