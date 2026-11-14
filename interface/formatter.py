"""
Formatador Visual de Relatórios (interface/formatter.py)
Funções puras responsáveis por projetar os resultados do grafo em texto legível.
Desenvolvido estritamente com lambdas e interpolação funcional de strings.
"""

from implementation.models import Dish, MatchResult, UserPreferences

# Formata qualquer coleção congelada de termos em texto ordenado separado por vírgulas
formatar_conjunto = lambda s: ", ".join(sorted(s)) if s else "nenhum"

# Formata o card individual de um prato viável recomendado
formatar_card_prato = lambda idx, m: (
    f"[{idx}] {m.dish.name.upper()} (Categoria: {m.dish.category.title()})\n"
    f"    Correspondência: {m.match_percentage}% [{len(m.available_ingredients)}/{len(m.dish.clean_ingredients)} ingredientes]\n"
    f"    ✅ Disponíveis em casa: [{formatar_conjunto(m.available_ingredients)}]\n"
    + (
        "    🎉 Todos os ingredientes disponíveis em casa! Pronto para cozinhar.\n"
        if not m.missing_ingredients else
        f"    🛒 Lista de compras (faltam {len(m.missing_ingredients)}): [{formatar_conjunto(m.missing_ingredients)}]\n"
    )
)

# Formata a seção de alerta com os pratos que foram excluídos devido a alérgenos
formatar_secao_bloqueados = lambda bloqueados, alergenos: (
    (
        "\n--------------------------------------------------------------------------------\n"
        "🛡️  Pratos Bloqueados por Segurança Alimentar:\n"
        + "\n".join(
            map(
                lambda d: f"   ⛔ {d.name} (Contém: [{formatar_conjunto(frozenset(filter(lambda ing: any(a in ing for a in alergenos), d.clean_ingredients)))}])",
                bloqueados,
            )
        )
    )
    if bloqueados else ""
)

# Constrói o relatório visual completo para exibição no console
formatar_relatorio_completo = lambda resultados, bloqueados, prefs: (
    "================================================================================\n"
    "        🍳 COOK WHAT U HAVE — SUGESTÕES DE REFEIÇÃO DISPONÍVEIS\n"
    "================================================================================\n"
    "Configurações da Sessão:\n"
    f"  • Despensa ({len(prefs.pantry)} itens): [{formatar_conjunto(prefs.pantry)}]\n"
    f"  • Alérgenos Banidos ({len(prefs.allergens)}): [{formatar_conjunto(prefs.allergens)}]\n"
    f"  • Tolerância Máxima de Faltantes: Até {prefs.max_missing} item(ns)\n"
    + (f"  • Filtro de Categoria: {prefs.category_filter}\n" if prefs.category_filter else "")
    + "--------------------------------------------------------------------------------\n\n"
    + (
        "\n".join(map(lambda pair: formatar_card_prato(pair[0] + 1, pair[1]), enumerate(resultados)))
        if resultados else
        "⚠️ Nenhum prato encontrado que atenda simultaneamente à despensa e à tolerância informadas.\n"
        "   Dica: Aumente o limiar de tolerância de compras faltantes para ver mais opções!\n"
    )
    + formatar_secao_bloqueados(bloqueados, prefs.allergens)
    + "\n================================================================================\n"
)
