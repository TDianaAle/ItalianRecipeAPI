from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Dict
from translator import IngredientTranslator

app = FastAPI(
    title="Italian Recipe API",
    description="API italiana veloce con Forkify",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FORKIFY_BASE = "https://forkify-api.herokuapp.com/api/v2/recipes"

def translate_forkify_recipe(recipe: Dict) -> Dict:
    """Traduce ricetta completa"""
    ingredients = []
    
    for ing in recipe.get('ingredients', []):
        quantity = ing.get('quantity') or ''
        unit = ing.get('unit') or ''
        description = ing.get('description', '')
        
        measure = f"{quantity} {unit}".strip() if quantity else unit
        
        translated = IngredientTranslator.translateFullIngredient(
            description,
            measure
        )
        
        ingredients.append({
            'name': translated['name'],
            'measure': translated['measure'],
            'original_name': description,
            'original_measure': measure
        })
    
    return {
        'id': recipe.get('id'),
        'name': recipe.get('title'),
        'category': 'Vegetarian',
        'image': recipe.get('image_url'),
        'ingredients': ingredients,
        'instructions': recipe.get('source_url'),
        'servings': recipe.get('servings'),
        'cookingTime': recipe.get('cooking_time'),
        'publisher': recipe.get('publisher'),
        'isVegan': is_vegan(recipe.get('title', '')),
        'isVegetarian': True,
        'source': 'Forkify'
    }

def is_vegan(title: str) -> bool:
    """Controllo veloce su titolo"""
    title_lower = title.lower()
    vegan_keywords = ['vegan', 'plant-based', 'plant based']
    non_vegan = ['egg', 'cheese', 'butter', 'milk', 'cream', 'yogurt', 'chicken', 'meat', 'fish']
    
    if any(k in title_lower for k in vegan_keywords):
        return True
    if any(k in title_lower for k in non_vegan):
        return False
    return False

@app.get("/")
async def root():
    return {
        "message": "🇮🇹 Italian Recipe API v3.0 - VELOCE",
        "version": "3.0.0",
        "endpoints": {
            "preview": "/api/recipes/preview?type=vegetarian|vegan|both",
            "details": "/api/recipes/{id}"
        }
    }

@app.get("/api/recipes/preview")
async def get_recipes_preview(type: str = "vegetarian"):
    """
    Preview ricette VELOCI (solo lista, no dettagli)
    type: vegetarian | vegan | both
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        results = []
        seen_ids = set()
        
        # Decidi quali query fare
        if type == "both":
            queries = ["vegetarian", "vegan"]
        elif type == "vegan":
            queries = ["vegan"]
        else:
            queries = ["vegetarian"]
        
        for query in queries:
            try:
                response = await client.get(f"{FORKIFY_BASE}?search={query}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get('data', {}).get('recipes', [])
                    
                    for recipe in recipes[:50]:  # Max 50 per query
                        recipe_id = recipe.get('id')
                        
                        # Evita duplicati
                        if recipe_id in seen_ids:
                            continue
                        seen_ids.add(recipe_id)
                        
                        is_vegan_recipe = is_vegan(recipe.get('title', ''))
                        
                        # Filtro solo se NON è "both"
                        if type == "vegan" and not is_vegan_recipe:
                            continue
                        if type == "vegetarian" and is_vegan_recipe:
                            continue
                        
                        results.append({
                            'id': recipe_id,
                            'name': recipe.get('title'),
                            'image': recipe.get('image_url'),
                            'publisher': recipe.get('publisher'),
                            'isVegan': is_vegan_recipe,
                            'isVegetarian': True
                        })
            
            except Exception as e:
                print(f"Error query {query}: {e}")
                continue
        
        return {
            "success": True,
            "count": len(results),
            "recipes": results,
            "source": "Forkify"
        }

@app.get("/api/recipes/{recipe_id}")
async def get_recipe_details(recipe_id: str):
    """Dettagli completi con traduzione"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{FORKIFY_BASE}/{recipe_id}")
            
            if response.status_code == 200:
                data = response.json()
                recipe = data.get('data', {}).get('recipe', {})
                
                if recipe:
                    translated = translate_forkify_recipe(recipe)
                    
                    return {
                        "success": True,
                        "recipe": translated
                    }
            
            raise HTTPException(status_code=404, detail="Recipe not found")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)