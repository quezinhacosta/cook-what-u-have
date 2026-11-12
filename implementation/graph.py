"""
Construtor Funcional do Grafo Bipartido (implementation/graph.py)
Estrutura puramente funcional para montagem das adjacências R -> I e I -> R.
Desenvolvido estritamente com lambdas, map, filter e frozenset, sem instrucoes imperativas.
"""

from typing import Mapping
from implementation.models import Dish, RecipeGraph

# Extrai o conjunto consolidado de todos os ingredientes centrais de uma coleção de pratos
extrair_todos_ingredientes = lambda pratos: (
    frozenset().union(*(p.clean_ingredients for p in pratos)) if pratos else frozenset()
)

# Constrói o mapeamento invertido (Ingrediente -> frozenset de IDs dos pratos que o contêm)
construir_adjacencia_invertida = lambda pratos, todos_ingredientes: dict(
    map(
        lambda ing: (
            ing,
            frozenset(map(lambda p: p.id, filter(lambda p: ing in p.clean_ingredients, pratos)))
        ),
        todos_ingredientes
    )
)

# Constrói o Grafo Bipartido completo imutável a partir de uma tupla de Dish
build_recipe_graph = lambda pratos: RecipeGraph(
    recipe_to_ingredients=dict(map(lambda p: (p.id, p.clean_ingredients), pratos)),
    ingredient_to_recipes=construir_adjacencia_invertida(
        pratos,
        extrair_todos_ingredientes(pratos)
    ),
    dishes_by_id=dict(map(lambda p: (p.id, p), pratos))
)
