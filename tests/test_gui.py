"""
Testes Unitários da Interface Gráfica Neo-Brutalista (tests/test_gui.py)

Valida tokens de estilo, dimensões de viewport smartphone, fábricas de controles,
formatação e renderização declarativa das 3 views (Busca, Resultados, Detalhes),
além de garantir estritamente a ausência total de emojis.
"""

import re
from typing import Any

import flet as ft

from implementation.models import Dish, MatchResult
from interface.gui import (
    GUIState,
    build_detail_view,
    build_results_view,
    build_search_view,
    formatar_lista_termos,
)
from interface.gui_theme import (
    COLOR_BG,
    COLOR_BLACK,
    COLOR_CORAL,
    COLOR_DESK,
    COLOR_GREEN,
    COLOR_LILAC,
    COLOR_ORANGE,
    COLOR_WHITE,
    COLOR_YELLOW,
    DESKTOP_WINDOW_HEIGHT,
    DESKTOP_WINDOW_WIDTH,
    PHONE_HEIGHT,
    PHONE_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    build_phone_home_indicator,
    build_phone_status_bar,
    neo_badge,
    neo_border,
    neo_button,
    neo_card,
    neo_chip,
    neo_icon_button,
    neo_shadow,
)

EMOJI_PATTERN = re.compile(
    r"[\U0001F600-\U0001F64F]|"
    r"[\U0001F300-\U0001F5FF]|"
    r"[\U0001F680-\U0001F6FF]|"
    r"[\U0001F1E0-\U0001F1FF]|"
    r"[\U00002702-\U000027B0]|"
    r"[\U000024C2-\U0001F251]|"
    r"[\U0001F900-\U0001F9FF]|"
    r"[\U0001FA70-\U0001FAFF]"
)


def _criar_prato_mock(
    dish_id: str = "mock-1",
    name: str = "Bolo de Chocolate",
    category: str = "bolos e tortas",
    raw_ingredients: tuple[str, ...] = ("2 ovos", "1 xícara de leite", "200g chocolate"),
    clean_ingredients: frozenset[str] = frozenset({"ovo", "leite", "chocolate"}),
    recipe: tuple[str, ...] = ("Bata os ovos com o leite.", "Asse por 30 minutos."),
) -> Dish:
    """Cria uma instância de Dish para testes de interface."""
    return Dish(
        id=dish_id,
        name=name,
        category=category,
        recipe=recipe,
        raw_ingredients=raw_ingredients,
        clean_ingredients=clean_ingredients,
    )


def test_theme_tokens_and_dimensions() -> None:
    """Verifica se os tokens de design do Neo-Brutalism e viewport estão corretos."""
    assert PHONE_WIDTH == 390
    assert PHONE_HEIGHT == 750
    assert WINDOW_WIDTH == 390
    assert WINDOW_HEIGHT == 750
    assert DESKTOP_WINDOW_WIDTH == 430
    assert DESKTOP_WINDOW_HEIGHT == 810
    assert COLOR_BG == "#FAF7F2"
    assert COLOR_BLACK == "#111111"
    assert COLOR_WHITE == "#FFFFFF"
    assert COLOR_YELLOW == "#FFD166"
    assert COLOR_GREEN == "#B5E48C"
    assert COLOR_LILAC == "#CDB4DB"
    assert COLOR_CORAL == "#FF8FA3"
    assert COLOR_ORANGE == "#F4A261"
    assert COLOR_DESK == "#E8E2D8"


def test_phone_mockup_components() -> None:
    """Verifica a montagem dos componentes de hardware simulados do smartphone."""
    status_bar = build_phone_status_bar()
    assert isinstance(status_bar, ft.Container)
    assert status_bar.height == 30

    home_bar = build_phone_home_indicator()
    assert isinstance(home_bar, ft.Container)
    assert home_bar.width == 120
    assert home_bar.height == 5


def test_neo_primitives_construction() -> None:
    """Valida a construção de bordas pretas sólidas e sombras duras sem desfoque."""
    border = neo_border(2, COLOR_BLACK)
    assert border.top.width == 2
    assert border.top.color == COLOR_BLACK

    shadow = neo_shadow(4.0, 4.0, COLOR_BLACK)
    assert shadow.spread_radius == 0.0
    assert shadow.blur_radius == 0.0
    assert shadow.color == COLOR_BLACK
    assert isinstance(shadow.offset, ft.Offset)
    assert shadow.offset.x == 4.0
    assert shadow.offset.y == 4.0


def test_neo_factories_controls() -> None:
    """Testa se as fábricas de componentes Neo-Brutalistas retornam containers válidos."""
    card = neo_card(content=ft.Text("Conteúdo"), bgcolor=COLOR_WHITE)
    assert isinstance(card, ft.Container)
    assert card.bgcolor == COLOR_WHITE

    badge = neo_badge("100% [3/3]", bgcolor=COLOR_GREEN)
    assert isinstance(badge, ft.Container)
    assert badge.bgcolor == COLOR_GREEN

    btn = neo_button("BUSCAR", on_click=lambda _: None, bgcolor=COLOR_YELLOW)
    assert isinstance(btn, ft.Container)
    assert btn.bgcolor == COLOR_YELLOW

    chip_selected = neo_chip("Aves", selected=True, on_click=lambda _: None)
    assert isinstance(chip_selected, ft.Container)
    assert chip_selected.bgcolor == COLOR_ORANGE

    chip_unselected = neo_chip("Carnes", selected=False, on_click=lambda _: None)
    assert isinstance(chip_unselected, ft.Container)
    assert chip_unselected.bgcolor == COLOR_WHITE

    icon_btn = neo_icon_button(icon=ft.Icons.ARROW_BACK, on_click=lambda _: None)
    assert isinstance(icon_btn, ft.Container)


def test_formatar_lista_termos() -> None:
    """Verifica ordenação alfabética e tratamento de listas vazias."""
    assert formatar_lista_termos(frozenset()) == "nenhum"
    assert formatar_lista_termos(frozenset({"ovo", "leite", "banana"})) == "banana, leite, ovo"


def test_build_search_view_normal_and_validation_error() -> None:
    """Verifica a renderização da Tela 1 sem erro e com banner de validação (< 2 itens)."""
    state_ok = GUIState(pratos=(_criar_prato_mock(),), validation_error=None)
    view_ok = build_search_view(
        state=state_ok,
        on_search=lambda _: None,
        on_category_select=lambda _: None,
        on_stepper_change=lambda _: None,
        on_pantry_change=lambda _: None,
        on_allergens_change=lambda _: None,
    )
    assert isinstance(view_ok, ft.ListView)
    assert len(view_ok.controls) == 4

    state_err = GUIState(
        pratos=(_criar_prato_mock(),),
        validation_error="A despensa deve conter ao menos 2 ingredientes para a busca.",
    )
    view_err = build_search_view(
        state=state_err,
        on_search=lambda _: None,
        on_category_select=lambda _: None,
        on_stepper_change=lambda _: None,
        on_pantry_change=lambda _: None,
        on_allergens_change=lambda _: None,
    )
    assert isinstance(view_err, ft.ListView)
    # Banner de validação é renderizado
    banner_card = view_err.controls[1]
    assert isinstance(banner_card, ft.Container)
    assert banner_card.bgcolor == COLOR_CORAL


def test_build_results_view_empty_and_populated() -> None:
    """Verifica a renderização da Tela 2 em estado vazio e com pratos sugeridos."""
    # Estado Vazio
    state_empty = GUIState(
        pantry_input="leite, queijo",
        results=(),
        blocked=(),
    )
    view_empty = build_results_view(
        state=state_empty,
        on_back_to_search=lambda _: None,
        on_select_recipe=lambda _: None,
        on_toggle_blocked=lambda _: None,
    )
    assert isinstance(view_empty, ft.ListView)
    # top_bar + summary + empty_card = 3 controls
    assert len(view_empty.controls) == 3

    # Estado com Resultados e Pratos Bloqueados
    prato = _criar_prato_mock()
    prato_bloqueado = _criar_prato_mock(
        dish_id="b-1",
        name="Camarao Frito",
        category="peixes e frutos do mar",
        clean_ingredients=frozenset({"camarao", "farinha"}),
    )
    match = MatchResult(
        dish=prato,
        match_percentage=100.0,
        available_ingredients=frozenset({"ovo", "leite", "chocolate"}),
        missing_ingredients=frozenset(),
    )
    state_populated = GUIState(
        pantry_input="ovo, leite, chocolate",
        allergens_input="farinha",
        results=(match,),
        blocked=(prato_bloqueado,),
        blocked_expanded=True,
    )
    view_populated = build_results_view(
        state=state_populated,
        on_back_to_search=lambda _: None,
        on_select_recipe=lambda _: None,
        on_toggle_blocked=lambda _: None,
    )
    assert isinstance(view_populated, ft.ListView)
    # Deve conter barra superior, resumo, card de prato, header de bloqueados e lista de bloqueados
    assert len(view_populated.controls) >= 4


def test_build_detail_view_100_percent_and_missing() -> None:
    """Verifica a renderização da Tela 3 para prato completo e com compras faltantes."""
    prato = _criar_prato_mock()

    # Caso 100% de correspondência
    match_100 = MatchResult(
        dish=prato,
        match_percentage=100.0,
        available_ingredients=frozenset({"ovo", "leite", "chocolate"}),
        missing_ingredients=frozenset(),
    )
    state_100 = GUIState(selected_match=match_100)
    view_100 = build_detail_view(
        state=state_100,
        on_back_to_results=lambda _: None,
        on_new_search=lambda _: None,
    )
    assert isinstance(view_100, ft.ListView)
    assert len(view_100.controls) == 6

    # Caso com ingredientes faltantes
    match_missing = MatchResult(
        dish=prato,
        match_percentage=66.7,
        available_ingredients=frozenset({"ovo", "leite"}),
        missing_ingredients=frozenset({"chocolate"}),
    )
    state_missing = GUIState(selected_match=match_missing)
    view_missing = build_detail_view(
        state=state_missing,
        on_back_to_results=lambda _: None,
        on_new_search=lambda _: None,
    )
    assert isinstance(view_missing, ft.ListView)
    # Card de resumo de compras em rosa/coral
    resumo_card = view_missing.controls[2]
    assert isinstance(resumo_card, ft.Container)
    assert resumo_card.bgcolor == COLOR_CORAL


def test_no_emojis_in_rendered_gui_views() -> None:
    """Garante que nenhum emoji seja renderizado em nenhum componente de texto da GUI."""
    prato = _criar_prato_mock()
    match = MatchResult(
        dish=prato,
        match_percentage=100.0,
        available_ingredients=frozenset({"ovo", "leite", "chocolate"}),
        missing_ingredients=frozenset(),
    )
    state = GUIState(
        pratos=(prato,),
        pantry_input="ovo, leite",
        allergens_input="farinha",
        max_missing=1,
        results=(match,),
        blocked=(prato,),
        selected_match=match,
        blocked_expanded=True,
        validation_error="Erro de teste",
    )

    v1 = build_search_view(
        state=state,
        on_search=lambda _: None,
        on_category_select=lambda _: None,
        on_stepper_change=lambda _: None,
        on_pantry_change=lambda _: None,
        on_allergens_change=lambda _: None,
    )
    v2 = build_results_view(
        state=state,
        on_back_to_search=lambda _: None,
        on_select_recipe=lambda _: None,
        on_toggle_blocked=lambda _: None,
    )
    v3 = build_detail_view(
        state=state,
        on_back_to_results=lambda _: None,
        on_new_search=lambda _: None,
    )

    v_status = build_phone_status_bar()
    v_home = build_phone_home_indicator()

    def extract_text(control: Any) -> list[str]:
        texts: list[str] = []
        if hasattr(control, "value") and isinstance(control.value, str):
            texts.append(control.value)
        if hasattr(control, "text") and isinstance(control.text, str):
            texts.append(control.text)
        if hasattr(control, "hint_text") and isinstance(control.hint_text, str):
            texts.append(control.hint_text)
        if hasattr(control, "content") and control.content:
            texts.extend(extract_text(control.content))
        if hasattr(control, "controls") and control.controls:
            for child in control.controls:
                texts.extend(extract_text(child))
        return texts

    all_texts = extract_text(v1) + extract_text(v2) + extract_text(v3) + extract_text(v_status) + extract_text(v_home)
    for text in all_texts:
        matches = EMOJI_PATTERN.findall(text)
        assert len(matches) == 0, f"Emoji detectado no texto '{text}': {matches}"
