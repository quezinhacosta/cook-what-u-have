"""
Suíte de testes de Interface, Usabilidade e Paginação (tests/test_cli_and_ux.py).

Verifica o mapeamento e resolução declarativa de categorias, a formatação
completa dos detalhes da receita (passo a passo) e a geração de URLs paginadas.
"""

from implementation.models import Dish, MatchResult
from ingestion.parser import gerar_url_pagina
from interface.cli import resolver_categoria_input
from interface.formatter import (
    CATEGORIAS_DISPONIVEIS,
    formatar_detalhes_receita,
    formatar_menu_categorias,
)


def test_gerar_url_pagina_paginacao() -> None:
    """Valida geração funcional pura de URLs para categorias paginadas."""
    base = "https://www.tudogostoso.com.br/categorias/1009-aves"

    assert gerar_url_pagina(base, 1) == base
    assert gerar_url_pagina(base, 0) == base
    assert gerar_url_pagina(base, 2) == f"{base}?page=2"
    assert gerar_url_pagina(base, 5) == f"{base}?page=5"


def test_formatar_menu_categorias() -> None:
    """Garante que todas as 8 categorias são exibidas de forma clara e numerada no menu."""
    menu = formatar_menu_categorias()
    assert all(map(lambda pair: f"[{pair[0] + 1}] {pair[1].title()}" in menu, enumerate(CATEGORIAS_DISPONIVEIS)))
    assert "[0] Todas as categorias" in menu


def test_resolver_categoria_input_por_numero() -> None:
    """Verifica resolução de categorias por índice numérico."""
    assert resolver_categoria_input("1") == "aves"
    assert resolver_categoria_input("2") == "bolos e tortas"
    assert resolver_categoria_input("3") == "carnes"
    assert resolver_categoria_input("4") == "doces e sobremesas"
    assert resolver_categoria_input("5") == "massas"
    assert resolver_categoria_input("6") == "peixes e frutos do mar"
    assert resolver_categoria_input("7") == "saladas e molhos"
    assert resolver_categoria_input("8") == "sopas"


def test_resolver_categoria_input_todas_e_vazias() -> None:
    """Garante que 0, strings vazias ou palavras-chave retornam None (busca global)."""
    assert resolver_categoria_input("0") is None
    assert resolver_categoria_input("") is None
    assert resolver_categoria_input("   ") is None
    assert resolver_categoria_input("todas") is None
    assert resolver_categoria_input("todos") is None


def test_resolver_categoria_input_textual() -> None:
    """Verifica resolução quando o usuário digita diretamente o nome da categoria."""
    assert resolver_categoria_input("aves") == "aves"
    assert resolver_categoria_input("MASSAS") == "massas"
    assert resolver_categoria_input("  Carnes  ") == "carnes"


def test_formatar_detalhes_receita_completo() -> None:
    """Valida a projeção visual da receita com ingredientes originais e modo de preparo."""
    dish = Dish(
        id="d1",
        name="Lasanha à Bolonhesa",
        category="massas",
        recipe=(
            "Cozinhar as folhas de massa",
            "Fazer o molho de carne moída com tomate",
            "Montar em camadas intercalando queijo e presunto",
            "Levar ao forno por 25 minutos a 180°C",
        ),
        raw_ingredients=(
            "500g de massa para lasanha",
            "500g de carne moída",
            "2 latas de molho de tomate",
            "300g de queijo mussarela fatiado",
        ),
        clean_ingredients=frozenset({"massa", "carne", "molho de tomate", "mussarela"}),
    )

    match = MatchResult(
        dish=dish,
        match_percentage=75.0,
        available_ingredients=frozenset({"massa", "carne", "molho de tomate"}),
        missing_ingredients=frozenset({"mussarela"}),
    )

    detalhe = formatar_detalhes_receita(match)

    # Cabeçalho
    assert "DETALHES DA RECEITA: LASANHA À BOLONHESA" in detalhe
    assert "Categoria: Massas" in detalhe
    assert "75.0%" in detalhe

    # Ingredientes com quantidades originais
    assert "500g de massa para lasanha" in detalhe
    assert "300g de queijo mussarela fatiado" in detalhe

    # Passo a passo numerado
    assert "[1] Cozinhar as folhas de massa" in detalhe
    assert "[4] Levar ao forno por 25 minutos a 180°C" in detalhe

    # Faltantes
    assert "Falta comprar (1 itens): [mussarela]" in detalhe
