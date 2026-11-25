# Diário de Bordo — Projeto Compilador-Intérprete MiniLang

Registro semanal do processo de desenvolvimento, decisões técnicas da equipe e auditoria crítica do uso de IA generativa.

---

## Registro por Fase

### Fase 0 — Setup e Governança do Repositório (14/11/2026)

- **O que foi pedido à IA:** Criação da estrutura inicial de diretórios e arquivos base e template do diário de bordo conforme a especificação do projeto.
- **O que a IA gerou:** Árvore de pastas, e textos iniciais de governança.
- **O que foi aceito, reescrito ou descartado e por quê:** Estrutura de diretórios aceita integralmente por atender ao layout exigido. `README.md` e `declaracao_IA.md` foram ajustados para incluir os nomes dos três integrantes e a ferramenta utilizada.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro técnico nesta etapa de configuração.

### Fase 1 — Definição Formal da Linguagem MiniLang (15/11/2026)

- **O que foi pedido à IA:** Proposta de rascunho da gramática EBNF, alfabeto de tokens, tabela de precedência/associatividade, estrutura guiada para justificativas formais e programas de exemplo válidos e inválidos (incluindo laço mal formado).
- **O que a IA gerou:** Especificação inicial dos tokens, gramática EBNF sem recursão à esquerda e compatível com LL(1), tabela de 5 níveis de precedência, arquivos `exemplos/programa_valido.ml` e `exemplos/programa_invalido.ml`, além do roteiro com lacunas para as justificativas sem retornar respostas.
- **O que foi aceito, reescrito ou descartado e por quê:** Aceita a separação entre `expr_igualdade` (associativa à esquerda via `{ ... }`) e `expr_relacional` (não associativa via `[ ... ]`) para impedir comparações encadeadas como `a < b < c` diretamente na sintaxe. Todas as justificativas formais da Seção 4 e dos 6 exemplos foram redigidas integralmente pelo trio a partir dos conceitos da disciplina.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro técnico na gramática; ajustamos apenas o exemplo válido do enunciado para incluir `;` ao final de todos os comandos simples (`atribuicao` e `impressao`), mantendo consistência com a EBNF.

### Fase 2 — Análise Léxica / AFD (15/11/2026)

- **O que foi pedido à IA:** Implementação manual do lexer baseado em AFD em `src/lexer.py` (com linha/coluna e tratamento de `@`, `1x` e comentário não fechado), tabela de tokens, tabela de transições e testes unitários.
- **O que a IA gerou:** Classe `Lexer` com 11 estados explícitos (`q0` a `q10`), `TokenType`, `LexicalError`, tabela de transições em `docs/gramatica.md` e 9 casos de teste com `pytest`.
- **O que foi aceito, reescrito ou descartado e por quê:** A arquitetura de estados explícitos (`q0`..`q10`) foi aceita por corresponder à tabela de transições. O projeto mantém comentários de linha `//` como forma obrigatória e adiciona comentários de bloco `/* ... */` como extensão documentada: um bloco sem fechamento gera `LexicalError`. A justificativa formal da Seção 6.3 foi redigida pelo trio.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro lógico encontrado; validamos manualmente o comportamento de lookahead em `/` seguido de número (`x / 2`) e em `1x` (rejeitado em `q2` antes de avançar para o parser).

### Fase 3 — Análise Sintática / Parser Descendente Recursivo (15/11/2026)

- **O que foi pedido à IA:** Implementação manual do parser descendente recursivo preditivo LL(1) em `src/parser.py`, construção das árvores sintáticas concretas (`1 + 2 * 3`, `(1 + 2) * 3`, `while` e `for`), roteiro para justificativas formais e comparação com análise LR, além de testes unitários válidos e inválidos.
- **O que a IA gerou:** Classe `Parser` com métodos correspondentes a cada produção EBNF, estrutura `ParseNode` com método `pretty_print()`, exceção `MiniLangSyntaxError` com linha/coluna, árvores concretas na Seção 7 de `docs/gramatica.md` e 12 novos testes unitários.
- **O que foi aceito, reescrito ou descartado e por quê:** Aceita a correspondência direta 1-para-1 entre as produções da EBNF e os métodos `_parse_*`, bem como a separação explícita de `parse_cst()` para preservar a Árvore Sintática Concreta antes da abstração para AST na Fase 4. As justificativas da Seção 7.3 e a comparação entre LL(1) e LR/Shift-Reduce foram redigidas pelo trio.
- **Erros da IA encontrados e corrigidos pelo grupo:** Na suíte de testes sintáticos (`tests/invalidos/test_parser_invalido.py`), a IA fixou o número de linha literal (`assert exc_info.value.line == 5`) ao validar `exemplos/programa_invalido.ml`, causando falha de asserção (`assert 6 == 5`) devido ao cabeçalho de comentários do arquivo. O grupo corrigiu o teste para localizar dinamicamente a linha da instrução `for` no arquivo de exemplo e validar tanto o rastreamento de linha quanto a mensagem diagnóstica.

### Fase 4 — Árvore Sintática Abstrata / AST (15/11/2026)

- **O que foi pedido à IA:** Definição formal das classes de nós da AST (`WhileNode`, `ForNode` com três cláusulas, etc.), extensão do parser para gerar a AST diretamente, diagrama de programa com laço, roteiro para justificativa de preservação semântica (CST vs. AST) e testes unitários.
- **O que a IA gerou:** Módulo `src/ast_nodes.py` com 11 classes `dataclass` e método `pretty_print()`, método `parse_ast()` em `src/parser.py`, diagrama na Seção 8 de `docs/gramatica.md` e 6 novos testes em `tests/validos/test_ast.py`.
- **O que foi aceito, reescrito ou descartado e por quê:** Aceita a construção direta da AST no parser (`_ast_*`) em paralelo a `parse_cst()`, evitando duplicação de código e mantendo compatibilidade com os testes de CST da Fase 3. Confirmamos que cada nó da AST armazena `line` e `column` para suportar mensagens de erro semântico na Fase 5. A justificativa da Seção 8.3 foi redigida pelo trio.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro encontrado; validamos com `pytest` a igualdade estrutural das ASTs de `1 + 2 * 3`, `(1 + 2) * 3` e `ForNode`.

### Fase 5 — Tabela de Símbolos, Semântica Operacional e Interpretador (15/11/2026)

- **O que foi pedido à IA:** Implementação da tabela de símbolos (`insert`, `lookup`), do interpretador sobre a AST (`src/interpreter.py`), formalização da semântica operacional (especialmente `while` e `for`), verificação estrita de tipos e testes unitários válidos e inválidos.
- **O que a IA gerou:** Classes `SymbolTable`, `SymbolEntry`, `Interpreter`, `SemanticError`, ponto de entrada CLI (`python3 -m src.interpreter`), documentação da Seção 9 em `docs/gramatica.md` e 17 novos testes unitários.
- **O que foi aceito, reescrito ou descartado e por quê:** Aceita a distinção explícita entre `bool` e `int` (`isinstance(val, bool)` antes de `type(val) is int`) para evitar que booleanos em Python sejam tratados como inteiros `0`/`1` em somas ou comparações. Aceita também a ordem exata do `for` (`init` $\to$ `condition` $\to$ `body` $\to$ `update`) e o limite de iterações para proteção contra laços infinitos. A justificativa da Seção 9.3 foi redigida pelo.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro lógico encontrado; validamos a execução ponta a ponta do arquivo `exemplos/programa_valido.ml` via terminal e via `pytest`.

### Fase 6 — Catálogo de Erros e Estratégia de Diagnóstico (15/11/2026)

- **O que foi pedido à IA:** Estruturação do catálogo de erros (léxicos, sintáticos e semânticos, com pelo menos 3 casos por categoria, incluindo erros em laços), documentação dos resultados esperados no topo dos arquivos de teste em `tests/invalidos/` e roteiro guiado para a justificativa da estratégia de diagnóstico/recuperação.
- **O que a IA gerou:** Seção 10 em `docs/gramatica.md` com 13 erros catalogados (mensagem, causa formal e exemplo), comandos CLI de demonstração e cabeçalhos documentados nos 3 arquivos de testes inválidos.
- **O que foi aceito, reescrito ou descartado e por quê:** Aceita a padronização das mensagens com fase e coordenadas (`[linha X, coluna Y]`) e a documentação explícita no topo de `test_lexer_invalido.py`, `test_parser_invalido.py` e `test_interpreter_invalido.py`. A justificativa comparando a estratégia _Fail-Fast_ com o _Modo Pânico_ na Seção 10.5 foi redigida pelo trio.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro técnico; conferimos manualmente que todas as mensagens listadas nas tabelas da Seção 10 correspondem exatamente às strings emitidas por `src/lexer.py`, `src/parser.py` e `src/interpreter.py`.

### Fase 7 — Suíte Completa de Testes de Laços e Relatório Final (16/11/2026)

- **O que foi pedido à IA:** Criação dos testes de casos de borda para `while` e `for` (`0`, `1` e `N` iterações e alteração da variável de controle), testes de laço infinito com limite de iterações e estruturação do esqueleto do relatório final de 2 a 3 páginas.
- **O que a IA gerou:** Arquivos `tests/validos/test_lacos.py` (9 testes) e `tests/invalidos/test_laco_infinito.py` (4 testes), além do roteiro estruturado do relatório com seções de fundamentação teórica e análise crítica do uso de IA.
- **O que foi aceito, reescrito ou descartado e por quê:** Aceitos integralmente os 13 novos testes automatizados (totalizando 57 testes aprovados na suíte). O grupo preencheu as análises críticas, a comparação teórica e os exemplos concretos do diário de bordo antes de exportar o documento final para `docs/relatorio.pdf`.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro técnico nesta fase; validamos que os testes de laço infinito concluem em milissegundos graças ao parâmetro `max_iterations`.

---

---

## Registro semanal

### Semana 1 — 10/11/2026 a 16/11/2026

- **O que foi feito:** organização do repositório, definição da linguagem, gramática EBNF, implementação inicial do lexer e criação dos primeiros testes.
- **Uso de IA:** Google Gemini foi usado para rascunhos estruturais e testes, que foram revisados pelo trio.
- **Dificuldades:** alinhar maximal munch, posições de erro e comentários com a especificação formal.
- **Decisões:** definir exclusivamente `/` como divisão e manter `//` como comentário de linha; os comentários de bloco foram documentados como extensão adicional.

### Semana 2 — 17/11/2026 a 23/11/2026

- **O que foi feito:** consolidação do parser, AST, interpretador, tabela de símbolos, catálogo de erros e testes de laços.
- **Uso de IA:** auxílio na geração de esqueleto de código e de casos de teste; a equipe corrigiu problemas de linha, prioridade de operadores e divisão inteira.
- **Dificuldades:** diferenciar CST e AST, testar associatividade à esquerda e proteger laços infinitos.
- **Decisões:** manter escopo global, exceções tipadas por fase e limite configurável de iterações.

### Semana 3 — 24/11/2026 a 30/11/2026

- **O que foi feito:** revisão da documentação, geração do relatório PDF, ensaio do vídeo e verificação final em ambiente limpo.
- **Uso de IA:** aplicar IA somente como apoio de redação e revisão, com validação humana de toda afirmação técnica.
- **Dificuldades:** garantir que o relatório permaneça entre duas e três páginas e que os exemplos sejam verificáveis.
- **Decisões:** não considerar uma afirmação correta até que o código e os testes correspondentes tenham sido executados.

### Semana 4 — 01/12/2026

- **Entrega e apresentação:** publicação da versão final, gravação/apresentação do vídeo e preparação da arguição individual.
- **Uso de IA:** revisar o histórico e a declaração de IA, mantendo consistência entre README, declaração, diário e relatório.
- **Dificuldades:** explicar todos os itens individualmente e demonstrar execução ponta a ponta sem consulta durante a arguição.
- **Decisões:** cada integrante deve conhecer lexer, parser, AST, interpretador, testes e justificativas da IA.
