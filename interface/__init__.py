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
from interface.io_adapter import carregar_pratos

_raise_attribute_error = lambda name: (_ for _ in ()).throw(
    AttributeError(f"module {__name__!r} has no attribute {name!r}")
)

__getattr__ = lambda name: (
    getattr(__import__("interface.gui", fromlist=[name]), name)
    if name in ("iniciar_gui", "GUIState", "criar_app_controller")
    else _raise_attribute_error(name)
)


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
