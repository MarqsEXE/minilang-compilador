# Declaração de Uso de Inteligência Artificial Generativa

Em conformidade com a **Portaria CNPq nº 2.664/2026** e com as normas da disciplina de Linguagens Formais e Compiladores (UNIT), declaramos o uso de ferramenta de Inteligência Artificial generativa como apoio ao desenvolvimento deste projeto:

- **Ferramenta e Versão/Modelo:** Google Gemini (interface web — novembro de 2026).
- **Etapas em que foi empregada:**
  - **Fase 0 (Setup):** organização da estrutura inicial do repositório e modelos de documentação.
  - **Fase 1 (Definição Formal da Linguagem):** apoio na organização do alfabeto de tokens, rascunho da gramática EBNF e criação dos arquivos de exemplo (`programa_valido.ml` e `programa_invalido.ml`); justificativas formais redigidas pelo grupo.

  - **Fase 2 (Análise Léxica):** apoio na codificação do autômato finito determinístico em `src/lexer.py`, estruturação da tabela de transições em `docs/gramatica.md` e criação dos testes unitários de tokens válidos e inválidos; justificativa formal redigida pelo grupo.

  - **Fase 3 (Análise Sintática):** apoio na implementação do parser descendente recursivo LL(1) e da estrutura `ParseNode` em `src/parser.py`, além dos testes sintáticos; justificativas formais e comparação com análise LR redigidas pelo grupo.

  - **Fase 4 (Árvore Sintática Abstrata):** apoio na modelagem das classes de nós em `src/ast_nodes.py`, implementação de `parse_ast()` em `src/parser.py` e criação dos testes da AST; justificativa formal de preservação semântica redigida pelo grupo.

  - **Fase 5 (Análise Semântica e Interpretador):** apoio na implementação de `SymbolTable` e `Interpreter` em `src/interpreter.py`, bem como nos casos de teste semânticos; justificativas da tabela de símbolos e semântica operacional redigidas pelo grupo.

  - **Fase 6 (Catálogo de Erros e Diagnóstico):** apoio na organização das tabelas de erros (léxicos, sintáticos e semânticos) e na documentação dos cabeçalhos de testes inválidos; justificativa da estratégia de diagnóstico redigida pelo grupo.

- _(Atualizar progressivamente ao final de cada fase: Análise Léxica, Análise Sintática, AST, Interpretador, Catálogo de Erros, Testes e Revisão do Relatório)._

- **Finalidade específica de uso em cada etapa:**
  - Apoio na estruturação de arquivos de configuração e revisão estrutural de código e casos de teste.
  - Todas as definições formais (gramática EBNF, autômato finito determinístico, tabela de símbolos, semântica operacional e justificativas teóricas) foram construídas, validadas e revisadas integralmente pelos integrantes do grupo, com rastreamento detalhado em `docs/diario_de_bordo.md`.
