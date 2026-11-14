"""
Suíte de testes do Normalizador Funcional de Ingredientes (ingestion/normalizer.py).

Garante que strings culinárias ruidosas da web sejam reduzidas puramente
aos seus termos canônicos centrais sem quantidades, unidades de medida ou modos de preparo.
"""

from ingestion.models import RawRecipe
from ingestion.normalizer import (
    extrair_ingrediente_central,
    normalizar_colecao_ingredientes,
    processar_receita,
    remove_parenteses,
    remove_quantidades_e_fracoes,
    slugify,
    strip_accents,
)


def test_strip_accents() -> None:
    """Valida remoção pura de acentuação gráfica e diacríticos."""
    assert strip_accents("Açúcar refinado") == "Acucar refinado"
    assert strip_accents("Maçã fuji") == "Maca fuji"
    assert strip_accents("Camarão fresco") == "Camarao fresco"
    assert strip_accents("Café coado") == "Cafe coado"


def test_remove_parenteses() -> None:
    """Valida descarte do conteúdo explicativo contido entre parênteses."""
    assert remove_parenteses("1 lata de milho verde (escorrido)").strip() == "1 lata de milho verde"
    assert remove_parenteses("leite (opcional)").strip() == "leite"
    assert remove_parenteses("sal (a gosto)").strip() == "sal"


def test_remove_quantidades_e_fracoes() -> None:
    """Valida eliminação de algarismos decimais, inteiros e caracteres Unicode de fração."""
    assert remove_quantidades_e_fracoes("2 xícaras").strip() == "xícaras"
    assert remove_quantidades_e_fracoes("1/2 colher").strip() == "colher"
    assert remove_quantidades_e_fracoes("½ xícara").strip() == "xícara"


def test_extrair_ingrediente_central_casos_reais() -> None:
    """Testa a extração canônica para uma variedade de ingredientes reais do TudoGostoso."""
    exemplos = [
        ("2 xícaras (chá) de farinha de trigo", "farinha de trigo"),
        ("1 colher de sopa de fermento em pó", "fermento em po"),
        ("500g de carne moída", "carne"),
        ("1 lata de leite condensado", "leite condensado"),
        ("3 dentes de alho picados", "alho"),
        ("sal e pimenta-do-reino a gosto", "sal e pimenta do reino"),
        ("1 cebola grande picada", "cebola"),
        ("1/2 xícara de azeite de oliva", "azeite de oliva"),
        ("2 peitos de frango cozidos e desfiados", "peitos de frango"),
        ("frango cozido e desfiado", "frango"),
    ]

    for raw, esperado in exemplos:
        resultado = extrair_ingrediente_central(raw)
        assert resultado == esperado, f"Esperava '{esperado}' para '{raw}', obteve '{resultado}'"


def test_normalizar_colecao_ingredientes() -> None:
    """Valida normalização e ordenação de coleção de ingredientes."""
    brutos = (
        "2 xícaras de farinha de trigo",
        "1 colher de fermento em pó",
        "2 xícaras de farinha de trigo",  # Duplicado
    )
    resultado = normalizar_colecao_ingredientes(brutos)
    assert resultado == ("farinha de trigo", "fermento em po")
    assert isinstance(resultado, tuple)


def test_slugify() -> None:
    """Valida geração de slugs limpos."""
    assert slugify("Bolo de Cenoura!") == "bolo-de-cenoura"
    assert slugify("Frango com Quiabo & Polenta") == "frango-com-quiabo-polenta"


def test_processar_receita_transformacao_pura() -> None:
    """Valida a projeção funcional completa de RawRecipe para ProcessedRecipe imutável."""
    raw = RawRecipe(
        titulo="Bolo de Cenoura Fofinho",
        tipo="bolos",
        receita=("Bater tudo no liquidificador", "Assar por 40 minutos"),
        ingredientes_originais=(
            "3 cenouras médias raladas",
            "4 ovos",
            "2 xícaras de açúcar",
            "2 xícaras de farinha de trigo",
        ),
        url="https://www.tudogostoso.com.br/receita/123-bolo.html",
    )

    processada = processar_receita(raw, "bolos")

    assert processada.titulo == "Bolo de Cenoura Fofinho"
    assert processada.tipo == "bolos"
    assert len(processada.receita) == 2
    assert len(processada.ingredientes_originais) == 4
    assert "cenoura" in processada.ingredientes_centrais
    assert "ovo" in processada.ingredientes_centrais  # Singularizado
    assert "acucar" in processada.ingredientes_centrais
    assert "farinha de trigo" in processada.ingredientes_centrais
    assert processada.id.startswith("bolos_bolo-de-cenoura-fofinho_")
