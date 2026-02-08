from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import List, Dict, Optional
from translator import IngredientTranslator
import asyncio

app = FastAPI(
    title="Italian Recipe API",
    description="API italiana con Forkify (1M+ ricette gratuite)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CONFIGURAZIONE API ====================

FORKIFY_BASE = "https://forkify-api.herokuapp.com/api/v2/recipes"

# ==================== TRADUZIONE RICETTE ====================

def translate_forkify_recipe(recipe: Dict) -> Dict:
    """Traduce ricetta da Forkify"""
    ingredients = []
    
    for ing in recipe.get('ingredients', []):
        # Forkify format: {quantity, unit, description}
        quantity = ing.get('quantity') or ''
        unit = ing.get('unit') or ''
        description = ing.get('description', '')
        
        # Combina quantity + unit
        if quantity:
            measure = f"{quantity} {unit}".strip()
        else:
            measure = unit
        
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
        'category': 'Vegetarian',  # Forkify non ha categorie native
        'image': recipe.get('image_url'),
        'ingredients': ingredients,
        'instructions': recipe.get('source_url'),  # Link ricetta originale
        'servings': recipe.get('servings'),
        'cookingTime': recipe.get('cooking_time'),
        'publisher': recipe.get('publisher'),
        'isVegan': False,  # Determiniamo dal contenuto
        'isVegetarian': True,
        'source': 'Forkify'
    }

def is_vegetarian_recipe(recipe: Dict) -> bool:
    """Controlla se ricetta è vegetariana analizzando ingredienti"""
    non_veg_keywords = [
        'chicken', 'beef', 'pork', 'fish', 'meat', 'bacon',
        'turkey', 'lamb', 'duck', 'salmon', 'tuna', 'shrimp',
        'pollo', 'manzo', 'maiale', 'pesce', 'carne'
    ]
    
    ingredients_text = ' '.join([
        ing.get('description', '').lower() 
        for ing in recipe.get('ingredients', [])
    ])
    
    title = recipe.get('title', '').lower()
    
    # Se contiene parole non-veg, skip
    for keyword in non_veg_keywords:
        if keyword in ingredients_text or keyword in title:
            return False
    
    return True

def is_vegan_recipe(recipe: Dict) -> bool:
    """Controlla se ricetta è vegana"""
    non_vegan_keywords = [
        'egg', 'milk', 'cheese', 'butter', 'cream', 'yogurt',
        'honey', 'uovo', 'latte', 'formaggio', 'burro', 'panna'
    ]
    
    ingredients_text = ' '.join([
        ing.get('description', '').lower() 
        for ing in recipe.get('ingredients', [])
    ])
    
    for keyword in non_vegan_keywords:
        if keyword in ingredients_text:
            return False
    
    return is_vegetarian_recipe(recipe)

# ==================== ENDPOINT ====================

@app.get("/")
async def root():
    return {
        "message": "🇮🇹 Italian Recipe API v2.0",
        "version": "2.0.0",
        "source": "Forkify API (1M+ recipes)",
        "features": [
            "Unlimited requests",
            "Beautiful images",
            "Italian translation",
            "Vegetarian/Vegan filtering"
        ],
        "endpoints": {
            "vegetarian": "/api/recipes/vegetarian",
            "vegan": "/api/recipes/vegan",
            "search": "/api/recipes/search?q=pasta",
            "details": "/api/recipes/{id}"
        }
    }

@app.get("/api/recipes/vegetarian")
async def get_vegetarian_recipes():
    """
    Ricette vegetariane da Forkify
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = []
        
        # Cerca varie query vegetariane
        queries = ['vegetarian', 'pasta', 'salad', 'vegetables', 'quinoa']
        
        for query in queries:
            try:
                response = await client.get(f"{FORKIFY_BASE}?search={query}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get('data', {}).get('recipes', [])
                    
                    # Filtra solo vegetariane
                    for recipe_preview in recipes[:5]:  # Prime 5 per query
                        # Fetch dettagli completi
                        detail_response = await client.get(
                            f"{FORKIFY_BASE}/{recipe_preview['id']}"
                        )
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            recipe_full = detail_data.get('data', {}).get('recipe', {})
                            
                            if is_vegetarian_recipe(recipe_full):
                                translated = translate_forkify_recipe(recipe_full)
                                translated['isVegan'] = is_vegan_recipe(recipe_full)
                                results.append(translated)
                                
                                if len(results) >= 30:  # Max 30 ricette
                                    break
                
                if len(results) >= 30:
                    break
                    
            except Exception as e:
                print(f"Error fetching {query}: {e}")
                continue
        
        return {
            "success": True,
            "count": len(results),
            "recipes": results,
            "source": "Forkify"
        }

@app.get("/api/recipes/vegan")
async def get_vegan_recipes():
    """
    Ricette vegane da Forkify
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        results = []
        
        queries = ['vegan', 'plant-based', 'tofu', 'chickpea']
        
        for query in queries:
            try:
                response = await client.get(f"{FORKIFY_BASE}?search={query}")
                
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get('data', {}).get('recipes', [])
                    
                    for recipe_preview in recipes[:8]:
                        detail_response = await client.get(
                            f"{FORKIFY_BASE}/{recipe_preview['id']}"
                        )
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            recipe_full = detail_data.get('data', {}).get('recipe', {})
                            
                            if is_vegan_recipe(recipe_full):
                                translated = translate_forkify_recipe(recipe_full)
                                translated['isVegan'] = True
                                translated['isVegetarian'] = True
                                results.append(translated)
                                
                                if len(results) >= 30:
                                    break
                
                if len(results) >= 30:
                    break
                    
            except Exception as e:
                print(f"Error fetching vegan {query}: {e}")
                continue
        
        return {
            "success": True,
            "count": len(results),
            "recipes": results,
            "source": "Forkify"
        }

@app.get("/api/recipes/search")
async def search_recipes(q: str):
    """
    Cerca ricette per nome
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{FORKIFY_BASE}?search={q}")
            
            if response.status_code == 200:
                data = response.json()
                recipes = data.get('data', {}).get('recipes', [])
                
                results = []
                
                # Fetch dettagli per ogni ricetta
                for recipe_preview in recipes[:20]:  # Max 20
                    try:
                        detail_response = await client.get(
                            f"{FORKIFY_BASE}/{recipe_preview['id']}"
                        )
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            recipe_full = detail_data.get('data', {}).get('recipe', {})
                            
                            # Filtra solo vegetariane
                            if is_vegetarian_recipe(recipe_full):
                                translated = translate_forkify_recipe(recipe_full)
                                translated['isVegan'] = is_vegan_recipe(recipe_full)
                                results.append(translated)
                    except:
                        continue
                
                return {
                    "success": True,
                    "count": len(results),
                    "recipes": results,
                    "source": "Forkify"
                }
            else:
                raise HTTPException(status_code=500, detail="Forkify API error")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recipes/{recipe_id}")
async def get_recipe_details(recipe_id: str):
    """
    Dettagli ricetta
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{FORKIFY_BASE}/{recipe_id}")
            
            if response.status_code == 200:
                data = response.json()
                recipe = data.get('data', {}).get('recipe', {})
                
                if recipe:
                    translated = translate_forkify_recipe(recipe)
                    translated['isVegan'] = is_vegan_recipe(recipe)
                    translated['isVegetarian'] = is_vegetarian_recipe(recipe)
                    
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