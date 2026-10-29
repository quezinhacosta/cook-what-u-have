# 📥 Módulo de Ingestão de Dados (`ingestion/`)
### Extração de Receitas do TudoGostoso por Categorias e Geração da Base Imutável

> **Componente do Projeto:** *Cook What U Have (MealMatch)*  
> **Responsabilidade:** Extrair as 15 primeiras receitas recomendadas de cada categoria do TudoGostoso, estruturando os 4 campos essenciais (`titulo`, `tipo`, `receita`, `ingredientes`) e gravando o catálogo `pratos.json` dentro de cada respectiva subpasta de `data/`.

---

## 🎯 1. Objetivo e Papel na Arquitetura

O módulo de **Ingestão de Dados** atua como uma etapa prévia e desacoplada do motor central de recomendação:

1. **O Motor de Decisão permanece 100% Offline e Determinístico:** Não há chamadas de rede HTTP em tempo real durante a execução do motor de recomendação.
2. **Separação de Preocupações (*Separation of Concerns*):** O motor da pasta `implementation/` consome os dados consolidados no disco, processando-os como um Grafo Bipartido puramente em memória.
3. **Mapeamento Modular por Categorias:** Cada categoria gastronômica possui sua própria subpasta dentro de `ingestion/data/`, facilitando consultas filtradas ou carregamento sob demanda.

---

## 🛠️ 2. Tecnologias Utilizadas

* **[`recipe-scrapers`](https://github.com/hhursev/recipe-scrapers):** Parser especializado com suporte oficial às páginas de receitas do TudoGostoso (`tudogostoso.com.br`).
* **`beautifulsoup4` e `requests`:** Utilizados de forma declarativa e pura em `extractor.py` para descobrir os links das receitas recomendadas no topo de cada página de categoria.
* **Paradigma Funcional:** Uso estrito de imutabilidade (`NamedTuple`), predicados puros (`filter`) e mapeamentos declarativos (`map`), sem loops imperativos `for`/`while` com acumuladores mutáveis.

---

## 📂 3. Estrutura de Pastas e Mapeamento de Categorias

A pasta `ingestion/data/` está estruturada com as seguintes 8 categorias:

```
ingestion/
├── data/
│   ├── aves/                     # pratos.json (até 15 receitas)
│   ├── bolos e tortas/           # pratos.json (até 15 receitas)
│   ├── carnes/                   # pratos.json (até 15 receitas)
│   ├── doces e sobremesas/       # pratos.json (até 15 receitas)
│   ├── massas/                   # pratos.json (até 15 receitas)
│   ├── peixes e frutos do mar/   # pratos.json (até 15 receitas)
│   ├── saladas e molhos/         # pratos.json (até 15 receitas)
│   └── sopas/                    # pratos.json (até 15 receitas)
│
├── extractor.py                  # Extração da página de categoria e de cada receita
├── normalizer.py                 # Funções puras de sanitização textual
├── pipeline.py                   # Orquestrador funcional por categorias
└── README.md                     # Documentação técnica do módulo
```

### URLs Oficiais Mapeadas no TudoGostoso:
| Categoria na pasta `data/` | URL da Categoria no TudoGostoso |
| :--- | :--- |
| `aves` | `https://www.tudogostoso.com.br/categorias/1009-aves` |
| `bolos e tortas` | `https://www.tudogostoso.com.br/categorias/1000-bolos-e-tortas-doces` |
| `carnes` | `https://www.tudogostoso.com.br/categorias/1004-carnes` |
| `doces e sobremesas` | `https://www.tudogostoso.com.br/categorias/1037-doces-e-sobremesas` |
| `massas` | `https://www.tudogostoso.com.br/categorias/1028-massas` |
| `peixes e frutos do mar` | `https://www.tudogostoso.com.br/categorias/1014-peixes-e-frutos-do-mar` |
| `saladas e molhos` | `https://www.tudogostoso.com.br/categorias/1023-saladas-molhos-e-acompanhamentos` |
| `sopas` | `https://www.tudogostoso.com.br/categorias/1027-sopas` |

---

## 📄 4. Esquema dos 4 Campos em cada `pratos.json`

Cada arquivo `pratos.json` gerado em sua respectiva subpasta possui a seguinte estrutura:

```json
[
  {
    "titulo": "Macarrão à carbonara",
    "tipo": "Massas",
    "receita": "Em uma panela, coloque a água e o sal para ferver...\nFrite o bacon até ficar crocante...",
    "ingredientes": [
      "500 g de macarrão",
      "250 g de bacon em cubos",
      "1 caixa de creme de leite",
      "3 ovos",
      "Queijo ralado a gosto",
      "Pimenta-do-reino a gosto"
    ]
  }
]
```

---

## 🚀 5. Como Executar a Ingestão

Para disparar o processo de scraping e gerar os arquivos `pratos.json` de cada categoria:

### Processar Todas as 8 Categorias:
```bash
cd /home/quezia/cook-what-u-have/cook-what-u-have
.venv/bin/python -m ingestion.pipeline
```

### Processar Apenas uma Categoria Específica (ex: Massas):
```bash
.venv/bin/python -m ingestion.pipeline massas
```
