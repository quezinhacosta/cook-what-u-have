"""
Motor Matemático e Teoria dos Conjuntos (implementation/engine.py)
Operações puras de poda de alérgenos no grafo, cálculo de interseção,
diferença de conjuntos e tolerância de faltantes.
Implementado integralmente com funções lambda e expressões de ordem superior.
"""

from implementation.models import Dish, MatchResult, RecipeGraph

# Localiza todos os IDs de pratos contaminados a partir das arestas invertidas dos alérgenos
encontrar_ids_contaminados = lambda graph, allergens: (
    frozenset().union(*(graph.ingredient_to_recipes.get(a, frozenset()) for a in allergens))
    if allergens else frozenset()
)

# Poda determinística no grafo: subtrai os nós contaminados do conjunto total de receitas
prune_allergens = lambda graph, allergens: (
    frozenset(graph.recipe_to_ingredients.keys()) - encontrar_ids_contaminados(graph, allergens)
)

# Calcula o percentual de correspondência a partir das cardinalidades dos conjuntos
calcular_percentual_cobertura = lambda qtd_presentes, qtd_total: (
    round((qtd_presentes / qtd_total) * 100.0, 2) if qtd_total > 0 else 0.0
)

# Realiza a projeção analítica de viabilidade de um prato contra a despensa do usuário
calculate_match = lambda dish, pantry: MatchResult(
    dish=dish,
    match_percentage=calcular_percentual_cobertura(
        len(dish.clean_ingredients & pantry),
        len(dish.clean_ingredients)
    ),
    available_ingredients=dish.clean_ingredients & pantry,
    missing_ingredients=dish.clean_ingredients - pantry,
)

# Predicado que verifica se a quantidade de itens faltantes respeita o teto aceito
is_within_tolerance = lambda match, max_missing: (
    len(match.missing_ingredients) <= max_missing
)

# Predicado que verifica a pertinência da receita ao filtro opcional de categoria
matches_category = lambda dish, category_filter: (
    True if not category_filter else category_filter.strip().lower() in dish.category.lower()
)
