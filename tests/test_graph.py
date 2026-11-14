"""
Suíte de testes de Construção e Consistência do Grafo Bipartido.

Verifica a integridade bidirecional das arestas R -> I e I -> R,
o mapeamento de índices invertidos e a consistência da busca em tempo constante.
"""

from implementation.graph import build_recipe_graph
from implementation.models import Dish


def test_build_recipe_graph_empty() -> None:
    """Valida construção do grafo a partir de uma coleção vazia de pratos."""
    grafo = build_recipe_graph(())
    assert len(grafo.dishes_by_id) == 0
    assert len(grafo.recipe_to_ingredients) == 0
    assert len(grafo.ingredient_to_recipes) == 0


def test_build_recipe_graph_single_dish() -> None:
    """Valida grafo com um único prato e seus nós bipartidos."""
    prato = Dish(
        id="d1",
        name="Café Puro",
        category="bebidas",
        recipe=("Ferver água", "Passar no filtro com pó de café"),
        raw_ingredients=("água quente", "pó de café"),
        clean_ingredients=frozenset({"agua", "cafe"}),
    )
    grafo = build_recipe_graph((prato,))

    assert grafo.dishes_by_id["d1"] == prato
    assert grafo.recipe_to_ingredients["d1"] == frozenset({"agua", "cafe"})
    assert grafo.ingredient_to_recipes["agua"] == frozenset({"d1"})
    assert grafo.ingredient_to_recipes["cafe"] == frozenset({"d1"})


def test_build_recipe_graph_inverted_index_overlap() -> None:
    """Verifica agregação de múltiplos pratos compartilhando os mesmos nós de ingredientes."""
    prato1 = Dish(
        id="p1",
        name="Batata Frita",
        category="rapidas",
        recipe=("Cortar batatas", "Fritar no óleo", "Temperar com sal"),
        raw_ingredients=("batata", "óleo", "sal"),
        clean_ingredients=frozenset({"batata", "oleo", "sal"}),
    )
    prato2 = Dish(
        id="p2",
        name="Arroz Branco",
        category="acompanhamentos",
        recipe=("Refogar alho e arroz no óleo", "Cozinhar com água e sal"),
        raw_ingredients=("arroz", "alho", "óleo", "sal"),
        clean_ingredients=frozenset({"arroz", "alho", "oleo", "sal"}),
    )
    grafo = build_recipe_graph((prato1, prato2))

    # O ingrediente compartilhado 'sal' deve apontar para ambos os pratos
    assert grafo.ingredient_to_recipes["sal"] == frozenset({"p1", "p2"})
    assert grafo.ingredient_to_recipes["oleo"] == frozenset({"p1", "p2"})

    # Ingredientes exclusivos devem apontar apenas para o prato correspondente
    assert grafo.ingredient_to_recipes["batata"] == frozenset({"p1"})
    assert grafo.ingredient_to_recipes["arroz"] == frozenset({"p2"})
    assert grafo.ingredient_to_recipes["alho"] == frozenset({"p2"})


def test_build_recipe_graph_bidirectional_consistency() -> None:
    """
    Teorema de consistência do Grafo Bipartido:
    Para todo prato d e todo ingrediente i em R->I(d):
      d DEVE pertencer a I->R(i).
    Para todo ingrediente i e todo prato d em I->R(i):
      i DEVE pertencer a R->I(d).
    """
    pratos = (
        Dish("p1", "Prato 1", "cat1", (), (), frozenset({"a", "b", "c"})),
        Dish("p2", "Prato 2", "cat2", (), (), frozenset({"b", "c", "d"})),
        Dish("p3", "Prato 3", "cat1", (), (), frozenset({"a", "d", "e"})),
    )
    grafo = build_recipe_graph(pratos)

    # Direção R -> I => I -> R
    for dish_id, ings in grafo.recipe_to_ingredients.items():
        for ing in ings:
            assert ing in grafo.ingredient_to_recipes
            assert dish_id in grafo.ingredient_to_recipes[ing]

    # Direção I -> R => R -> I
    for ing, dish_ids in grafo.ingredient_to_recipes.items():
        for dish_id in dish_ids:
            assert dish_id in grafo.recipe_to_ingredients
            assert ing in grafo.recipe_to_ingredients[dish_id]
