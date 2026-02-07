import re

class IngredientTranslator:
    """Traduttore italiano completo con riordino grammaticale"""
    
    # DIZIONARIO COMPLETO - OGNI SINGOLA PAROLA
    WORDS = {
        # Verdure
        'tomato': 'pomodoro',
        'tomatoes': 'pomodori',
        'onion': 'cipolla',
        'onions': 'cipolle',
        'garlic': 'aglio',
        'carrot': 'carota',
        'carrots': 'carote',
        'potato': 'patata',
        'potatoes': 'patate',
        'eggplant': 'melanzana',
        'eggplants': 'melanzane',
        'aubergine': 'melanzana',
        'zucchini': 'zucchina',
        'courgette': 'zucchina',
        'pepper': 'peperone',
        'peppers': 'peperoni',
        'bell': 'peperone',
        'chili': 'peperoncino',
        'mushroom': 'fungo',
        'mushrooms': 'funghi',
        'spinach': 'spinaci',
        'lettuce': 'lattuga',
        'cucumber': 'cetriolo',
        'broccoli': 'broccoli',
        'cauliflower': 'cavolfiore',
        'celery': 'sedano',
        'cabbage': 'cavolo',
        'kale': 'cavolo riccio',
        'asparagus': 'asparagi',
        'peas': 'piselli',
        'bean': 'fagiolo',
        'beans': 'fagioli',
        'lentil': 'lenticchia',
        'lentils': 'lenticchie',
        'chickpea': 'cece',
        'chickpeas': 'ceci',
        'corn': 'mais',
        'pumpkin': 'zucca',
        'squash': 'zucca',
        'beetroot': 'barbabietola',
        'beet': 'barbabietola',
        'radish': 'ravanello',
        'leek': 'porro',
        'fennel': 'finocchio',
        'artichoke': 'carciofo',
        
        # Frutta
        'apple': 'mela',
        'apples': 'mele',
        'banana': 'banana',
        'bananas': 'banane',
        'orange': 'arancia',
        'oranges': 'arance',
        'lemon': 'limone',
        'lemons': 'limoni',
        'lime': 'lime',
        'strawberry': 'fragola',
        'strawberries': 'fragole',
        'blueberry': 'mirtillo',
        'blueberries': 'mirtilli',
        'raspberry': 'lampone',
        'raspberries': 'lamponi',
        'cherry': 'ciliegia',
        'cherries': 'ciliegie',
        'peach': 'pesca',
        'pear': 'pera',
        'plum': 'prugna',
        'grape': 'uva',
        'grapes': 'uva',
        'melon': 'melone',
        'watermelon': 'anguria',
        'pineapple': 'ananas',
        'mango': 'mango',
        'avocado': 'avocado',
        'kiwi': 'kiwi',
        'fig': 'fico',
        'date': 'dattero',
        'raisin': 'uvetta',
        
        # Erbe e spezie
        'basil': 'basilico',
        'parsley': 'prezzemolo',
        'oregano': 'origano',
        'thyme': 'timo',
        'rosemary': 'rosmarino',
        'sage': 'salvia',
        'mint': 'menta',
        'cilantro': 'coriandolo',
        'coriander': 'coriandolo',
        'dill': 'aneto',
        'chives': 'erba cipollina',
        'bay': 'alloro',
        'leaf': 'foglia',
        'leaves': 'foglie',
        'cinnamon': 'cannella',
        'ginger': 'zenzero',
        'cumin': 'cumino',
        'paprika': 'paprika',
        'turmeric': 'curcuma',
        'nutmeg': 'noce moscata',
        'clove': 'chiodo di garofano',
        'cloves': 'chiodi di garofano',
        'cardamom': 'cardamomo',
        'vanilla': 'vaniglia',
        'curry': 'curry',
        'mustard': 'senape',
        
        # Cereali e legumi
        'rice': 'riso',
        'pasta': 'pasta',
        'bread': 'pane',
        'flour': 'farina',
        'wheat': 'grano',
        'oat': 'avena',
        'oats': 'avena',
        'barley': 'orzo',
        'quinoa': 'quinoa',
        'couscous': 'couscous',
        'bulgur': 'bulgur',
        
        # Condimenti
        'oil': 'olio',
        'olive': 'oliva',
        'salt': 'sale',
        'pepper': 'pepe',
        'vinegar': 'aceto',
        'balsamic': 'balsamico',
        'soy': 'soia',
        'sauce': 'salsa',
        'ketchup': 'ketchup',
        'mayonnaise': 'maionese',
        'honey': 'miele',
        'sugar': 'zucchero',
        'butter': 'burro',
        'milk': 'latte',
        'cream': 'panna',
        'cheese': 'formaggio',
        'yogurt': 'yogurt',
        'egg': 'uovo',
        'eggs': 'uova',
        'water': 'acqua',
        'stock': 'brodo',
        'broth': 'brodo',
        'vegetable': 'vegetale',
        'tofu': 'tofu',
        'tempeh': 'tempeh',
        
        # Frutta secca
        'almond': 'mandorla',
        'almonds': 'mandorle',
        'walnut': 'noce',
        'walnuts': 'noci',
        'hazelnut': 'nocciola',
        'hazelnuts': 'nocciole',
        'pistachio': 'pistacchio',
        'pistachios': 'pistacchi',
        'cashew': 'anacardo',
        'cashews': 'anacardi',
        'peanut': 'arachide',
        'peanuts': 'arachidi',
        'pine': 'pinolo',
        'nut': 'noce',
        'nuts': 'noci',
        'seed': 'seme',
        'seeds': 'semi',
        'sunflower': 'girasole',
        'pumpkin': 'zucca',
        'sesame': 'sesamo',
        'chia': 'chia',
        'flax': 'lino',
        
        # AGGETTIVI - PER RIORDINO
        'fresh': 'fresco',
        'dried': 'secco',
        'frozen': 'congelato',
        'canned': 'in scatola',
        'chopped': 'tritato',
        'minced': 'tritato finemente',
        'diced': 'a cubetti',
        'sliced': 'affettato',
        'grated': 'grattugiato',
        'ground': 'macinato',
        'whole': 'intero',
        'raw': 'crudo',
        'cooked': 'cotto',
        'fried': 'fritto',
        'roasted': 'arrostito',
        'baked': 'al forno',
        'steamed': 'al vapore',
        'boiled': 'bollito',
        'grilled': 'grigliato',
        'smoked': 'affumicato',
        
        # Colori (per verdure)
        'red': 'rosso',
        'green': 'verde',
        'yellow': 'giallo',
        'white': 'bianco',
        'black': 'nero',
        'brown': 'marrone',
        'orange': 'arancione',
        
        # Dimensioni
        'large': 'grande',
        'small': 'piccolo',
        'medium': 'medio',
        'big': 'grande',
        'baby': 'baby',
        
        # Altro
        'extra': 'extra',
        'virgin': 'vergine',
        'can': 'barattolo',
        'jar': 'vasetto',
        'bunch': 'mazzo',
        'stalk': 'gambo',
        'sprig': 'rametto',
        'head': 'testa',
        'bulb': 'bulbo',
        'cherry': 'ciliegino',
        'sun': 'sole',
        'spring': 'primavera',
    }
    
    # UNITÀ DI MISURA
    UNITS = {
        'tsp': 'cucchiaino',
        'tsps': 'cucchiaini',
        'teaspoon': 'cucchiaino',
        'teaspoons': 'cucchiaini',
        'tbsp': 'cucchiaio',
        'tbsps': 'cucchiai',
        'tablespoon': 'cucchiaio',
        'tablespoons': 'cucchiai',
        'cup': 'tazza',
        'cups': 'tazze',
        'ml': 'ml',
        'l': 'litro',
        'liter': 'litro',
        'liters': 'litri',
        'g': 'g',
        'kg': 'kg',
        'gram': 'grammo',
        'grams': 'grammi',
        'oz': 'oz',
        'lb': 'lb',
        'pound': 'libbra',
        'pinch': 'pizzico',
        'dash': 'pizzico',
        'clove': 'spicchio',
        'cloves': 'spicchi',
        'piece': 'pezzo',
        'pieces': 'pezzi',
        'slice': 'fetta',
        'slices': 'fette',
    }
    
    # FRASI FISSE (eccezioni al riordino)
    FIXED_PHRASES = {
        'olive oil': 'olio d\'oliva',
        'extra virgin olive oil': 'olio extravergine d\'oliva',
        'soy sauce': 'salsa di soia',
        'bay leaf': 'foglia di alloro',
        'bay leaves': 'foglie di alloro',
        'bell pepper': 'peperone',
        'cherry tomato': 'pomodorino',
        'cherry tomatoes': 'pomodorini',
        'sun-dried tomato': 'pomodoro secco',
        'sun-dried tomatoes': 'pomodori secchi',
        'spring onion': 'cipollotto',
        'spring onions': 'cipollotti',
    }
    
    # AGGETTIVI (per identificarli)
    ADJECTIVES = {
        'fresh', 'dried', 'frozen', 'canned', 'chopped', 'minced',
        'diced', 'sliced', 'grated', 'ground', 'whole', 'raw',
        'cooked', 'fried', 'roasted', 'baked', 'steamed', 'boiled',
        'grilled', 'smoked', 'red', 'green', 'yellow', 'white',
        'black', 'brown', 'orange', 'large', 'small', 'medium',
        'big', 'baby', 'extra', 'virgin'
    }
    
    @classmethod
    def translate_ingredient(cls, ingredient: str) -> str:
        """Traduce ingrediente con riordino grammaticale"""
        if not ingredient:
            return ''
        
        original = ingredient.strip()
        lower = original.lower()
        
        # 1. Rimuovi prefissi comuni
        lower = re.sub(r'^(a|an|the)\s+', '', lower)
        lower = re.sub(r'\s*\(.*?\)\s*', '', lower)  # Rimuovi parentesi
        lower = lower.strip()
        
        # 2. Cerca frasi fisse (eccezioni)
        if lower in cls.FIXED_PHRASES:
            return cls.FIXED_PHRASES[lower]
        
        # 3. Dividi in parole
        words = lower.split()
        if not words:
            return original
        
        # 4. Traduci ogni parola
        translated_words = []
        for word in words:
            # Rimuovi punteggiatura
            clean_word = word.strip('.,;:')
            if clean_word in cls.WORDS:
                translated_words.append(cls.WORDS[clean_word])
            else:
                translated_words.append(clean_word)
        
        # 5. RIORDINO GRAMMATICALE
        # Pattern inglese: ADJECTIVE + NOUN → italiano: NOUN + ADJECTIVE
        reordered = cls._reorder_words(words, translated_words)
        
        return reordered
    
    @classmethod
    def _reorder_words(cls, original_words, translated_words):
        """Riordina parole secondo grammatica italiana"""
        if len(translated_words) == 1:
            return translated_words[0].capitalize()
        
        # Identifica aggettivi e nomi
        adjectives = []
        nouns = []
        
        for i, word in enumerate(original_words):
            clean = word.strip('.,;:').lower()
            if clean in cls.ADJECTIVES:
                adjectives.append((i, translated_words[i]))
            else:
                nouns.append((i, translated_words[i]))
        
        # Se non ci sono aggettivi, ritorna così com'è
        if not adjectives:
            return ' '.join(translated_words).capitalize()
        
        # RIORDINO: prima i nomi, poi gli aggettivi
        # Es: "fresh red tomato" → "pomodoro rosso fresco"
        result = []
        
        # Aggiungi nomi
        for idx, noun in nouns:
            result.append(noun)
        
        # Aggiungi aggettivi
        for idx, adj in adjectives:
            result.append(adj)
        
        # Capitalizza
        final = ' '.join(result)
        return final.capitalize() if final else original_words[0]
    
    @classmethod
    def translate_unit(cls, unit: str, quantity: float = 1) -> str:
        """Traduce unità con singolare/plurale"""
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
            translated = translated.replace('grammi', 'grammo')
            translated = translated.replace('litri', 'litro')
        
        return translated
    
    @classmethod
    def translate_measure(cls, measure: str) -> str:
        """Traduce misura completa"""
        if not measure or measure.strip() == '':
            return ''
        
        # Estrai numero e unità
        parts = measure.strip().split(' ', 1)
        
        try:
            # Prova a convertire il primo elemento in numero
            quantity = float(parts[0])
            unit = parts[1] if len(parts) > 1 else ''
            
            translated_unit = cls.translate_unit(unit, quantity)
            
            # Formatta numero
            if quantity == int(quantity):
                num_str = str(int(quantity))
            else:
                num_str = str(quantity).rstrip('0').rstrip('.')
            
            return f"{num_str} {translated_unit}".strip()
        except (ValueError, IndexError):
            # Se non è un numero, ritorna così
            return measure