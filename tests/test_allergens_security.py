"""
Suíte de testes de Segurança Alimentar e Poda de Alérgenos.

Valida a política de tolerância zero contra alérgenos no Grafo Bipartido,
garantindo detecção por substring, termos compostos e exclusão de receitas contaminadas.
"""

from implementation.engine import (
    encontrar_chaves_alergenas,
    encontrar_ids_contaminados,
    prune_allergens,
)
from implementation.graph import build_recipe_graph
from implementation.models import Dish


def criar_grafo_seguranca() -> tuple[Dish, Dish, Dish, any]:  # type: ignore[valid-type]
    prato_mar = Dish(
        id="prato_mar",
        name="Bobó de Camarão",
        category="peixes",
        recipe=("Cozinhar aipim", "Adicionar camarão limpo", "Finalizar com azeite de dendê"),
        raw_ingredients=("500g de camarão limpo", "1kg de aipim", "azeite de dendê"),
        clean_ingredients=frozenset({"camarao limpo", "aipim", "azeite de dende"}),
    )
    prato_doce = Dish(
        id="prato_doce",
        name="Pudim de Leite",
        category="sobremesas",
        recipe=("Bater leite condensado com ovos", "Assar em banho-maria"),
        raw_ingredients=("1 lata de leite condensado", "3 ovos", "1 xícara de leite integral"),
        clean_ingredients=frozenset({"leite condensado", "ovos", "leite integral"}),
    )
    prato_seguro = Dish(
        id="prato_seguro",
        name="Arroz de Frango com Legumes",
        category="aves",
        recipe=("Refogar peito de frango", "Adicionar arroz e cenoura"),
        raw_ingredients=("500g de peito de frango", "2 xícaras de arroz", "cenoura"),
        clean_ingredients=frozenset({"peito de frango", "arroz", "cenoura"}),
    )
    grafo = build_recipe_graph((prato_mar, prato_doce, prato_seguro))
    return prato_mar, prato_doce, prato_seguro, grafo


def test_encontrar_chaves_alergenas_compostos() -> None:
    """Valida detecção de chaves alérgenas mesmo quando o termo está contido em expressões compostas."""
    _, _, _, grafo = criar_grafo_seguranca()

    chaves_camarao = encontrar_chaves_alergenas(grafo, frozenset({"camarao"}))
    assert "camarao limpo" in chaves_camarao

    chaves_leite = encontrar_chaves_alergenas(grafo, frozenset({"leite"}))
    assert "leite condensado" in chaves_leite
    assert "leite integral" in chaves_leite

    chaves_inexistentes = encontrar_chaves_alergenas(grafo, frozenset({"amendoim"}))
    assert len(chaves_inexistentes) == 0


def test_encontrar_ids_contaminados_tolerancia_zero() -> None:
    """Garante que pratos com qualquer traço de ingrediente alérgeno são marcados como contaminados."""
    _, _, _, grafo = criar_grafo_seguranca()

    contaminados_camarao = encontrar_ids_contaminados(grafo, frozenset({"camarao"}))
    assert "prato_mar" in contaminados_camarao
    assert "prato_doce" not in contaminados_camarao
    assert "prato_seguro" not in contaminados_camarao

    contaminados_leite = encontrar_ids_contaminados(grafo, frozenset({"leite"}))
    assert "prato_doce" in contaminados_leite
    assert "prato_mar" not in contaminados_leite
    assert "prato_seguro" not in contaminados_leite


def test_encontrar_ids_contaminados_multiplos_alergenos() -> None:
    """Verifica contaminação cruzada para conjunto de múltiplos alérgenos simultâneos."""
    _, _, _, grafo = criar_grafo_seguranca()

    contaminados = encontrar_ids_contaminados(grafo, frozenset({"camarao", "leite"}))
    assert contaminados == frozenset({"prato_mar", "prato_doce"})


def test_encontrar_ids_contaminados_sem_alergenos() -> None:
    """Quando o conjunto de alérgenos for vazio, nenhum prato deve ser marcado como contaminado."""
    _, _, _, grafo = criar_grafo_seguranca()

    contaminados = encontrar_ids_contaminados(grafo, frozenset())
    assert contaminados == frozenset()


def test_prune_allergens_retorna_apenas_receitas_puras() -> None:
    """Verifica que prune_allergens remove todos os pratos contaminados do conjunto elegível."""
    _, _, _, grafo = criar_grafo_seguranca()

    receitas_seguras = prune_allergens(grafo, frozenset({"camarao", "leite"}))
    assert receitas_seguras == frozenset({"prato_seguro"})

    receitas_sem_filtro = prune_allergens(grafo, frozenset())
    assert receitas_sem_filtro == frozenset({"prato_mar", "prato_doce", "prato_seguro"})
