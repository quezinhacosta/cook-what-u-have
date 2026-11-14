"""
Pacote do Motor Funcional do Grafo (implementation/__init__.py)
Exporta modelos imutáveis, construtor de grafo e pipeline de recomendação.
"""

from implementation.engine import (
    calculate_match,
    encontrar_chaves_alergenas,
    encontrar_ids_contaminados,
    ingrediente_coberto,
    is_within_tolerance,
    matches_category,
    obter_ingredientes_disponiveis,
    prune_allergens,
)
from implementation.graph import build_recipe_graph
from implementation.loader import dict_to_dish, load_dishes_from_records
from implementation.models import Dish, MatchResult, RecipeGraph, UserPreferences
from implementation.pipeline import obter_pratos_bloqueados, run_recommendation

__all__ = (
    "Dish",
    "MatchResult",
    "RecipeGraph",
    "UserPreferences",
    "build_recipe_graph",
    "calculate_match",
    "dict_to_dish",
    "encontrar_chaves_alergenas",
    "encontrar_ids_contaminados",
    "ingrediente_coberto",
    "is_within_tolerance",
    "load_dishes_from_records",
    "matches_category",
    "obter_ingredientes_disponiveis",
    "obter_pratos_bloqueados",
    "prune_allergens",
    "run_recommendation",
)
