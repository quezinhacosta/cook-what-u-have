"""
Tema e Tokens de Design Neo-Brutalism (interface/gui_theme.py)

Define a paleta cromática de alto contraste, bordas sólidas pretas, sombras
deslocadas sem desfoque (hard offset drop shadows) e fábricas de componentes
estilizados (cards, botões em pílula, chips e badges) para a viewport mobile.
"""

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

# Dimensões da Viewport Mobile Vertical (Estilo Tela de Celular)
VIEWPORT_WIDTH: int = 1060
VIEWPORT_HEIGHT: int = 760
WINDOW_WIDTH: int = 860
WINDOW_HEIGHT: int = 760


# ==============================================================================
# Primitivas de Estilo Neo-Brutalista (Funções Lambda Puras)
# ==============================================================================
neo_border = lambda width=2, color=COLOR_BLACK: ft.Border.all(width=width, color=color)

neo_shadow = lambda offset_x=4.0, offset_y=4.0, color=COLOR_BLACK: ft.BoxShadow(
    spread_radius=0.0,
    blur_radius=0.0,
    color=color,
    offset=ft.Offset(offset_x, offset_y),
)


# ==============================================================================
# Fábricas de Controles Neo-Brutalistas (Funções Lambda Puras)
# ==============================================================================
neo_card = lambda content, bgcolor=COLOR_WHITE, border_radius=18, padding=14, margin=None, on_click=None, offset_shadow=(4.0, 4.0), expand=False: ft.Container(
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

neo_badge = lambda text, bgcolor=COLOR_YELLOW, text_color=COLOR_BLACK, border_radius=999, font_size=11, padding_h=10, padding_v=4: ft.Container(
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

neo_button = lambda text, on_click=None, bgcolor=COLOR_YELLOW, text_color=COLOR_BLACK, height=48, font_size=14, expand=False, border_radius=999: ft.Container(
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

neo_icon_button = lambda icon, on_click=None, bgcolor=COLOR_WHITE, icon_color=COLOR_BLACK, size=40, icon_size=20: ft.Container(
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

neo_chip = lambda label, selected, on_click=None, active_color=COLOR_ORANGE: ft.Container(
    content=ft.Text(
        label,
        size=11,
        weight=ft.FontWeight.BOLD,
        color=COLOR_BLACK,
        no_wrap=True,
    ),
    bgcolor=active_color if selected else COLOR_WHITE,
    border=neo_border(2, COLOR_BLACK),
    border_radius=ft.BorderRadius.all(999),
    shadow=neo_shadow(3.0 if selected else 2.0, 3.0 if selected else 2.0, COLOR_BLACK),
    padding=ft.Padding(12, 6, 12, 6),
    alignment=ft.Alignment.CENTER,
    on_click=on_click,
)
