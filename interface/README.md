# 🖥️ Módulo de Interface do Usuário e Adaptadores de E/S (`interface/`)
### Camada de Interação, Bordas de Efeitos Colaterais e Formatação Declarativa

> **Componente do Projeto:** *Cook What U Have (MealMatch)*  
> **Responsabilidade:** Gerenciar a interação com o usuário via terminal (CLI), carregar a base de dados dos pratos a partir do disco e formatar relatórios visuais claros, isolando os efeitos colaterais (*I/O Boundaries*) do núcleo puro do sistema.

---

## 🎯 1. Arquitetura e Princípio de Bordas de E/S (*I/O Boundaries*)

Na arquitetura de sistemas funcionais, o domínio algorítmico (`implementation/`) permanece 100% puro e sem contato com o mundo externo. O módulo `interface/` desempenha o papel de **casca protetora (*Functional Core, Imperative Shell*)**:

```
[ BORDAS DE EFEITOS COLATERAIS ]                   [ NÚCLEO FUNCIONAL PURO ]
           cli.py / io_adapter.py                         implementation/
  (Teclado / Disco / Terminal)   ── frozenset / Dish ──►  (Grafo Bipartido)
                                                                 │
                                                                 ▼
           formatter.py                                   MatchResult
  (Formatação visual declarativa) ◄──────────────────────────────┘
```

1. **Sem Instruções Imperativas `def`:** Toda a lógica de carga, conversão e formatação foi concebida através de **funções lambda de primeira ordem** e encadeamento funcional puro.
2. **Coleta e Conversão Segura:** Converte entradas do teclado diretamente para conjuntos imutáveis `frozenset`.
3. **Carga em Lote Controlada:** Lê os arquivos `pratos.json` das 8 categorias em `ingestion/data/` e instancia as entidades congeladas `Dish`.
4. **Formatação Declarativa:** Projeta os nós recomendados em cards visuais no terminal, destacando itens em posse do usuário, a lista de compras automática e os pratos bloqueados por segurança alimentar.

---

## 📂 2. Estrutura Modular da Pasta

```
interface/
├── __init__.py           # Exportação dos componentes da interface
├── io_adapter.py         # Leitura pura dos JSONs do disco -> tuple[Dish, ...]
├── formatter.py          # Projeção pura: MatchResult -> texto formatado
├── cli.py                # Ponto de entrada interativo no console
└── README.md             # Documentação técnica da camada de interface
```

---

## 🚀 3. Como Executar a Interface Interativa

A partir da raiz do repositório (`cook-what-u-have/`):

```bash
.venv/bin/python -m interface.cli
```

### Exemplo de Uso Interativo no Console:
```text
================================================================================
🍳 COOK WHAT U HAVE — SISTEMA FUNCIONAL DE RECOMENDAÇÃO DE REFEIÇÕES
================================================================================
Base de dados: 120 pratos carregados em memória.

1. Ingredientes na sua despensa (separados por vírgula): ovo, cebola, bacon, queijo
2. Alérgenos a banir com tolerância zero (ou Enter para nenhum): camarao
3. Quantidade máxima de ingredientes em falta aceitável (padrão 0): 2
4. Categoria culinária (ou Enter para buscar em todas as 8): massas
```
