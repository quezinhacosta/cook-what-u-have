"""
Ponto de Entrada Principal (main.py)

Cook What U Have (MealMatch) — Sistema Funcional de Recomendação de Refeições.
Permite executar a aplicação via interface gráfica desktop estilo smartphone (--gui)
ou via interface de linha de comando declarativa interativa (CLI padrão).
"""

from interface.cli import iniciar_aplicacao

if __name__ == "__main__":
    iniciar_aplicacao()
