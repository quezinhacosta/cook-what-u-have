"""
Interface Gráfica Desktop Neo-Brutalista (interface/gui.py)

Implementação de GUI em Python com Flet simulando a ergonomia e proporção de
um smartphone (viewport fixa de 410x800px centralizada), seguindo a estética
Neo-Brutalism (bordas pretas 2px, sombras duras deslocadas sem blur, paleta
vibrante, botões pílula e cantos arredondados).

Fluxo em 3 Telas:
1. Consulta da Despensa (Filtros, Tolerância, Categorias e Validação >= 2 itens)
2. Resultados e Sugestões (Cards viáveis, porcentagens e seção de bloqueados)
3. Detalhes da Receita (Ingredientes originais e modo de preparo passo a passo)

Restrição: Zero emojis. Utiliza texto limpo, badges geométricos e ícones vetoriais.
"""

import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import flet as ft

from implementation.graph import build_recipe_graph
from implementation.models import Dish, MatchResult, RecipeGraph, UserPreferences
from implementation.pipeline import obter_pratos_bloqueados, run_recommendation
from interface.cli import parse_input_set
from interface.formatter import CATEGORIAS_DISPONIVEIS
from interface.gui_theme import (
    COLOR_BG,
    COLOR_BLACK,
    COLOR_CORAL,
    COLOR_GRAY_LIGHT,
    COLOR_GREEN,
    COLOR_LILAC,
    COLOR_ORANGE,
    COLOR_WHITE,
    COLOR_YELLOW,
    VIEWPORT_HEIGHT,
    VIEWPORT_WIDTH,
    neo_badge,
    neo_border,
    neo_button,
    neo_card,
    neo_chip,
    neo_icon_button,
    neo_shadow,
)
from interface.io_adapter import carregar_pratos


# ==============================================================================
# Estado Global da Aplicação GUI
# ==============================================================================
@dataclass
class GUIState:
    """Estado mutável da sessão interativa da interface gráfica."""

    pratos: tuple[Dish, ...] = field(default_factory=tuple)
    grafo: RecipeGraph = field(
        default_factory=lambda: RecipeGraph(
            recipe_to_ingredients={},
            ingredient_to_recipes={},
            dishes_by_id={},
        )
    )
    current_view: str = "search"  # 'search', 'results', 'detail'

    # Inputs do usuário
    pantry_input: str = ""
    allergens_input: str = ""
    max_missing: int = 0
    category_filter: str | None = None
    validation_error: str | None = None

    # Resultados cacheados em memória (evita recalcular ao voltar da Tela 3)
    results: tuple[MatchResult, ...] = field(default_factory=tuple)
    blocked: tuple[Dish, ...] = field(default_factory=tuple)
    selected_match: MatchResult | None = None
    blocked_expanded: bool = False


# ==============================================================================
# Construtores de Componentes e Telas
# ==============================================================================
def formatar_lista_termos(itens: frozenset[str] | set[str] | tuple[str, ...]) -> str:
    """Formata termos em string ordenada separada por vírgula."""
    return ", ".join(sorted(itens)) if itens else "nenhum"


def build_search_view(
    state: GUIState,
    on_search: Callable[[Any], Any],
    on_category_select: Callable[[str | None], Any],
    on_stepper_change: Callable[[int], Any],
    on_pantry_change: Callable[[Any], Any],
    on_allergens_change: Callable[[Any], Any],
) -> ft.Control:
    """Constrói a Tela 1: Consulta da Despensa com inputs e seletores."""
    # Banner de validação de erro (se houver menos de 2 ingredientes)
    validation_banner: ft.Control
    if state.validation_error:
        validation_banner = neo_card(
            content=ft.Row(
                controls=[
                    neo_badge("[!]", bgcolor=COLOR_WHITE, text_color=COLOR_BLACK, padding_h=6, padding_v=2),
                    ft.Text(
                        state.validation_error,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BLACK,
                        expand=True,
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COLOR_CORAL,
            padding=10,
            border_radius=12,
        )
    else:
        validation_banner = ft.Container(height=0)

    # Campo 1: Despensa
    pantry_field = ft.TextField(
        value=state.pantry_input,
        hint_text="ex: leite, ovo, chocolate, queijo",
        bgcolor=COLOR_WHITE,
        border_color=COLOR_BLACK,
        border_width=2,
        border_radius=ft.BorderRadius.all(14),
        color=COLOR_BLACK,
        cursor_color=COLOR_BLACK,
        text_size=12,
        dense=True,
        content_padding=ft.Padding(12, 10, 12, 10),
        multiline=False,
        on_change=on_pantry_change,
    )

    # Campo 2: Alérgenos
    allergens_field = ft.TextField(
        value=state.allergens_input,
        hint_text="ex: farinha, camarao, amendoim",
        bgcolor=COLOR_WHITE,
        border_color=COLOR_BLACK,
        border_width=2,
        border_radius=ft.BorderRadius.all(14),
        color=COLOR_BLACK,
        cursor_color=COLOR_BLACK,
        text_size=12,
        dense=True,
        content_padding=ft.Padding(12, 10, 12, 10),
        multiline=False,
        on_change=on_allergens_change,
    )

    # Campo 3: Stepper de Tolerância de Faltantes
    stepper_row = ft.Row(
        controls=[
            neo_icon_button(
                icon=ft.Icons.REMOVE,
                on_click=lambda _: on_stepper_change(max(0, state.max_missing - 1)),
                bgcolor=COLOR_WHITE if state.max_missing > 0 else COLOR_GRAY_LIGHT,
                size=36,
                icon_size=18,
            ),
            ft.Container(
                content=ft.Text(
                    f"{state.max_missing} item(ns)",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_BLACK,
                ),
                bgcolor=COLOR_WHITE,
                border=neo_border(2, COLOR_BLACK),
                border_radius=ft.BorderRadius.all(999),
                padding=ft.Padding(16, 6, 16, 6),
                shadow=neo_shadow(2.0, 2.0, COLOR_BLACK),
            ),
            neo_icon_button(
                icon=ft.Icons.ADD,
                on_click=lambda _: on_stepper_change(min(10, state.max_missing + 1)),
                bgcolor=COLOR_WHITE,
                size=36,
                icon_size=18,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10,
    )

    # Campo 4: Chips de Categoria Culinária
    def make_category_handler(c: str | None) -> Callable[[Any], Any]:
        return lambda _: on_category_select(c)

    category_chips: list[ft.Control] = [
        neo_chip(
            label="[0] Todas",
            selected=(state.category_filter is None),
            on_click=make_category_handler(None),
            active_color=COLOR_YELLOW,
        )
    ]
    for idx, cat in enumerate(CATEGORIAS_DISPONIVEIS, start=1):
        category_chips.append(
            neo_chip(
                label=f"[{idx}] {cat.title()}",
                selected=(state.category_filter == cat),
                on_click=make_category_handler(cat),
                active_color=COLOR_ORANGE,
            )
        )

    categories_row = ft.Row(
        controls=category_chips,
        scroll=ft.ScrollMode.AUTO,
        spacing=8,
    )

    # Cabeçalho da aplicação
    header_card = neo_card(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "COOK WHAT U HAVE",
                            size=16,
                            weight=ft.FontWeight.W_900,
                            color=COLOR_BLACK,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        neo_badge(
                            f"Base: {len(state.pratos)} pratos carregados",
                            bgcolor=COLOR_LILAC,
                            text_color=COLOR_BLACK,
                            font_size=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COLOR_WHITE,
        border_radius=14,
        padding=10,
    )

    # Formulário Principal
    form_card = neo_card(
        content=ft.Column(
            controls=[
                # Seção Despensa
                ft.Text(
                    "Ingredientes na Despensa (minimo 2):",
                    size=12,
                    weight=ft.FontWeight.W_900,
                    color=COLOR_BLACK,
                ),
                pantry_field,
                ft.Text(
                    "Separe os ingredientes por virgula (ex: ovo, queijo, leite)",
                    size=10,
                    color="#555555",
                ),
                ft.Divider(height=10, color=COLOR_GRAY_LIGHT),

                # Seção Alérgenos
                ft.Text(
                    "Alergenos Banidos (tolerancia zero):",
                    size=12,
                    weight=ft.FontWeight.W_900,
                    color=COLOR_BLACK,
                ),
                allergens_field,
                ft.Text(
                    "Opcional. Exclui qualquer prato que contenha estes itens",
                    size=10,
                    color="#555555",
                ),
                ft.Divider(height=10, color=COLOR_GRAY_LIGHT),

                # Seção Tolerância
                ft.Text(
                    "Tolerancia de Faltantes (compras):",
                    size=12,
                    weight=ft.FontWeight.W_900,
                    color=COLOR_BLACK,
                ),
                stepper_row,
                ft.Divider(height=10, color=COLOR_GRAY_LIGHT),

                # Seção Categorias
                ft.Text(
                    "Categoria Culinaria:",
                    size=12,
                    weight=ft.FontWeight.W_900,
                    color=COLOR_BLACK,
                ),
                categories_row,
            ],
            spacing=6,
        ),
        bgcolor=COLOR_WHITE,
        border_radius=16,
        padding=12,
    )

    # Botão de Ação CTA
    search_button = neo_button(
        text="BUSCAR RECEITAS",
        on_click=on_search,
        bgcolor=COLOR_YELLOW,
        text_color=COLOR_BLACK,
        height=46,
        font_size=14,
        expand=True,
    )

    return ft.ListView(
        controls=[
            header_card,
            validation_banner,
            form_card,
            search_button,
        ],
        spacing=10,
        expand=True,
        padding=ft.Padding(10, 6, 10, 14),
    )


def build_results_view(
    state: GUIState,
    on_back_to_search: Callable[[Any], Any],
    on_select_recipe: Callable[[MatchResult], Any],
    on_toggle_blocked: Callable[[Any], Any],
) -> ft.Control:
    """Constrói a Tela 2: Resultados e Sugestões Viáveis com acordeão de bloqueados."""
    # Barra Superior
    top_bar = ft.Row(
        controls=[
            neo_icon_button(
                icon=ft.Icons.ARROW_BACK,
                on_click=on_back_to_search,
                bgcolor=COLOR_WHITE,
                size=38,
                icon_size=20,
            ),
            ft.Text(
                "Sugestoes",
                size=18,
                weight=ft.FontWeight.W_900,
                color=COLOR_BLACK,
                expand=True,
            ),
            neo_badge(
                text=f"{len(state.results)} viaveis",
                bgcolor=COLOR_GREEN if state.results else COLOR_CORAL,
                font_size=11,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Card Resumo da Sessão (Lilás)
    pantry_parsed = parse_input_set(state.pantry_input)
    allergens_parsed = parse_input_set(state.allergens_input)
    cat_name = state.category_filter.title() if state.category_filter else "Todas"

    session_summary = neo_card(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Configuracao da Sessao",
                    size=12,
                    weight=ft.FontWeight.W_900,
                    color=COLOR_BLACK,
                ),
                ft.Text(
                    f"• Despensa ({len(pantry_parsed)} itens): [{formatar_lista_termos(pantry_parsed)}]",
                    size=11,
                    color=COLOR_BLACK,
                ),
                ft.Text(
                    f"• Alergenos ({len(allergens_parsed)}): [{formatar_lista_termos(allergens_parsed)}]",
                    size=11,
                    color=COLOR_BLACK,
                ),
                ft.Text(
                    f"• Tolerancia Maxima: Ate {state.max_missing} faltante(s) | Categoria: {cat_name}",
                    size=11,
                    color=COLOR_BLACK,
                ),
            ],
            spacing=4,
        ),
        bgcolor=COLOR_LILAC,
        border_radius=16,
        padding=12,
    )

    controls_list: list[ft.Control] = [top_bar, session_summary]

    # Estado Vazio (quando 0 pratos são encontrados)
    if not state.results:
        empty_card = neo_card(
            content=ft.Column(
                controls=[
                    neo_badge("[!]", bgcolor=COLOR_CORAL, text_color=COLOR_BLACK, font_size=14, padding_h=12, padding_v=4),
                    ft.Text(
                        "Nenhum prato encontrado",
                        size=15,
                        weight=ft.FontWeight.W_900,
                        color=COLOR_BLACK,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Nenhum prato atendeu simultaneamente a despensa e a tolerancia informadas.",
                        size=12,
                        color=COLOR_BLACK,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Dica: Aumente o limiar de tolerancia de faltantes ou adicione mais ingredientes a despensa.",
                        size=11,
                        color="#444444",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    neo_button(
                        text="AJUSTAR CONSULTA",
                        on_click=on_back_to_search,
                        bgcolor=COLOR_YELLOW,
                        height=42,
                        font_size=13,
                        expand=False,
                    ),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COLOR_WHITE,
            border_radius=18,
            padding=18,
        )
        controls_list.append(empty_card)
    else:
        # Lista de Cards dos Pratos Viáveis
        def make_select_handler(m: MatchResult) -> Callable[[Any], Any]:
            return lambda _: on_select_recipe(m)

        for idx, match in enumerate(state.results, start=1):
            is_perfect: bool = len(match.missing_ingredients) == 0
            match_badge_color: str = COLOR_GREEN if is_perfect else COLOR_YELLOW

            # Seção de ingredientes disponíveis
            disp_text = formatar_lista_termos(match.available_ingredients)

            # Bloco de compras / faltantes
            compras_control: ft.Control
            if is_perfect:
                compras_control = ft.Container(
                    content=ft.Text(
                        "Todos os ingredientes disponiveis em casa! Pronto para cozinhar.",
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BLACK,
                    ),
                    bgcolor=COLOR_GREEN,
                    border=neo_border(1, COLOR_BLACK),
                    border_radius=ft.BorderRadius.all(8),
                    padding=ft.Padding(8, 4, 8, 4),
                )
            else:
                compras_text = formatar_lista_termos(match.missing_ingredients)
                compras_control = ft.Container(
                    content=ft.Text(
                        f"Lista de compras (faltam {len(match.missing_ingredients)}): [{compras_text}]",
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BLACK,
                    ),
                    bgcolor=COLOR_CORAL,
                    border=neo_border(1, COLOR_BLACK),
                    border_radius=ft.BorderRadius.all(8),
                    padding=ft.Padding(8, 4, 8, 4),
                )

            # Card individual Neo-Brutalista do prato
            dish_card = neo_card(
                content=ft.Column(
                    controls=[
                        # Linha superior: ranking, categoria e correspondência
                        ft.Row(
                            controls=[
                                neo_badge(f"#{idx}", bgcolor=COLOR_YELLOW, font_size=11),
                                neo_badge(match.dish.category.title(), bgcolor=COLOR_ORANGE, font_size=10),
                                ft.Container(expand=True),
                                neo_badge(
                                    f"{match.match_percentage}% [{len(match.available_ingredients)}/{len(match.dish.clean_ingredients)}]",
                                    bgcolor=match_badge_color,
                                    font_size=10,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        # Nome do Prato
                        ft.Text(
                            match.dish.name,
                            size=14,
                            weight=ft.FontWeight.W_900,
                            color=COLOR_BLACK,
                        ),
                        # Disponíveis em casa
                        ft.Text(
                            f"Disponiveis em casa: [{disp_text}]",
                            size=11,
                            color="#333333",
                        ),
                        compras_control,
                        # Botão Ver Receita
                        neo_button(
                            text="VER RECEITA ->",
                            on_click=make_select_handler(match),
                            bgcolor=COLOR_YELLOW,
                            height=36,
                            font_size=12,
                        ),
                    ],
                    spacing=8,
                ),
                bgcolor=COLOR_WHITE,
                border_radius=16,
                padding=12,
            )
            controls_list.append(dish_card)

    # Seção Colapsável / Acordeão: Pratos Bloqueados por Segurança Alimentar
    if state.blocked:
        toggle_icon = ft.Icons.KEYBOARD_ARROW_UP if state.blocked_expanded else ft.Icons.KEYBOARD_ARROW_DOWN
        toggle_label = "[-] Ocultar" if state.blocked_expanded else "[+] Expandir"

        blocked_header = neo_card(
            content=ft.Row(
                controls=[
                    neo_badge("[!]", bgcolor=COLOR_WHITE, font_size=10, padding_h=6, padding_v=2),
                    ft.Text(
                        f"Pratos Bloqueados ({len(state.blocked)})",
                        size=12,
                        weight=ft.FontWeight.W_900,
                        color=COLOR_BLACK,
                        expand=True,
                    ),
                    ft.Text(
                        toggle_label,
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BLACK,
                    ),
                    ft.Icon(toggle_icon, color=COLOR_BLACK, size=18),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=COLOR_CORAL,
            border_radius=14,
            padding=10,
            on_click=on_toggle_blocked,
        )
        controls_list.append(blocked_header)

        if state.blocked_expanded:
            blocked_items: list[ft.Control] = []
            for b_dish in state.blocked:
                contaminantes = frozenset(
                    ing for ing in b_dish.clean_ingredients
                    if any(a in ing for a in allergens_parsed)
                )
                blocked_items.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    f"[BLOQUEADO] {b_dish.name}",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BLACK,
                                ),
                                ft.Text(
                                    f"Contem: [{formatar_lista_termos(contaminantes)}]",
                                    size=10,
                                    color="#551111",
                                ),
                            ],
                            spacing=2,
                        ),
                        bgcolor="#FFE4E8",
                        border=neo_border(1, COLOR_BLACK),
                        border_radius=ft.BorderRadius.all(10),
                        padding=ft.Padding(10, 6, 10, 6),
                    )
                )

            controls_list.append(
                neo_card(
                    content=ft.Column(controls=blocked_items, spacing=6),
                    bgcolor=COLOR_WHITE,
                    border_radius=14,
                    padding=10,
                )
            )

    return ft.ListView(
        controls=controls_list,
        spacing=10,
        expand=True,
        padding=ft.Padding(10, 6, 10, 14),
    )


def build_detail_view(
    state: GUIState,
    on_back_to_results: Callable[[Any], Any],
    on_new_search: Callable[[Any], Any],
) -> ft.Control:
    """Constrói a Tela 3: Detalhes da Receita Selecionada."""
    match = state.selected_match
    if not match:
        return ft.Container(content=ft.Text("Nenhum prato selecionado."))

    is_perfect: bool = len(match.missing_ingredients) == 0

    # Barra Superior
    top_bar = ft.Row(
        controls=[
            neo_icon_button(
                icon=ft.Icons.ARROW_BACK,
                on_click=on_back_to_results,
                bgcolor=COLOR_WHITE,
                size=38,
                icon_size=20,
            ),
            ft.Text(
                "Detalhes do Prato",
                size=16,
                weight=ft.FontWeight.W_900,
                color=COLOR_BLACK,
                expand=True,
            ),
            neo_button(
                text="NOVA BUSCA",
                on_click=on_new_search,
                bgcolor=COLOR_YELLOW,
                height=34,
                font_size=11,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Cabeçalho da Receita
    recipe_header = neo_card(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        neo_badge(match.dish.category.title(), bgcolor=COLOR_ORANGE, font_size=11),
                        neo_badge(
                            f"Cobertura: {match.match_percentage}%",
                            bgcolor=COLOR_GREEN if is_perfect else COLOR_YELLOW,
                            font_size=11,
                        ),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    match.dish.name.upper(),
                    size=16,
                    weight=ft.FontWeight.W_900,
                    color=COLOR_BLACK,
                ),
            ],
            spacing=8,
        ),
        bgcolor=COLOR_LILAC,
        border_radius=18,
        padding=14,
    )

    # Bloco 1: Resumo de Compras
    resumo_compras: ft.Control
    if is_perfect:
        resumo_compras = neo_card(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            neo_badge("[OK]", bgcolor=COLOR_WHITE, font_size=11, padding_h=6, padding_v=2),
                            ft.Text(
                                "Pronto para Cozinhar!",
                                size=13,
                                weight=ft.FontWeight.W_900,
                                color=COLOR_BLACK,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        "Voce tem todos os ingredientes necessarios em casa!",
                        size=11,
                        color=COLOR_BLACK,
                    ),
                ],
                spacing=4,
            ),
            bgcolor=COLOR_GREEN,
            border_radius=14,
            padding=12,
        )
    else:
        missing_text = formatar_lista_termos(match.missing_ingredients)
        resumo_compras = neo_card(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            neo_badge("[!]", bgcolor=COLOR_WHITE, font_size=11, padding_h=6, padding_v=2),
                            ft.Text(
                                f"Falta comprar ({len(match.missing_ingredients)} itens):",
                                size=13,
                                weight=ft.FontWeight.W_900,
                                color=COLOR_BLACK,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        f"[{missing_text}]",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BLACK,
                    ),
                ],
                spacing=4,
            ),
            bgcolor=COLOR_CORAL,
            border_radius=14,
            padding=12,
        )

    # Bloco 2: Ingredientes Originais Necessários
    ingredientes_items: list[ft.Control] = []
    if match.dish.raw_ingredients:
        for raw_ing in match.dish.raw_ingredients:
            ingredientes_items.append(
                ft.Row(
                    controls=[
                        neo_badge("•", bgcolor=COLOR_YELLOW, font_size=10, padding_h=6, padding_v=1),
                        ft.Text(raw_ing, size=11, color=COLOR_BLACK, expand=True),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            )
    else:
        ingredientes_items.append(
            ft.Text("Lista de ingredientes nao informada.", size=11, italic=True)
        )

    bloco_ingredientes = neo_card(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Ingredientes Originais Necessarios:",
                    size=13,
                    weight=ft.FontWeight.W_900,
                    color=COLOR_BLACK,
                ),
                ft.Divider(height=8, color=COLOR_GRAY_LIGHT),
                ft.Column(controls=ingredientes_items, spacing=6),
            ],
            spacing=6,
        ),
        bgcolor=COLOR_WHITE,
        border_radius=16,
        padding=14,
    )

    # Bloco 3: Modo de Preparo (Passo a Passo)
    passos_items: list[ft.Control] = []
    if match.dish.recipe:
        for idx, passo in enumerate(match.dish.recipe, start=1):
            passos_items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            neo_badge(f"[{idx}]", bgcolor=COLOR_ORANGE, font_size=10, padding_h=6, padding_v=2),
                            ft.Text(passo, size=11, color=COLOR_BLACK, expand=True),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    bgcolor="#FFFBF5",
                    border=neo_border(1, COLOR_BLACK),
                    border_radius=ft.BorderRadius.all(10),
                    padding=ft.Padding(10, 8, 10, 8),
                )
            )
    else:
        passos_items.append(
            ft.Text("Passo a passo nao disponivel para este prato.", size=11, italic=True)
        )

    bloco_preparo = neo_card(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Modo de Preparo (Passo a Passo):",
                    size=13,
                    weight=ft.FontWeight.W_900,
                    color=COLOR_BLACK,
                ),
                ft.Divider(height=8, color=COLOR_GRAY_LIGHT),
                ft.Column(controls=passos_items, spacing=8),
            ],
            spacing=6,
        ),
        bgcolor=COLOR_WHITE,
        border_radius=16,
        padding=14,
    )

    # Botões inferiores de navegação
    bottom_actions = ft.Row(
        controls=[
            neo_button(
                text="<- VOLTAR",
                on_click=on_back_to_results,
                bgcolor=COLOR_WHITE,
                height=42,
                font_size=12,
                expand=True,
            ),
            neo_button(
                text="NOVA BUSCA",
                on_click=on_new_search,
                bgcolor=COLOR_YELLOW,
                height=42,
                font_size=12,
                expand=True,
            ),
        ],
        spacing=8,
    )

    return ft.ListView(
        controls=[
            top_bar,
            recipe_header,
            resumo_compras,
            bloco_ingredientes,
            bloco_preparo,
            bottom_actions,
        ],
        spacing=10,
        expand=True,
        padding=ft.Padding(10, 6, 10, 14),
    )


# ==============================================================================
# Controlador Principal da Aplicação
# ==============================================================================
def criar_app_controller(page: ft.Page, pratos_iniciais: tuple[Dish, ...] | None = None) -> None:
    """Configura o estado, os handlers reativos e renderiza o viewport do smartphone."""
    pratos = pratos_iniciais if pratos_iniciais is not None else carregar_pratos()
    grafo = build_recipe_graph(pratos)

    state = GUIState(pratos=pratos, grafo=grafo)

    # Configuração de Janela Mobile Viewport (estreita e vertical)
    page.title = "Cook What U Have"
    page.bgcolor = "#EFEAE1"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = ft.Padding(0, 10, 0, 10)
    page.scroll = ft.ScrollMode.AUTO

    try:
        page.window.width = VIEWPORT_WIDTH + 16
        page.window.height = VIEWPORT_HEIGHT + 32
        page.window.resizable = False
        page.window.min_width = VIEWPORT_WIDTH
        page.window.min_height = VIEWPORT_HEIGHT
    except Exception:
        pass

    # Viewport vertical estilo tela de celular (sem adornos literais de hardware)
    viewport_container = ft.Container(
        width=VIEWPORT_WIDTH,
        height=VIEWPORT_HEIGHT,
        bgcolor=COLOR_BG,
        border=neo_border(2, COLOR_BLACK),
        border_radius=ft.BorderRadius.all(20),
        shadow=neo_shadow(5.0, 5.0, COLOR_BLACK),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        alignment=ft.Alignment.TOP_CENTER,
    )

    def render() -> None:
        """Renderiza a view correspondente ao estado atual dentro da viewport vertical."""
        if state.current_view == "search":
            viewport_container.content = build_search_view(
                state=state,
                on_search=handle_search,
                on_category_select=handle_category_select,
                on_stepper_change=handle_stepper_change,
                on_pantry_change=handle_pantry_change,
                on_allergens_change=handle_allergens_change,
            )
        elif state.current_view == "results":
            viewport_container.content = build_results_view(
                state=state,
                on_back_to_search=handle_back_to_search,
                on_select_recipe=handle_select_recipe,
                on_toggle_blocked=handle_toggle_blocked,
            )
        elif state.current_view == "detail":
            viewport_container.content = build_detail_view(
                state=state,
                on_back_to_results=handle_back_to_results,
                on_new_search=handle_back_to_search,
            )
        page.update()

    # Handlers Reativos
    def handle_pantry_change(e: Any) -> None:
        state.pantry_input = str(e.control.value or "")

    def handle_allergens_change(e: Any) -> None:
        state.allergens_input = str(e.control.value or "")

    def handle_stepper_change(val: int) -> None:
        state.max_missing = val
        render()

    def handle_category_select(cat: str | None) -> None:
        state.category_filter = cat
        render()

    def handle_search(_: Any) -> None:
        pantry_set = parse_input_set(state.pantry_input)
        if len(pantry_set) < 2:
            state.validation_error = "A despensa deve conter ao menos 2 ingredientes para a busca."
            render()
            return

        state.validation_error = None
        allergens_set = parse_input_set(state.allergens_input)

        prefs = UserPreferences(
            pantry=pantry_set,
            allergens=allergens_set,
            max_missing=state.max_missing,
            category_filter=state.category_filter,
            min_matched=2,
        )

        state.results = run_recommendation(state.grafo, prefs)
        state.blocked = obter_pratos_bloqueados(state.grafo, prefs.allergens, prefs.category_filter)
        state.current_view = "results"
        render()

    def handle_back_to_search(_: Any) -> None:
        state.current_view = "search"
        render()

    def handle_select_recipe(match: MatchResult) -> None:
        state.selected_match = match
        state.current_view = "detail"
        render()

    def handle_back_to_results(_: Any) -> None:
        state.current_view = "results"
        render()

    def handle_toggle_blocked(_: Any) -> None:
        state.blocked_expanded = not state.blocked_expanded
        render()

    page.controls = [
        ft.Row(
            controls=[viewport_container],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    ]
    render()


def iniciar_gui(
    view: ft.AppView | None = None,
    port: int = 0,
    pratos_iniciais: tuple[Dish, ...] | None = None,
) -> None:
    """Ponto de entrada para inicializar a GUI no desktop ou no navegador."""
    # Previne crash do GTK/GIO no Linux Wayland (Ubuntu 24.04/GNOME 46) forçando backend X11/XWayland
    if sys.platform.startswith("linux"):
        os.environ.setdefault("GDK_BACKEND", "x11")

    # Detecção de ambiente gráfico (X11 / Wayland)
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    is_desktop_os = sys.platform in ("win32", "darwin")

    is_web_requested = "--web" in sys.argv or "-w" in sys.argv

    chosen_view: ft.AppView
    if view is not None:
        chosen_view = view
    elif is_web_requested or (not has_display and not is_desktop_os):
        chosen_view = ft.AppView.WEB_BROWSER
    else:
        chosen_view = ft.AppView.FLET_APP

    if chosen_view == ft.AppView.WEB_BROWSER:
        print("[Cook What U Have] Iniciando interface grafica no navegador web...")
    else:
        print("[Cook What U Have] Iniciando interface grafica desktop (Viewport Mobile 410x800)...")
        print("   Dica: Se preferir abrir no navegador web, utilize: python3 main.py --gui --web")

    def main(page: ft.Page) -> None:
        criar_app_controller(page, pratos_iniciais=pratos_iniciais)

    try:
        ft.run(main, view=chosen_view, port=port)
    except Exception as exc:
        if chosen_view == ft.AppView.FLET_APP:
            print(f"[Cook What U Have] Falha ao iniciar cliente desktop ({exc}).")
            print("[Cook What U Have] Alternando automaticamente para o modo navegador web...")
            ft.run(main, view=ft.AppView.WEB_BROWSER, port=port)
        else:
            raise


if __name__ == "__main__":
    iniciar_gui()
