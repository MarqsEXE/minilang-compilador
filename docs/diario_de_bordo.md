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

---

### Template para as Próximas Fases

```markdown
### Fase X — [Nome da Fase] (DD/MM/2026)

- **O que foi pedido à IA:**
- **O que a IA gerou:**
- **O que foi aceito, reescrito ou descartado e por quê:**
- **Erros da IA encontrados e corrigidos pelo grupo (conceito teórico envolvido):**
```

