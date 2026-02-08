from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Dict
from translator import IngredientTranslator

app = FastAPI(
    title="Italian Recipe API",
    description="API italiana con Forkify (1M+ ricette gratuite)",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FORKIFY_BASE = "https://forkify-api.herokuapp.com/api/v2/recipes"

# ==================== UTILS ====================

def translate_forkify_recipe(recipe: Dict) -> Dict:
    ingredients = []

    for ing in recipe.get("ingredients", []):
        quantity = ing.get("quantity") or ""
        unit = ing.get("unit") or ""
        description = ing.get("description", "")

        measure = f"{quantity} {unit}".strip()

        translated = IngredientTranslator.translateFullIngredient(
            description,
            measure
        )

        ingredients.append({
            "name": translated["name"],
            "measure": translated["measure"],
            "original_name": description,
            "original_measure": measure
        })

    return {
        "id": recipe.get("id"),
        "name": recipe.get("title"),
        "category": "Vegetarian",
        "image": recipe.get("image_url"),
        "ingredients": ingredients,
        "instructions": recipe.get("source_url"),
        "servings": recipe.get("servings"),
        "cookingTime": recipe.get("cooking_time"),
        "publisher": recipe.get("publisher"),
        "isVegan": False,
        "isVegetarian": True,
        "source": "Forkify"
    }


def is_vegetarian_recipe(recipe: Dict) -> bool:
    non_veg = [
        "chicken", "beef", "pork", "fish", "meat", "bacon",
        "turkey", "lamb", "duck", "salmon", "tuna", "shrimp",
        "pollo", "manzo", "maiale", "pesce", "carne"
    ]

    text = (
        recipe.get("title", "").lower() +
        " ".join(i.get("description", "").lower()
                 for i in recipe.get("ingredients", []))
    )

    return not any(k in text for k in non_veg)


def is_vegan_recipe(recipe: Dict) -> bool:
    non_vegan = [
        "egg", "milk", "cheese", "butter", "cream",
        "yogurt", "honey", "uovo", "latte",
        "formaggio", "burro", "panna"
    ]

    text = " ".join(
        i.get("description", "").lower()
        for i in recipe.get("ingredients", [])
    )

    if any(k in text for k in non_vegan):
        return False

    return is_vegetarian_recipe(recipe)

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "🇮🇹 Italian Recipe API",
        "version": "2.1.0",
        "endpoints": [
            "/api/recipes/vegetarian",
            "/api/recipes/vegan",
            "/api/recipes/search?q=pasta",
            "/api/recipes/{id}"
        ]
    }


@app.get("/api/recipes/vegetarian")
async def get_vegetarian_recipes():
    async with httpx.AsyncClient(timeout=30) as client:
        results = []
        seen_ids = set()

        queries = ["vegetarian", "pasta", "salad", "vegetables", "quinoa"]

        for query in queries:
            r = await client.get(f"{FORKIFY_BASE}?search={query}")
            if r.status_code != 200:
                continue

            recipes = r.json().get("data", {}).get("recipes", [])

            for preview in recipes:
                rid = preview["id"]
                if rid in seen_ids:
                    continue

                seen_ids.add(rid)

                detail = await client.get(f"{FORKIFY_BASE}/{rid}")
                if detail.status_code != 200:
                    continue

                recipe = detail.json().get("data", {}).get("recipe", {})
                if not is_vegetarian_recipe(recipe):
                    continue

                translated = translate_forkify_recipe(recipe)
                translated["isVegan"] = is_vegan_recipe(recipe)

                results.append(translated)

                if len(results) >= 30:
                    break

            if len(results) >= 30:
                break

        return {
            "success": True,
            "count": len(results),
            "recipes": results,
            "source": "Forkify"
        }


@app.get("/api/recipes/vegan")
async def get_vegan_recipes():
    async with httpx.AsyncClient(timeout=30) as client:
        results = []
        seen_ids = set()

        queries = ["vegan", "plant-based", "tofu", "chickpea"]

        for query in queries:
            r = await client.get(f"{FORKIFY_BASE}?search={query}")
            if r.status_code != 200:
                continue

            recipes = r.json().get("data", {}).get("recipes", [])

            for preview in recipes:
                rid = preview["id"]
                if rid in seen_ids:
                    continue

                seen_ids.add(rid)

                detail = await client.get(f"{FORKIFY_BASE}/{rid}")
                if detail.status_code != 200:
                    continue

                recipe = detail.json().get("data", {}).get("recipe", {})
                if not is_vegan_recipe(recipe):
                    continue

                translated = translate_forkify_recipe(recipe)
                translated["isVegan"] = True
                translated["isVegetarian"] = True

                results.append(translated)

                if len(results) >= 30:
                    break

            if len(results) >= 30:
                break

        return {
            "success": True,
            "count": len(results),
            "recipes": results,
            "source": "Forkify"
        }


@app.get("/api/recipes/search")
async def search_recipes(q: str):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{FORKIFY_BASE}?search={q}")
        if r.status_code != 200:
            raise HTTPException(500, "Forkify error")

        results = []
        seen_ids = set()

        for preview in r.json().get("data", {}).get("recipes", [])[:20]:
            rid = preview["id"]
            if rid in seen_ids:
                continue

            seen_ids.add(rid)

            detail = await client.get(f"{FORKIFY_BASE}/{rid}")
            if detail.status_code != 200:
                continue

            recipe = detail.json().get("data", {}).get("recipe", {})
            if not is_vegetarian_recipe(recipe):
                continue

            translated = translate_forkify_recipe(recipe)
            translated["isVegan"] = is_vegan_recipe(recipe)

            results.append(translated)

        return {
            "success": True,
            "count": len(results),
            "recipes": results,
            "source": "Forkify"
        }


@app.get("/api/recipes/{recipe_id}")
async def get_recipe_details(recipe_id: str):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{FORKIFY_BASE}/{recipe_id}")
        if r.status_code != 200:
            raise HTTPException(404, "Recipe not found")

        recipe = r.json().get("data", {}).get("recipe", {})
        translated = translate_forkify_recipe(recipe)
        translated["isVegan"] = is_vegan_recipe(recipe)
        translated["isVegetarian"] = is_vegetarian_recipe(recipe)

        return {"success": True, "recipe": translated}
