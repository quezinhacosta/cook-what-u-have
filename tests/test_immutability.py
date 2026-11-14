"""
Suíte de testes de Imutabilidade Estrita.

Verifica que todas as estruturas de dados do domínio (Dish, UserPreferences, MatchResult, RecipeGraph)
e coleções subjacentes (frozenset, tuple) são totalmente imutáveis e rejeitam qualquer mutação.
"""

import pytest

from implementation.models import Dish, MatchResult, RecipeGraph, UserPreferences


def test_dish_immutability() -> None:
    """Valida que instâncias de Dish não permitem reatribuição de atributos."""
    prato = Dish(
        id="prato_teste_1",
        name="Omelete de Ervas",
        category="rapidas",
        recipe=("Bater os ovos", "Temperar com ervas", "Fritar na manteiga"),
        raw_ingredients=("2 ovos", "1 colher de manteiga", "ervas finas a gosto"),
        clean_ingredients=frozenset({"ovos", "manteiga", "ervas finas"}),
    )

    with pytest.raises(AttributeError):
        prato.name = "Novo Nome"  # type: ignore[misc]

    with pytest.raises(AttributeError):
        prato.clean_ingredients = frozenset()  # type: ignore[misc]

    with pytest.raises(AttributeError):
        prato.id = "outro_id"  # type: ignore[misc]


def test_dish_nested_collections_are_immutable() -> None:
    """Garante que as coleções internas de Dish são frozenset e tuple (sem append/add)."""
    prato = Dish(
        id="prato_teste_2",
        name="Salada Simples",
        category="saladas",
        recipe=("Lavar as folhas", "Temperar com azeite"),
        raw_ingredients=("1 maço de alface", "2 colheres de azeite"),
        clean_ingredients=frozenset({"alface", "azeite"}),
    )

    assert isinstance(prato.clean_ingredients, frozenset)
    assert not hasattr(prato.clean_ingredients, "add")
    assert not hasattr(prato.clean_ingredients, "remove")

    assert isinstance(prato.recipe, tuple)
    assert not hasattr(prato.recipe, "append")
    assert not hasattr(prato.recipe, "extend")

    assert isinstance(prato.raw_ingredients, tuple)
    assert not hasattr(prato.raw_ingredients, "append")


def test_user_preferences_immutability() -> None:
    """Valida que UserPreferences rejeita alterações em tempo de execução."""
    prefs = UserPreferences(
        pantry=frozenset({"arroz", "feijao"}),
        allergens=frozenset({"camarao", "leite"}),
        max_missing=2,
        category_filter="carnes",
    )

    with pytest.raises(AttributeError):
        prefs.max_missing = 5  # type: ignore[misc]

    with pytest.raises(AttributeError):
        prefs.category_filter = "massas"  # type: ignore[misc]

    assert isinstance(prefs.pantry, frozenset)
    assert isinstance(prefs.allergens, frozenset)


def test_match_result_immutability() -> None:
    """Valida que MatchResult não pode ter seus escores recalculados por mutação externa."""
    prato = Dish(
        id="prato_3",
        name="Arroz de Couve",
        category="legumes",
        recipe=("Refogar a couve", "Misturar ao arroz"),
        raw_ingredients=("couve", "arroz"),
        clean_ingredients=frozenset({"couve", "arroz"}),
    )
    resultado = MatchResult(
        dish=prato,
        match_percentage=50.0,
        available_ingredients=frozenset({"arroz"}),
        missing_ingredients=frozenset({"couve"}),
    )

    with pytest.raises(AttributeError):
        resultado.match_percentage = 100.0  # type: ignore[misc]

    with pytest.raises(AttributeError):
        resultado.missing_ingredients = frozenset()  # type: ignore[misc]


def test_recipe_graph_immutability() -> None:
    """Valida que a estrutura do RecipeGraph é congelada e não permite sobrescrita de índices."""
    grafo = RecipeGraph(
        recipe_to_ingredients={},
        ingredient_to_recipes={},
        dishes_by_id={},
    )

    with pytest.raises(AttributeError):
        grafo.dishes_by_id = {}  # type: ignore[misc]

    with pytest.raises(AttributeError):
        grafo.recipe_to_ingredients = {}  # type: ignore[misc]

    with pytest.raises(AttributeError):
        grafo.ingredient_to_recipes = {}  # type: ignore[misc]
