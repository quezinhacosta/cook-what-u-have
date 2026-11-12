# 📥 Módulo de Ingestão de Dados Funcional (`ingestion/`)
### Extração de Receitas do TudoGostoso, Normalização Pura e Base Imutável para o Grafo

> **Componente do Projeto:** *Cook What U Have (MealMatch)*  
> **Responsabilidade:** Extrair as 15 receitas recomendadas de cada categoria do TudoGostoso, separar rigorosamente as transformações puras de dados do I/O impuro, sanitizar termos culinários para extração dos `ingredientes_centrais` e gerar a base imutável `pratos.json` para alimentação do Grafo Bipartido.

---

## 🎯 1. Arquitetura e Princípios Funcionais

O módulo de **Ingestão** foi reconstruído sob o padrão arquitetural **Functional Core, Imperative Shell** (Núcleo Funcional, Casca Imperativa):

```
       [ EFEITOS COLATERAIS / I/O ]                  [ TRANSFORMAÇÕES PURAS ]
               io_gateway.py                                parser.py
    (Requisição HTTP GET / Rede)   ── HTML bruto ──►  (Extração pura de dados)
                                                             │
                                                             ▼
               io_gateway.py                              normalizer.py
    (Persistência JSON / Disco)   ◄── ProcessedRecipe ─ (Limpeza pura e ingredientes canônicos)
```

1. **Separação Rígida de Responsabilidades:**
   - **`models.py`:** Entidades de dados 100% imutáveis (`NamedTuple`) usando `tuple` e `frozenset`.
   - **`normalizer.py`:** Pipeline puramente matemático de transformações encadeadas via `functools.reduce` para sanitização de strings, remoção de unidades/medidas e extração de termos canônicos (`extrair_ingrediente_central`).
   - **`parser.py`:** Análise sintática pura de strings HTML sem tocar na rede.
   - **`io_gateway.py`:** Única camada com efeitos colaterais de rede (`requests.get`) e disco (`json.dump`).
   - **`pipeline.py`:** Orquestrador declarativo que conecta as camadas usando funções de alta ordem (`map`, `filter`).

2. **Imutabilidade Total:**
   - Proibição categórica de métodos mutadores de coleção (`.append()`, `.extend()`, `.update()`).
   - Todos os dados fluem como tuplas e dicionários imutáveis por concepção.

---

## 📂 2. Estrutura Modular de Arquivos

```
ingestion/
├── __init__.py           # Identificador do pacote Python
├── models.py             # Entidades imutáveis: RawRecipe, ProcessedRecipe, CategoryTarget, CategoryResult
├── normalizer.py         # Pipeline funcional puro de normalização e extração de ingredientes centrais
├── parser.py             # Parser funcional puro de HTML e extração de links
├── io_gateway.py         # Casca isolada de E/S (chamadas de rede HTTP e persistência em disco)
├── pipeline.py           # Orquestrador funcional do pipeline de ponta a ponta
├── README.md             # Documentação do módulo de ingestão
└── data/                 # Diretório com as 8 categorias oficiais do TudoGostoso
    ├── aves/             # pratos.json (15 receitas)
    ├── bolos e tortas/   # pratos.json (15 receitas)
    ├── carnes/           # pratos.json (15 receitas)
    ├── doces e sobremesas/# pratos.json (15 receitas)
    ├── massas/           # pratos.json (15 receitas)
    ├── peixes e frutos do mar/ # pratos.json (15 receitas)
    ├── saladas e molhos/ # pratos.json (15 receitas)
    └── sopas/            # pratos.json (15 receitas)
```

---

## 📄 3. Estrutura Canônica de cada Receita no `pratos.json`

Cada receita gerada preserva as informações originais intactas para visualização e já projeta os ingredientes limpos para a álgebra de conjuntos do motor de grafos:

```json
[
  {
    "id": "massas_macarrao-a-carbonara_7b12d93e",
    "titulo": "Macarrão à carbonara",
    "tipo": "massas",
    "receita": [
      "Em uma panela, coloque a água e o sal para ferver...",
      "Frite o bacon até ficar crocante...",
      "Misture os ovos com o queijo ralado e a pimenta-do-reino...",
      "Junte a massa ainda quente e misture imediatamente."
    ],
    "ingredientes_originais": [
      "500 g de macarrão",
      "250 g de bacon em cubos",
      "1 caixa de creme de leite",
      "3 ovos",
      "Queijo ralado a gosto",
      "Pimenta-do-reino a gosto"
    ],
    "ingredientes_centrais": [
      "bacon",
      "creme de leite",
      "macarrao",
      "ovo",
      "pimenta do reino",
      "queijo"
    ]
  }
]
```

---

## 🚀 4. Como Executar a Geração da Base

A partir do diretório raiz do repositório (`cook-what-u-have/`):

### Gerar todas as 8 categorias (120 receitas):
```bash
.venv/bin/python -m ingestion.pipeline
```

### Gerar apenas uma categoria específica para testes rápidos (ex: Massas):
```bash
.venv/bin/python -m ingestion.pipeline massas
```
