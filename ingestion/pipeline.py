"""
Pipeline Orquestrador de Ingestão de Dados (ingestion/pipeline.py)
Responsabilidade: Orquestrar o fluxo funcional conectando as bordas de I/O
(rede e disco via io_gateway) com o núcleo computacional 100% puro
(parser.py e normalizer.py), mapeando 15 receitas recomendadas para cada
uma das 8 categorias do TudoGostoso e gerando pratos.json padronizados.
"""

import sys
from pathlib import Path
from typing import Optional
from ingestion.models import CategoryTarget, CategoryResult, ProcessedRecipe
from ingestion.parser import extrair_links_categoria_html, extrair_receita_html
from ingestion.normalizer import processar_receita
from ingestion.io_gateway import baixar_html, salvar_categoria_json

# Diretório base de persistência dos dados: ingestion/data/
DATA_DIR: Path = Path(__file__).parent / "data"

# Mapeamento imutável das 8 categorias oficiais do TudoGostoso
CATEGORIAS_PADRAO: tuple[CategoryTarget, ...] = (
    CategoryTarget("aves", "https://www.tudogostoso.com.br/categorias/1009-aves"),
    CategoryTarget("bolos e tortas", "https://www.tudogostoso.com.br/categorias/1000-bolos-e-tortas-doces"),
    CategoryTarget("carnes", "https://www.tudogostoso.com.br/categorias/1004-carnes"),
    CategoryTarget("doces e sobremesas", "https://www.tudogostoso.com.br/categorias/1037-doces-e-sobremesas"),
    CategoryTarget("massas", "https://www.tudogostoso.com.br/categorias/1028-massas"),
    CategoryTarget("peixes e frutos do mar", "https://www.tudogostoso.com.br/categorias/1014-peixes-e-frutos-do-mar"),
    CategoryTarget("saladas e molhos", "https://www.tudogostoso.com.br/categorias/1023-saladas-molhos-e-acompanhamentos"),
    CategoryTarget("sopas", "https://www.tudogostoso.com.br/categorias/1027-sopas"),
)


# ==============================================================================
# FUNÇÕES PURAS DE FILTRAGEM E FORMATAÇÃO
# ==============================================================================

def filtrar_alvos_por_nome(
    alvos: tuple[CategoryTarget, ...],
    filtro: Optional[str]
) -> tuple[CategoryTarget, ...]:
    """Função pura: filtra os alvos de processamento com base em argumento textual opcional."""
    if not filtro:
        return alvos
    filtro_lower = filtro.strip().lower()
    return tuple(filter(lambda alvo: filtro_lower in alvo.nome.lower(), alvos))


def formatar_linha_resumo(resultado: CategoryResult) -> str:
    """Função pura: formata cada linha de relatório do processamento de categoria."""
    return f"  • {resultado.nome:<22}: {len(resultado.receitas):>2} receitas salvas em {resultado.destino.name}"


# ==============================================================================
# CASCA IMPURA DE ORQUESTRAÇÃO (CONECTA I/O AO NÚCLEO PURO)
# ==============================================================================

def extrair_e_processar_url(url: str, categoria: str) -> Optional[ProcessedRecipe]:
    """
    Orquestra o processamento de uma única URL:
    1. I/O: Baixa HTML via rede.
    2. Puro: Extrai dados brutos com parser.
    3. Puro: Normaliza ingredientes e gera ID determinístico.
    Retorna a receita processada ou None em caso de falha.
    """
    html = baixar_html(url)
    if not html:
        return None

    raw_recipe = extrair_receita_html(html, url, tipo_padrao=categoria)
    if not raw_recipe:
        return None

    return processar_receita(raw_recipe, categoria_alvo=categoria)


def processar_categoria(
    alvo: CategoryTarget,
    base_dir: Path,
    limite: int = 15
) -> CategoryResult:
    """
    Processa uma categoria completa de ponta a ponta:
    1. Baixa o HTML da página de categoria.
    2. Extrai de forma pura as URLs recomendadas.
    3. Mapeia a extração e normalização de cada receita.
    4. Persiste o resultado no arquivo JSON de destino.
    """
    destino = base_dir / alvo.nome / "pratos.json"
    print(f"\n📂 [{alvo.nome.upper()}] Buscando até {limite} receitas recomendadas...")

    html_categoria = baixar_html(alvo.url)
    urls_recomendadas = extrair_links_categoria_html(html_categoria, limite=limite)

    if not urls_recomendadas:
        print(f"   ⚠️ Nenhuma URL encontrada para a categoria '{alvo.nome}'.")
        resultado_vazio = CategoryResult(nome=alvo.nome, destino=destino, receitas=())
        salvar_categoria_json(resultado_vazio)
        return resultado_vazio

    print(f"   ↳ {len(urls_recomendadas)} URLs encontradas. Extraindo e normalizando...")

    # Mapeamento funcional das receitas através de funções de alta ordem
    receitas_iter = map(lambda u: extrair_e_processar_url(u, alvo.nome), urls_recomendadas)
    receitas_validas: tuple[ProcessedRecipe, ...] = tuple(
        filter(lambda r: r is not None, receitas_iter)
    )

    resultado = CategoryResult(
        nome=alvo.nome,
        destino=destino,
        receitas=receitas_validas
    )

    total_salvo = salvar_categoria_json(resultado)
    print(f"   ✅ {total_salvo} receitas padronizadas salvas em: {destino}")

    return resultado


def executar_pipeline(
    alvos: tuple[CategoryTarget, ...] = CATEGORIAS_PADRAO,
    base_dir: Path = DATA_DIR,
    limite_por_categoria: int = 15
) -> tuple[CategoryResult, ...]:
    """
    Orquestra o pipeline funcional para todas as categorias informadas.
    Utiliza composição declarativa via map(), sem acumuladores mutáveis.
    """
    print(f"🚀 Iniciando Pipeline Funcional de Ingestão (limite: {limite_por_categoria} receitas/categoria)...")
    print(f"Categorias selecionadas: {[alvo.nome for alvo in alvos]}")

    resultados: tuple[CategoryResult, ...] = tuple(
        map(lambda alvo: processar_categoria(alvo, base_dir, limite=limite_por_categoria), alvos)
    )

    total_geral = sum(map(lambda res: len(res.receitas), resultados))
    linhas_resumo = "\n".join(map(formatar_linha_resumo, resultados))

    print("\n" + "=" * 70)
    print("🎉 Pipeline de Ingestão Concluído com Sucesso!")
    print(f"Total geral de receitas padronizadas: {total_geral}")
    print(linhas_resumo)
    print("=" * 70)

    return resultados


def main() -> None:
    """Ponto de entrada via CLI com suporte a filtro de categoria opcional."""
    filtro_cli = sys.argv[1].strip() if len(sys.argv) > 1 else None
    alvos_selecionados = filtrar_alvos_por_nome(CATEGORIAS_PADRAO, filtro_cli)

    if not alvos_selecionados:
        print(f"❌ Nenhuma categoria encontrada correspondente ao filtro: '{filtro_cli}'")
        print(f"Categorias disponíveis: {[alvo.nome for alvo in CATEGORIAS_PADRAO]}")
        sys.exit(1)

    executar_pipeline(alvos=alvos_selecionados, base_dir=DATA_DIR, limite_por_categoria=15)


if __name__ == "__main__":
    main()
