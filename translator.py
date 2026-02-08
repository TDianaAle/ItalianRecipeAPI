import re
from typing import Dict

class IngredientTranslator:
    """Traduttore avanzato ingredienti API → Italiano naturale"""
    
    # Dizionario base parola→parola
    WORDS = {
        # Verdure e frutta
        'tomato':'pomodoro','tomatoes':'pomodori','onion':'cipolla','onions':'cipolle',
        'garlic':'aglio','carrot':'carota','carrots':'carote','potato':'patata','potatoes':'patate',
        'eggplant':'melanzana','zucchini':'zucchina','courgette':'zucchina','bell':'peperone',
        'pepper':'peperone','peppers':'peperoni','chili':'peperoncino','mushroom':'fungo',
        'mushrooms':'funghi','spinach':'spinaci','lettuce':'lattuga','cucumber':'cetriolo',
        'broccoli':'broccoli','cauliflower':'cavolfiore','celery':'sedano','cabbage':'cavolo',
        'kale':'cavolo riccio','asparagus':'asparagi','peas':'piselli','bean':'fagiolo',
        'beans':'fagioli','lentil':'lenticchia','lentils':'lenticchie','chickpea':'cece',
        'chickpeas':'ceci','corn':'mais','pumpkin':'zucca','squash':'zucca','beetroot':'barbabietola',
        'beet':'barbabietola','radish':'ravanello','leek':'porro','fennel':'finocchio','artichoke':'carciofo',
        'apple':'mela','apples':'mele','banana':'banana','bananas':'banane','orange':'arancia',
        'oranges':'arance','lemon':'limone','lemons':'limoni','lime':'lime','strawberry':'fragola',
        'strawberries':'fragole','blueberry':'mirtillo','blueberries':'mirtilli','raspberry':'lampone',
        'raspberries':'lamponi','cherry':'ciliegia','cherries':'ciliegie','peach':'pesca','pear':'pera',
        'plum':'prugna','grape':'uva','grapes':'uva','melon':'melone','watermelon':'anguria',
        'pineapple':'ananas','mango':'mango','avocado':'avocado','kiwi':'kiwi','fig':'fico','date':'dattero',
        'raisin':'uvetta',
        
        # Legumi, cereali, tofu
        'rice':'riso','pasta':'pasta','bread':'pane','flour':'farina','wheat':'grano','oat':'avena',
        'oats':'avena','barley':'orzo','quinoa':'quinoa','couscous':'couscous','bulgur':'bulgur',
        'tofu':'tofu','tempeh':'tempeh',
        
        # Condimenti
        'oil':'olio','olive':'oliva','salt':'sale','pepper':'pepe','vinegar':'aceto','balsamic':'balsamico',
        'soy':'soia','sauce':'salsa','ketchup':'ketchup','mayonnaise':'maionese','honey':'miele',
        'sugar':'zucchero','butter':'burro','milk':'latte','cream':'panna','cheese':'formaggio','yogurt':'yogurt',
        'egg':'uovo','eggs':'uova','water':'acqua','stock':'brodo','broth':'brodo','vegetable':'vegetale',
        
        # Frutta secca e semi
        'almond':'mandorla','almonds':'mandorle','walnut':'noce','walnuts':'noci','hazelnut':'nocciola',
        'hazelnuts':'nocciole','pistachio':'pistacchio','pistachios':'pistacchi','cashew':'anacardo',
        'cashews':'anacardi','peanut':'arachide','peanuts':'arachidi','pine':'pinolo','nut':'noce','nuts':'noci',
        'seed':'seme','seeds':'semi','sunflower':'girasole','pumpkin':'zucca','sesame':'sesamo','chia':'chia',
        'flax':'lino',
        
        # Aggettivi e azioni
        'fresh':'fresco','dried':'secco','frozen':'congelato','canned':'in scatola','chopped':'tritato',
        'minced':'tritato finemente','diced':'a cubetti','sliced':'affettato','grated':'grattugiato',
        'ground':'macinato','whole':'intero','raw':'crudo','cooked':'cotto','fried':'fritto','roasted':'arrostito',
        'baked':'al forno','steamed':'al vapore','boiled':'bollito','grilled':'grigliato','smoked':'affumicato',
        'peeled':'sbucciato','pitted':'denocciolato','seeded':'privato dei semi','lengthwise':'longitudinalmente',
        'cut':'tagliato','into':'in','thin':'sottile','medium':'medio','large':'grande','small':'piccolo',
        'extra':'extra','virgin':'vergine','red':'rosso','green':'verde','yellow':'giallo','white':'bianco',
        'black':'nero','brown':'marrone','orange':'arancione',
        
        # Contenitori
        'can':'barattolo','jar':'vasetto','tube':'tubo','container':'contenitore','bunch':'mazzo','cup':'tazza',
    }

    UNITS = {
        'tsp':'cucchiaino','tsps':'cucchiaini','teaspoon':'cucchiaino','teaspoons':'cucchiaini',
        'tbsp':'cucchiaio','tbsps':'cucchiai','tablespoon':'cucchiaio','tablespoons':'cucchiai',
        'cup':'tazza','cups':'tazze','ml':'ml','l':'litro','liter':'litro','liters':'litri',
        'g':'g','kg':'kg','gram':'grammo','grams':'grammi','oz':'oz','lb':'libbra','pinch':'pizzico',
        'dash':'pizzico','clove':'spicchio','cloves':'spicchi','piece':'pezzo','pieces':'pezzi',
        'slice':'fetta','slices':'fette'
    }

    ADJECTIVES = set([
        'fresh','dried','frozen','canned','chopped','minced','diced','sliced','grated','ground','whole',
        'raw','cooked','fried','roasted','baked','steamed','boiled','grilled','smoked','peeled','pitted',
        'seeded','lengthwise','thin','medium','large','small','extra','virgin','red','green','yellow','white',
        'black','brown','orange'
    ])

    FIXED_PHRASES = {
        'olive oil':"olio d'oliva",'extra virgin olive oil':"olio extravergine d'oliva",
        'soy sauce':"salsa di soia",'bay leaf':"foglia di alloro",'bay leaves':"foglie di alloro",
        'bell pepper':"peperone",'cherry tomato':"pomodorino",'cherry tomatoes':"pomodorini",
        'spring onion':"cipollotto",'spring onions':"cipollotti",
    }

    @classmethod
    def translate_ingredient(cls, ingredient: str) -> str:
        """Traduzione completa ingrediente in italiano naturale"""
        if not ingredient: return ''
        lower = ingredient.lower().strip()
        lower = re.sub(r'^(a|an|the)\s+', '', lower)
        lower = re.sub(r'\s*\(.*?\)\s*', '', lower)

        # Frasi fisse
        if lower in cls.FIXED_PHRASES:
            return cls.FIXED_PHRASES[lower]

        # Split parole
        words = re.split(r'[\s,]+', lower)
        translated_words = [cls.WORDS.get(w, w) for w in words]

        # Riordino aggettivi
        nouns = [t for i,t in enumerate(translated_words) if words[i] not in cls.ADJECTIVES]
        adjectives = [t for i,t in enumerate(translated_words) if words[i] in cls.ADJECTIVES]

        # Combina in frase italiana naturale
        result = nouns + adjectives
        return ' '.join(result).capitalize()

    @classmethod
    def translate_unit(cls, unit: str, quantity: float=1) -> str:
        if not unit: return ''
        lower = unit.lower().strip()
        translated = cls.UNITS.get(lower, unit)
        if quantity==1:
            translated = re.sub(r's$', '', translated)
        return translated

    @classmethod
    def translate_measure(cls, measure: str) -> str:
        if not measure or measure.strip()=='': return ''
        parts = measure.strip().split(' ',1)
        try:
            quantity = float(parts[0])
            unit = parts[1] if len(parts)>1 else ''
            translated_unit = cls.translate_unit(unit, quantity)
            num_str = str(int(quantity)) if quantity==int(quantity) else str(quantity)
            return f"{num_str} {translated_unit}".strip()
        except (ValueError, IndexError):
            return measure

    @classmethod
    def translate_full(cls, name:str, measure:str) -> Dict[str,str]:
        return {
            'name': cls.translate_ingredient(name),
            'measure': cls.translate_measure(measure)
        }

# --- Esempio ---
if __name__=="__main__":
    sample_ingredients = [
        {"name":"large red bell pepper","measure":"1"},
        {"name":"barattolo fagioli drained nero","measure":"1"},
        {"name":"Banane lengthwise affettato","measure":"2"},
        {"name":"olio d'oliva","measure":"2 tbsps"}
    ]
    for ing in sample_ingredients:
        print(IngredientTranslator.translate_full(ing['name'], ing['measure']))
