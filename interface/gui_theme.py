"""
Tema e Tokens de Design Neo-Brutalism (interface/gui_theme.py)

Define a paleta cromática de alto contraste, bordas sólidas pretas, sombras
deslocadas sem desfoque (hard offset drop shadows) e fábricas de componentes
estilizados (cards, botões em pílula, chips e badges) para a viewport mobile.
"""

from collections.abc import Callable
from typing import Any

import flet as ft

# ==============================================================================
# Paleta de Cores Neo-Brutalista
# ==============================================================================
COLOR_BG: str = "#FAF7F2"  # Fundo principal off-white / creme suave
COLOR_BLACK: str = "#111111"  # Preto sólido para bordas e sombras duras
COLOR_WHITE: str = "#FFFFFF"  # Branco puro para inputs e cards neutros
COLOR_YELLOW: str = "#FFD166"  # Amarelo mostarda vibrante (ações principais / CTA)
COLOR_GREEN: str = "#B5E48C"  # Verde menta/limão (100% match / sucesso)
COLOR_GREEN_MINT: str = "#A8E6CF"  # Verde pastel complementar
COLOR_LILAC: str = "#CDB4DB"  # Lilás suave (cards de resumo / filtros de sessão)
COLOR_CORAL: str = "#FF8FA3"  # Rosa chiclete/coral (alertas / itens faltantes / bloqueados)
COLOR_CORAL_LIGHT: str = "#FFAFCC"  # Coral suave secundário
COLOR_ORANGE: str = "#F4A261"  # Laranja tangerina (chips de categorias culinárias)
COLOR_GRAY_LIGHT: str = "#EAE6DF"  # Cinza neutro para seletores e bordas de fundo

# Dimensões da Viewport Mobile Similares a Smartphone
WINDOW_WIDTH: int = 410
WINDOW_HEIGHT: int = 800


# ==============================================================================
# Primitivas de Estilo Neo-Brutalista
# ==============================================================================
def neo_border(width: int = 2, color: str = COLOR_BLACK) -> ft.Border:
    """Retorna borda sólida com espessura padrão de 2px."""
    return ft.Border.all(width=width, color=color)


def neo_shadow(
    offset_x: float = 4.0,
    offset_y: float = 4.0,
    color: str = COLOR_BLACK,
) -> ft.BoxShadow:
    """Retorna sombra sólida deslocada sem desfoque (hard shadow)."""
    return ft.BoxShadow(
        spread_radius=0.0,
        blur_radius=0.0,
        color=color,
        offset=ft.Offset(offset_x, offset_y),
    )


# ==============================================================================
# Fábricas de Controles Neo-Brutalistas
# ==============================================================================
def neo_card(
    content: ft.Control,
    bgcolor: str = COLOR_WHITE,
    border_radius: int = 18,
    padding: int = 14,
    margin: ft.Margin | None = None,
    on_click: Callable[[Any], Any] | None = None,
    offset_shadow: tuple[float, float] = (4.0, 4.0),
    expand: bool = False,
) -> ft.Container:
    """Cria um card com borda preta sólida de 2px e sombra dura deslocada."""
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border=neo_border(2, COLOR_BLACK),
        border_radius=ft.BorderRadius.all(border_radius),
        shadow=neo_shadow(offset_shadow[0], offset_shadow[1], COLOR_BLACK),
        padding=ft.Padding(padding, padding, padding, padding),
        margin=margin,
        on_click=on_click,
        expand=expand,
    )


def neo_badge(
    text: str,
    bgcolor: str = COLOR_YELLOW,
    text_color: str = COLOR_BLACK,
    border_radius: int = 999,
    font_size: int = 11,
    padding_h: int = 10,
    padding_v: int = 4,
) -> ft.Container:
    """Cria um badge em formato de pílula com borda preta e texto em negrito."""
    return ft.Container(
        content=ft.Text(
            text,
            size=font_size,
            weight=ft.FontWeight.BOLD,
            color=text_color,
            no_wrap=True,
        ),
        bgcolor=bgcolor,
        border=neo_border(2, COLOR_BLACK),
        border_radius=ft.BorderRadius.all(border_radius),
        padding=ft.Padding(padding_h, padding_v, padding_h, padding_v),
        shadow=neo_shadow(2.0, 2.0, COLOR_BLACK),
        alignment=ft.Alignment.CENTER,
    )


def neo_button(
    text: str,
    on_click: Callable[[Any], Any] | None,
    bgcolor: str = COLOR_YELLOW,
    text_color: str = COLOR_BLACK,
    height: int = 48,
    font_size: int = 14,
    expand: bool = False,
    border_radius: int = 999,
) -> ft.Container:
    """Cria botão de ação estilo pílula com borda preta grossa e sombra dura."""
    return ft.Container(
        content=ft.Text(
            text,
            size=font_size,
            weight=ft.FontWeight.W_900,
            color=text_color,
            text_align=ft.TextAlign.CENTER,
        ),
        bgcolor=bgcolor,
        border=neo_border(2, COLOR_BLACK),
        border_radius=ft.BorderRadius.all(border_radius),
        shadow=neo_shadow(4.0, 4.0, COLOR_BLACK),
        alignment=ft.Alignment.CENTER,
        height=height,
        padding=ft.Padding(16, 8, 16, 8),
        on_click=on_click,
        expand=expand,
    )


def neo_icon_button(
    icon: Any,
    on_click: Callable[[Any], Any] | None,
    bgcolor: str = COLOR_WHITE,
    icon_color: str = COLOR_BLACK,
    size: int = 40,
    icon_size: int = 20,
) -> ft.Container:
    """Cria botão circular compacto com ícone e borda preta para navegação."""
    return ft.Container(
        content=ft.Icon(icon, color=icon_color, size=icon_size),
        bgcolor=bgcolor,
        border=neo_border(2, COLOR_BLACK),
        border_radius=ft.BorderRadius.all(999),
        shadow=neo_shadow(3.0, 3.0, COLOR_BLACK),
        width=size,
        height=size,
        alignment=ft.Alignment.CENTER,
        on_click=on_click,
    )


def neo_chip(
    label: str,
    selected: bool,
    on_click: Callable[[Any], Any] | None,
    active_color: str = COLOR_ORANGE,
) -> ft.Container:
    """Cria chip/pílula selecionável para filtros como categorias culinárias."""
    bg: str = active_color if selected else COLOR_WHITE
    shadow_offset: tuple[float, float] = (3.0, 3.0) if selected else (2.0, 2.0)
    return ft.Container(
        content=ft.Text(
            label,
            size=11,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BLACK,
            no_wrap=True,
        ),
        bgcolor=bg,
        border=neo_border(2, COLOR_BLACK),
        border_radius=ft.BorderRadius.all(999),
        shadow=neo_shadow(shadow_offset[0], shadow_offset[1], COLOR_BLACK),
        padding=ft.Padding(12, 6, 12, 6),
        alignment=ft.Alignment.CENTER,
        on_click=on_click,
    )
