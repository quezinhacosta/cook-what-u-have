"""
Módulo de Gateway de E/S e Efeitos Colaterais (ingestion/io_gateway.py)
Responsabilidade: Centralizar de forma estrita todas as operações impuras de
entrada e saída (requisições HTTP via rede e persistência/leitura de arquivos no disco),
blindando as camadas de domínio, modelos, normalizador e parser contra side-effects.
"""

import json
from pathlib import Path
import requests
from ingestion.models import CategoryResult, recipe_to_dict

# Headers HTTP padrão simulando navegador comum
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def baixar_html(url: str, timeout: int = 15) -> str:
    """
    Efeito colateral de rede isolado:
    Executa a requisição HTTP GET para uma URL externa e retorna o HTML textual.
    Em caso de falha de conexão, timeout ou status code != 200, retorna string vazia
    de forma segura, permitindo que os filtros funcionais descartem o resultado.
    """
    try:
        resposta = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        return resposta.text if resposta.status_code == 200 else ""
    except Exception:
        return ""


def salvar_categoria_json(resultado: CategoryResult) -> int:
    """
    Efeito colateral de disco isolado:
    Garante a existência do diretório e serializa a coleção de receitas
    processadas no arquivo pratos.json de destino.
    Retorna a quantidade de receitas persistidas.
    """
    resultado.destino.parent.mkdir(parents=True, exist_ok=True)
    dados_serializaveis = list(map(recipe_to_dict, resultado.receitas))

    with open(resultado.destino, "w", encoding="utf-8") as f:
        json.dump(dados_serializaveis, f, ensure_ascii=False, indent=2)

    return len(dados_serializaveis)


def ler_categoria_json(caminho_arquivo: Path) -> tuple[dict, ...]:
    """
    Efeito colateral de disco isolado:
    Lê um arquivo JSON de receitas previamente persistido e retorna uma tupla imutável.
    Em caso de arquivo inexistente ou erro de parse, retorna uma tupla vazia.
    """
    if not caminho_arquivo.exists():
        return ()
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return tuple(dados) if isinstance(dados, list) else ()
    except Exception:
        return ()
