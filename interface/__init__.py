"""
Pacote de Interface e Adaptadores de E/S (interface/__init__.py)
Exporta carregador de pratos, formatador de relatórios e pontos de entrada da CLI e GUI.
"""

from interface.cli import (
    executar_consulta,
    executar_sessao,
    iniciar_aplicacao,
    loop_navegacao_pratos,
    parse_input_set,
    parse_int,
    resolver_categoria_input,
)
from interface.formatter import (
    CATEGORIAS_DISPONIVEIS,
    formatar_detalhes_receita,
    formatar_menu_categorias,
    formatar_relatorio_completo,
)
from interface.gui import (
    GUIState,
    criar_app_controller,
    iniciar_gui,
)
from interface.io_adapter import carregar_pratos

__all__ = (
    "CATEGORIAS_DISPONIVEIS",
    "GUIState",
    "carregar_pratos",
    "criar_app_controller",
    "executar_consulta",
    "executar_sessao",
    "formatar_detalhes_receita",
    "formatar_menu_categorias",
    "formatar_relatorio_completo",
    "iniciar_aplicacao",
    "iniciar_gui",
    "loop_navegacao_pratos",
    "parse_input_set",
    "parse_int",
    "resolver_categoria_input",
)
