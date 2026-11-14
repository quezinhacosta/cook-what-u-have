"""
Modelos de Dados Imutáveis do Motor Funcional (implementation/models.py)
Estruturas de dados estritamente imutáveis baseadas em NamedTuple.
Construídas sem qualquer uso de declaração imperativa de métodos.
"""

from typing import NamedTuple, Mapping


class Dish(NamedTuple):
    """
    Entidade imutável que representa um prato na base do grafo:
    - id: identificador determinístico único
    - name: título do prato
    - category: categoria culinária canônica
    - recipe: tupla ordenada com os passos de preparo intactos
    - raw_ingredients: ingredientes originais em texto bruto
    - clean_ingredients: conjunto congelado de ingredientes centrais
    """
    id: str
    name: str
    category: str
    recipe: tuple[str, ...]
    raw_ingredients: tuple[str, ...]
    clean_ingredients: frozenset[str]


class UserPreferences(NamedTuple):
    """
    Preferências e restrições imutáveis fornecidas pelo usuário:
    - pantry: conjunto congelado de ingredientes disponíveis em casa
    - allergens: conjunto congelado de ingredientes banidos por alergia
    - max_missing: tolerância máxima de ingredientes faltantes
    - category_filter: filtro opcional de categoria
    """
    pantry: frozenset[str]
    allergens: frozenset[str]
    max_missing: int = 0
    category_filter: str | None = None


class MatchResult(NamedTuple):
    """
    Resultado analítico imutável da correspondência de um prato:
    - dish: o prato analisado
    - match_percentage: percentual de ingredientes disponíveis
    - available_ingredients: ingredientes que o usuário já possui
    - missing_ingredients: ingredientes que precisam ser comprados
    """
    dish: Dish
    match_percentage: float
    available_ingredients: frozenset[str]
    missing_ingredients: frozenset[str]


class RecipeGraph(NamedTuple):
    """
    Representação imutável do Grafo Bipartido de Receitas e Ingredientes:
    - recipe_to_ingredients: mapeamento direto do ID da receita para seus ingredientes
    - ingredient_to_recipes: mapeamento invertido do ingrediente para as receitas que o usam
    - dishes_by_id: índice direto por ID para resgate em tempo constante
    """
    recipe_to_ingredients: Mapping[str, frozenset[str]]
    ingredient_to_recipes: Mapping[str, frozenset[str]]
    dishes_by_id: Mapping[str, Dish]
