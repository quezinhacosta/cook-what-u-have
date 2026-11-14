"""
Motor Matemático e Teoria dos Conjuntos (implementation/engine.py)
Operações puras de poda de alérgenos no grafo, cálculo de interseção,
diferença de conjuntos e tolerância de faltantes.
Implementado integralmente com funções lambda e expressões de ordem superior.
"""

from implementation.models import Dish, MatchResult, RecipeGraph

# Localiza todas as chaves de ingredientes no grafo que contêm o termo alérgeno
encontrar_chaves_alergenas = lambda graph, allergens: tuple(
    filter(
        lambda ing_key: any(a in ing_key for a in allergens),
        graph.ingredient_to_recipes.keys(),
    )
)

# Localiza todos os IDs de pratos contaminados a partir das arestas invertidas dos alérgenos
encontrar_ids_contaminados = lambda graph, allergens: (
    frozenset().union(*(
        graph.ingredient_to_recipes.get(chave, frozenset())
        for chave in encontrar_chaves_alergenas(graph, allergens)
    ))
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

# Predicado que verifica se um ingrediente exigido é satisfeito pela despensa
ingrediente_coberto = lambda ing, pantry: (
    ing in pantry or any(
        (p in ing or ing in p)
        for p in pantry
        if len(p) >= 3 and len(ing) >= 3
    )
)

# Filtra o subconjunto congelado de ingredientes do prato que estão disponíveis
obter_ingredientes_disponiveis = lambda clean_ingredients, pantry: frozenset(
    filter(lambda ing: ingrediente_coberto(ing, pantry), clean_ingredients)
)

# Realiza a projeção analítica de viabilidade de um prato contra a despensa do usuário
calculate_match = lambda dish, pantry: (
    lambda disponiveis: MatchResult(
        dish=dish,
        match_percentage=calcular_percentual_cobertura(
            len(disponiveis),
            len(dish.clean_ingredients),
        ),
        available_ingredients=disponiveis,
        missing_ingredients=dish.clean_ingredients - disponiveis,
    )
)(obter_ingredientes_disponiveis(dish.clean_ingredients, pantry))

# Predicado que verifica se a quantidade de itens faltantes respeita o teto aceito
is_within_tolerance = lambda match, max_missing: (
    len(match.missing_ingredients) <= max_missing
)

# Predicado que verifica a pertinência da receita ao filtro opcional de categoria
matches_category = lambda dish, category_filter: (
    True if not category_filter else category_filter.strip().lower() in dish.category.lower()
)
