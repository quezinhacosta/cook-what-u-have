"""
Ponto de Entrada Principal (main.py)

Cook What U Have (MealMatch) — Sistema Funcional de Recomendação de Refeições.
Permite executar a aplicação via interface gráfica desktop estilo smartphone (--gui)
ou via interface de linha de comando declarativa interativa (CLI padrão).
"""

import sys

from interface.cli import iniciar_aplicacao
from interface.gui import iniciar_gui

if __name__ == "__main__":
    if "--gui" in sys.argv or "-g" in sys.argv:
        iniciar_gui()
    else:
        iniciar_aplicacao()
