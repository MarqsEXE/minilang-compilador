# Diário de Bordo — Projeto Compilador-Intérprete MiniLang

Registro semanal do processo de desenvolvimento, decisões técnicas da equipe e auditoria crítica do uso de IA generativa.

---

## Registro por Fase

### Fase 0 — Setup e Governança do Repositório (14/11/2026)

- **O que foi pedido à IA:** Criação da estrutura inicial de diretórios e arquivos base e template do diário de bordo conforme a especificação do projeto.
- **O que a IA gerou:** Árvore de pastas, e textos iniciais de governança.
- **O que foi aceito, reescrito ou descartado e por quê:** Estrutura de diretórios aceitos integralmente por atenderem exatamente ao layout exigido. `README.md` e `declaração_IA.md` ajustados para incluir os nomes dos três integrantes do grupo e a versão exata da ferramenta utilizada.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro técnico nesta etapa de configuração.

### Fase 1 — Definição Formal da Linguagem MiniLang (15/11/2026)

- **O que foi pedido à IA:** Proposta de rascunho da gramática EBNF, alfabeto de tokens, tabela de precedência/associatividade, estrutura guiada para justificativas formais e programas de exemplo válidos e inválidos (incluindo laço mal formado).
- **O que a IA gerou:** Especificação inicial dos tokens, gramática EBNF sem recursão à esquerda e compatível com LL(1), tabela de 5 níveis de precedência, arquivos `exemplos/programa_valido.ml` e `exemplos/programa_invalido.ml`, além do roteiro com lacunas para as justificativas sem retornar respostas.
- **O que foi aceito, reescrito ou descartado e por quê:** Aceita a separação entre `expr_igualdade` (associativa à esquerda via `{ ... }`) e `expr_relacional` (não associativa via `[ ... ]`) para impedir comparações encadeadas como `a < b < c` diretamente na sintaxe. Todas as justificativas formais da Seção 4 e dos 6 exemplos foram redigidas integralmente pelo trio a partir dos conceitos da disciplina.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro técnico na gramática; ajustamos apenas o exemplo válido do enunciado para incluir `;` ao final de todos os comandos simples (`atribuicao` e `impressao`), mantendo consistência com a EBNF.

### Fase 2 — Análise Léxica / AFD (15/11/2026)

- **O que foi pedido à IA:** Implementação manual do lexer baseado em AFD em `src/lexer.py` (com linha/coluna e tratamento de `@`, `1x` e comentário não fechado), tabela de tokens, tabela de transições e testes unitários.
- **O que a IA gerou:** Classe `Lexer` com 11 estados explícitos (`q0` a `q10`), `TokenType`, `LexicalError`, tabela de transições em `docs/gramatica.md` e 9 casos de teste com `pytest`.
- **O que foi aceito, reescrito ou descartado e por quê:** Aceita a arquitetura de estados explícitos (`q0`..`q10`) pela correspondência direta 1-para-1 com a tabela de transições do relatório. Incluímos suporte a comentários de bloco `/* ... */` (além de `//`) para viabilizar o diagnóstico formal de comentário não fechado no AFD (`q9`/`q10`). A justificativa formal da Seção 6.3 foi redigida pelo trio.
- **Erros da IA encontrados e corrigidos pelo grupo:** Nenhum erro lógico encontrado; validamos manualmente o comportamento de lookahead em `/` seguido de número (`x / 2`) e em `1x` (rejeitado em `q2` antes de avançar para o parser).

---

### Template para as Próximas Fases

```markdown
### Fase X — [Nome da Fase] (DD/MM/2026)

- **O que foi pedido à IA:**
- **O que a IA gerou:**
- **O que foi aceito, reescrito ou descartado e por quê:**
- **Erros da IA encontrados e corrigidos pelo grupo (conceito teórico envolvido):**
```
