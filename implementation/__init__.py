"""
Pacote do Motor Funcional do Grafo (implementation/__init__.py)
Exporta modelos imutáveis, construtor de grafo e pipeline de recomendação.
"""

from implementation.models import Dish, UserPreferences, MatchResult, RecipeGraph
from implementation.graph import build_recipe_graph
from implementation.engine import (
    prune_allergens,
    calculate_match,
    is_within_tolerance,
    matches_category,
    encontrar_ids_contaminados,
    encontrar_chaves_alergenas,
    ingrediente_coberto,
    obter_ingredientes_disponiveis,
)
from implementation.pipeline import run_recommendation, obter_pratos_bloqueados
from implementation.loader import dict_to_dish, load_dishes_from_records

__all__ = (
    "Dish",
    "UserPreferences",
    "MatchResult",
    "RecipeGraph",
    "build_recipe_graph",
    "prune_allergens",
    "calculate_match",
    "is_within_tolerance",
    "matches_category",
    "encontrar_ids_contaminados",
    "encontrar_chaves_alergenas",
    "ingrediente_coberto",
    "obter_ingredientes_disponiveis",
    "run_recommendation",
    "obter_pratos_bloqueados",
    "dict_to_dish",
    "load_dishes_from_records",
)
