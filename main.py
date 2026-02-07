from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import List, Dict, Optional
from translator import IngredientTranslator

app = FastAPI(
    title="Italian Recipe API",
    description="API italiana per ricette vegetariane e vegane",
    version="1.0.0"
)

# CORS per permettere richieste da Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEALDB_BASE = "https://www.themealdb.com/api/json/v1/1"

def translate_recipe(meal: Dict) -> Dict:
    """Traduce una ricetta in italiano"""
    ingredients = []
    
    # Estrai ingredienti
    for i in range(1, 21):
        ingredient = meal.get(f'strIngredient{i}', '').strip()
        measure = meal.get(f'strMeasure{i}', '').strip()
        
        if ingredient:
            ingredients.append({
                'name': IngredientTranslator.translate_ingredient(ingredient),
                'measure': IngredientTranslator.translate_measure(measure),
                'original_name': ingredient,
                'original_measure': measure
            })
    
    return {
        'id': meal.get('idMeal'),
        'name': meal.get('strMeal'),
        'category': meal.get('strCategory'),
        'image': meal.get('strMealThumb'),
        'ingredients': ingredients,
        'instructions': meal.get('strInstructions'),
        'isVegan': meal.get('strCategory', '').lower() == 'vegan',
        'isVegetarian': meal.get('strCategory', '').lower() in ['vegetarian', 'vegan']
    }

@app.get("/")
async def root():
    return {
        "message": "🇮🇹 Italian Recipe API",
        "version": "1.0.0",
        "endpoints": {
            "vegetarian": "/api/recipes/vegetarian",
            "search": "/api/recipes/search?q=pasta",
            "details": "/api/recipes/{id}"
        }
    }

@app.get("/api/recipes/vegetarian")
async def get_vegetarian_recipes():
    """Ottieni ricette vegetariane tradotte in italiano"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MEALDB_BASE}/filter.php?c=Vegetarian")
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Errore API esterna")
        
        data = response.json()
        meals = data.get('meals', [])
        
        # Ottieni dettagli per ogni ricetta
        translated_meals = []
        for meal in meals[:20]:  # Limita a 20 per velocità
            detail_response = await client.get(f"{MEALDB_BASE}/lookup.php?i={meal['idMeal']}")
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                if detail_data.get('meals'):
                    translated = translate_recipe(detail_data['meals'][0])
                    translated_meals.append(translated)
        
        return {
            "success": True,
            "count": len(translated_meals),
            "recipes": translated_meals
        }

@app.get("/api/recipes/search")
async def search_recipes(q: str):
    """Cerca ricette per nome"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MEALDB_BASE}/search.php?s={q}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Errore API esterna")
        
        data = response.json()
        meals = data.get('meals', [])
        
        if not meals:
            return {
                "success": True,
                "count": 0,
                "recipes": []
            }
        
        translated_meals = [translate_recipe(meal) for meal in meals]
        
        return {
            "success": True,
            "count": len(translated_meals),
            "recipes": translated_meals
        }

@app.get("/api/recipes/{recipe_id}")
async def get_recipe_details(recipe_id: str):
    """Ottieni dettagli ricetta tradotti"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MEALDB_BASE}/lookup.php?i={recipe_id}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Errore API esterna")
        
        data = response.json()
        meals = data.get('meals')
        
        if not meals:
            raise HTTPException(status_code=404, detail="Ricetta non trovata")
        
        translated = translate_recipe(meals[0])
        
        return {
            "success": True,
            "recipe": translated
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)