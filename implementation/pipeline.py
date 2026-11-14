"""
Pipeline de Recomendação de Pratos (implementation/pipeline.py)
Orquestração puramente funcional de filtragem, mapeamento e ordenação
de receitas viáveis a partir do Grafo Bipartido.
Desenvolvido integralmente com funções lambda e composição de alta ordem.
"""

from implementation.models import Dish, UserPreferences, MatchResult, RecipeGraph
from implementation.engine import (
    prune_allergens,
    calculate_match,
    is_within_tolerance,
    matches_category,
    encontrar_ids_contaminados,
)

# Critério multicritério de ordenação pura:
# 1. Maior percentual de cobertura descrescente (-match_percentage)
# 2. Menor quantidade de ingredientes faltantes crescente (len(missing))
# 3. Nome alfabético como critério determinístico de desempate
criterio_ordenacao = lambda m: (
    -m.match_percentage,
    len(m.missing_ingredients),
    m.dish.name,
)

# Pipeline funcional de recomendação executado via composição encadeada de alta ordem:
# 1. Poda de alérgenos via grafo
# 2. Mapeamento dos nós seguros
# 3. Filtragem por categoria opcional
# 4. Projeção de match e cobertura
# 5. Filtragem por tolerância de faltantes
# 6. Ordenação determinística congelada em tupla imutável
run_recommendation = lambda graph, prefs: tuple(
    sorted(
        filter(
            lambda m: is_within_tolerance(m, prefs.max_missing),
            map(
                lambda d: calculate_match(d, prefs.pantry),
                filter(
                    lambda d: matches_category(d, prefs.category_filter),
                    map(
                        lambda did: graph.dishes_by_id[did],
                        prune_allergens(graph, prefs.allergens),
                    ),
                ),
            ),
        ),
        key=criterio_ordenacao,
    )
)

# Localiza e retorna a tupla imutável de pratos que foram excluídos devido aos alérgenos,
# respeitando opcionalmente o filtro de categoria culinária ativa
obter_pratos_bloqueados = lambda graph, allergens, category_filter=None: tuple(
    filter(
        lambda d: matches_category(d, category_filter),
        map(
            lambda did: graph.dishes_by_id[did],
            encontrar_ids_contaminados(graph, allergens),
        ),
    )
)
