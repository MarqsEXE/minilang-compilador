# Especificação Formal da Linguagem MiniLang

## 1. Alfabeto (Tokens)

O alfabeto de símbolos terminais $\Sigma$ da MiniLang é dividido nas seguintes categorias léxicas:

1. **Palavras Reservadas (Keywords):**
   `if`, `else`, `while`, `for`, `print`, `true`, `false`
2. **Identificadores (`ID`):**
   Sequências iniciadas por letra (`a-z`, `A-Z`) ou sublinhado (`_`), seguidas de zero ou mais letras, dígitos (`0-9`) ou sublinhados, desde que não coincidam com palavras reservadas.
   - _Expressão regular:_ `[a-zA-Z_][a-zA-Z0-9_]*`
3. **Literais Inteiros (`INT_LITERAL`):**
   Sequências não vazias de dígitos decimais.
   - _Expressão regular:_ `[0-9]+`
4. **Operadores Aritméticos:**
   `+` (adição), `-` (subtração), `*` (multiplicação), `/` (divisão inteira)
5. **Operadores Relacionais e de Igualdade:**
   `<` (menor que), `>` (maior que), `<=` (menor ou igual), `>=` (maior ou igual), `==` (igual a), `!=` (diferente de)
6. **Operador de Atribuição:**
   `=`
7. **Delimitadores e Pontuação:**
   `(` (abre parênteses), `)` (fecha parênteses), `{` (abre bloco), `}` (fecha bloco), `;` (terminador de comando/cláusula)
8. **Símbolos Ignorados (Trivia Léxica):**
   - Espaços em branco, tabulações e quebras de linha: `[ \t\r\n]+`
   - Comentários de linha única: `//[^\n]*` (iniciam em `//` e seguem até o fim da linha ou `EOF`)
9. **Fim de Arquivo (`EOF`):**
   Marcador lógico de término da entrada.

---

## 2. Gramática Livre de Contexto (EBNF)

Na notação EBNF abaixo, `{ X }` representa zero ou mais repetições de `X` (Fecho de Kleene, usado para associatividade à esquerda), `[ X ]` representa zero ou uma ocorrência de `X` (opcional, usado para não associatividade ou `else` opcional), e strings entre aspas representam terminais literais.

````ebnf
programa        = { comando } EOF ;

comando         = atribuicao ";"
                | impressao ";"
                | condicional
                | laco_while
                | laco_for
                | bloco ;

atribuicao      = ID "=" expressao ;

impressao       = "print" "(" expressao ")" ;

condicional     = "if" "(" expressao ")" bloco [ "else" bloco ] ;

laco_while      = "while" "(" expressao ")" bloco ;

laco_for        = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco ;

bloco           = "{" { comando } "}" ;

expressao       = expr_igualdade ;

expr_igualdade  = expr_relacional { ( "==" | "!=" ) expr_relacional } ;

expr_relacional = expr_aritmetica [ ( "<" | ">" | "<=" | ">=" ) expr_aritmetica ] ;

expr_aritmetica = termo { ( "+" | "-" ) termo } ;

termo           = fator { ( "*" | "/" ) fator } ;

fator           = INT_LITERAL
                | "true"
                | "false"
                | ID
                | "(" expressao ")" ;

                | **Nível** | **Operadores / Construtos** | **Categoria** | **Associatividade** | **Não Terminal na EBNF** |

## 3. Tabela de Precedência e Associatividade

A hierarquia de precedência é garantida estruturalmente pela profundidade dos não terminais na gramática (quanto mais próximo de fator, maior a precedência):

| --- | --- | --- | --- | --- |
| **1 (Maior)** | `( ... )`, literais, `ID` | Agrupamento e átomos | — | `fator` |
| **2** | `*`, `/` | Multiplicativa | Esquerda (`{ ... }`) | `termo` |
| **3** | `+`, `-` | Aditiva | Esquerda (`{ ... }`) | `expr_aritmetica` |
| **4** | `<`, `>`, `<=`, `>=` | Relacional | Não associativa (`[ ... ]`) | `expr_relacional` |
| **5 (Menor)** | `==`, `!=` | Igualdade | Esquerda (`{ ... }`) | `expr_igualdade` |

## 4. Justificativas Formais da Gramática (Construção do Grupo)

### 4.1. Eliminação de Recursão à Esquerda e Associatividade

**Conceito:** Uma gramática recursiva à esquerda (ex.: $E \to E + T \mid T$) entra em loop infinito em analisadores descendentes recursivos. Ao reescrevê-la em EBNF como `expr_aritmetica = termo { ("+" | "-") termo }`, eliminamos a recursão direta à esquerda e preservamos o agrupamento à esquerda na construção da árvore.

**Redação do Grupo:**
> [PREENCHER PELO GRUPO: Explique com suas palavras por que a regra `termo = fator { ("*" | "/") fator }` não possui recursão à esquerda e como ela garante que `10 / 2 * 5` seja avaliado como `(10 / 2) * 5` e não `10 / (2 * 5)`. Explique também por que usamos `[ ... ]` (opcional) em `expr_relacional` em vez de `{ ... }`.]

---

### 4.2. Compatibilidade com Análise Preditiva LL(1)

**Conceito:** Uma gramática é LL(1) quando, para qualquer não terminal $A \to \alpha_1 \mid \alpha_2 \mid \dots \mid \alpha_n$, os conjuntos $\text{FIRST}(\alpha_i)$ são mutuamente disjuntos (e, se algum $\alpha_i \Rightarrow^* \varepsilon$, $\text{FIRST}(\alpha_j) \cap \text{FOLLOW}(A) = \emptyset$).

**Redação do Grupo:**
> [PREENCHER PELO GRUPO: Liste o conjunto FIRST de cada uma das 6 alternativas de `comando` (`atribuicao ";"`, `impressao ";"`, `condicional`, `laco_while`, `laco_for`, `bloco`) e demonstre que eles são disjuntos. Explique também por que exigir `bloco` (`{ ... }`) em `if` e `else` elimina a ambiguidade clássica do *dangling else*.]

## 5. Programas de Exemplo Comentados

### Exemplo 1 — Programa Válido Completo

```c
// Calcula o fatorial de 5 usando while e acumula pares usando for
n = 5;
fat = 1;

while (n > 1) {
    fat = fat * n;
    n = n - 1;
}

soma_pares = 0;
for (i = 0; i <= 6; i = i + 2) {
    soma_pares = soma_pares + i;
}

if (fat == 120) {
    print(fat + soma_pares);
} else {
    print(0);
}
````

**Classificação:** Válido (léxico, sintático e semântico).

**Justificativa do Grupo:**

> [PREENCHER PELO GRUPO: Indique quais produções da EBNF derivam os comandos acima e por que todas as restrições de tipo e escopo são satisfeitas.]

---

### Exemplo 2 — Inválido: Erro Léxico (Caractere Fora do Alfabeto e Token Mal Formado)

```c
taxa@ = 10;
1x = 20;
```

**Classificação:** Erro Léxico.

**Justificativa do Grupo:**

> [PREENCHER PELO GRUPO: Explique quais definições do alfabeto (Seção 1) foram violadas pelo símbolo `@` e pela sequência `1x` (por que `1x` não casa com `INT_LITERAL` nem com `ID`).]

---

### Exemplo 3 — Inválido: Erro Sintático em Expressão Aritmética

```c
x = (1 + ;
print(x);
```

**Classificação:** Erro Sintático.

**Justificativa do Grupo:**

> [PREENCHER PELO GRUPO: Aponte exatamente qual não terminal da gramática (`atribuicao -> expressao -> ... -> fator`) falha ao encontrar o token `;` logo após o operador `+`.]

---

### Exemplo 4 — Inválido: Erro Sintático em Laço Mal Formado

```c
for (i = 0; i < 10) {
    print(i);
}
```

**Classificação:** Erro Sintático (laço mal formado).

**Justificativa do Grupo:**

> [PREENCHER PELO GRUPO: Compare a entrada com a produção `laco_for = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco ;` e indique qual token esperado foi encontrado em falta antes de `)`.]

---

### Exemplo 5 — Inválido: Erro Semântico de Incompatibilidade de Tipos e Divisão por Zero

```c
flag = true;
resultado = 10 + flag;
quociente = 50 / 0;
```

**Classificação:** Erro Semântico.

**Justificativa do Grupo:**

> [PREENCHER PELO GRUPO: Explique por que a árvore sintática desse programa é validada pelo parser (pois `true` e `0` são `fator` válidos), mas rejeitada na análise semântica/interpretação.]

---

### Exemplo 6 — Inválido: Erro Semântico em Laço (Condição Não Booleana e Variável Não Definida)

```c
contador = 3;
while (contador) {
    contador = contador - 1;
}

for (k = 0; k < limite; k = k + 1) {
    print(k);
}
```

**Classificação:** Erro Semântico em Laço.

**Justificativa do Grupo:**

> [PREENCHER PELO GRUPO: Explique as duas violações semânticas presentes: (1) o tipo da expressão `contador` (`int`) na condição do `while`, e (2) a ausência da variável `limite` na tabela de símbolos durante a avaliação da condição do `for`.]

## 6. Análise Léxica (Lexer / AFD)

### 6.1. Tabela de Tokens

| Tipo de Token (`TokenType`) | Expressão Regular / Padrão                              | Exemplos                         |
| :-------------------------- | :------------------------------------------------------ | :------------------------------- |
| `IF`                        | `if`                                                    | `if`                             |
| `ELSE`                      | `else`                                                  | `else`                           |
| `WHILE`                     | `while`                                                 | `while`                          |
| `FOR`                       | `for`                                                   | `for`                            |
| `PRINT`                     | `print`                                                 | `print`                          |
| `TRUE`                      | `true`                                                  | `true`                           |
| `FALSE`                     | `false`                                                 | `false`                          |
| `ID`                        | `[a-zA-Z_][a-zA-Z0-9_]*` (exceto reservadas)            | `x`, `soma_pares`, `_aux1`       |
| `INT_LITERAL`               | `[0-9]+`                                                | `0`, `42`, `120`                 |
| `PLUS`                      | `\+`                                                    | `+`                              |
| `MINUS`                     | `-`                                                     | `-`                              |
| `STAR`                      | `\*`                                                    | `*`                              |
| `SLASH`                     | `/`                                                     | `/`                              |
| `LT`                        | `<`                                                     | `<`                              |
| `GT`                        | `>`                                                     | `>`                              |
| `LE`                        | `<=`                                                    | `<=`                             |
| `GE`                        | `>=`                                                    | `>=`                             |
| `EQ`                        | `==`                                                    | `==`                             |
| `NEQ`                       | `!=`                                                    | `!=`                             |
| `ASSIGN`                    | `=`                                                     | `=`                              |
| `LPAREN`                    | `\(`                                                    | `(`                              |
| `RPAREN`                    | `\)`                                                    | `)`                              |
| `LBRACE`                    | `\{`                                                    | `{`                              |
| `RBRACE`                    | `\}`                                                    | `}`                              |
| `SEMICOLON`                 | `;`                                                     | `;`                              |
| `EOF`                       | Fim da entrada                                          | `""` (fim de arquivo)            |
| _(Ignorado)_                | `[ \t\r\n]+` \| `//[^\n]*` \| `/\*([^*]\|\*+[^*/])*\*/` | espaços, `// obs`, `/* bloco */` |

---

### 6.2. Tabela de Transições do AFD ($\delta: Q \times \Sigma \to Q$)

Legenda de classes de caracteres:

- `WS`: espaço, `\t`, `\r`, `\n`
- `LET`: `[a-zA-Z_]`
- `DIG`: `[0-9]`
- `OP1`: `+`, `-`, `*`, `(`, `)`, `{`, `}`, `;`
- `OUTRO`: qualquer caractere válido que não continua o lexema atual (aciona lookahead / aceitação com retrocesso de 1 posição)

|  Estado   |      `WS`       |      `LET`      |      `DIG`      |      `OP1`      |       `/`       |       `*`       |      `=`       |       `<`       |       `>`       |       `!`       |      `\n`       |      `EOF`      |     `OUTRO`     | Ação / Aceitação                 |
| :-------: | :-------------: | :-------------: | :-------------: | :-------------: | :-------------: | :-------------: | :------------: | :-------------: | :-------------: | :-------------: | :-------------: | :-------------: | :-------------: | :------------------------------- |
| **`q0`**  |      `q0`       |      `q1`       |      `q2`       |  Aceita `OP1`   |      `q3`       |  Aceita `STAR`  |      `q4`      |      `q5`       |      `q6`       |      `q7`       |      `q0`       |  Aceita `EOF`   |    **Erro**     | Estado inicial                   |
| **`q1`**  |    Aceita\*     |      `q1`       |      `q1`       |    Aceita\*     |    Aceita\*     |    Aceita\*     |    Aceita\*    |    Aceita\*     |    Aceita\*     |    Aceita\*     |    Aceita\*     |    Aceita\*     |    Aceita\*     | `*`: busca em `KEYWORDS` ou `ID` |
| **`q2`**  |  Aceita `INT`   | **Erro** (`1x`) |      `q2`       |  Aceita `INT`   |  Aceita `INT`   |  Aceita `INT`   |  Aceita `INT`  |  Aceita `INT`   |  Aceita `INT`   |  Aceita `INT`   |  Aceita `INT`   |  Aceita `INT`   |  Aceita `INT`   | Aceita `INT_LITERAL`             |
| **`q3`**  | Aceita `SLASH`  | Aceita `SLASH`  | Aceita `SLASH`  | Aceita `SLASH`  |      `q8`       |      `q9`       | Aceita `SLASH` | Aceita `SLASH`  | Aceita `SLASH`  | Aceita `SLASH`  | Aceita `SLASH`  | Aceita `SLASH`  | Aceita `SLASH`  | `/` vs `//` vs `/*`              |
| **`q4`**  | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` |  Aceita `EQ`   | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | `=` vs `==`                      |
| **`q5`**  |   Aceita `LT`   |   Aceita `LT`   |   Aceita `LT`   |   Aceita `LT`   |   Aceita `LT`   |   Aceita `LT`   |  Aceita `LE`   |   Aceita `LT`   |   Aceita `LT`   |   Aceita `LT`   |   Aceita `LT`   |   Aceita `LT`   |   Aceita `LT`   | `<` vs `<=`                      |
| **`q6`**  |   Aceita `GT`   |   Aceita `GT`   |   Aceita `GT`   |   Aceita `GT`   |   Aceita `GT`   |   Aceita `GT`   |  Aceita `GE`   |   Aceita `GT`   |   Aceita `GT`   |   Aceita `GT`   |   Aceita `GT`   |   Aceita `GT`   |   Aceita `GT`   | `>` vs `>=`                      |
| **`q7`**  |    **Erro**     |    **Erro**     |    **Erro**     |    **Erro**     |    **Erro**     |    **Erro**     |  Aceita `NEQ`  |    **Erro**     |    **Erro**     |    **Erro**     |    **Erro**     |    **Erro**     |    **Erro**     | Exige `=` após `!`               |
| **`q8`**  |      `q8`       |      `q8`       |      `q8`       |      `q8`       |      `q8`       |      `q8`       |      `q8`      |      `q8`       |      `q8`       |      `q8`       |      `q0`       |      `q0`       |      `q8`       | Comentário `//`                  |
| **`q9`**  |      `q9`       |      `q9`       |      `q9`       |      `q9`       |      `q9`       |      `q10`      |      `q9`      |      `q9`       |      `q9`       |      `q9`       |      `q9`       |    **Erro**     |      `q9`       | Comentário `/*`                  |
| **`q10`** |      `q9`       |      `q9`       |      `q9`       |      `q9`       |      `q0`       |      `q10`      |      `q9`      |      `q9`       |      `q9`       |      `q9`       |      `q9`       |    **Erro**     |      `q9`       | Fecha `*/` ou volta `q9`         |

---

### 6.3. Justificativa Formal: Expressões Regulares $\leftrightarrow$ AFD $\leftrightarrow$ Lexer (Construção do Grupo)

- **Conceito:** Pelo Teorema de Kleene, toda linguagem regular descrita por uma Expressão Regular pode ser reconhecida por um Autômato Finito Determinístico (AFD). Na implementação prática de um lexer, a união das ERs de todos os tokens forma um único AFD com dois mecanismos adicionais: (1) **regra do casamento mais longo (_maximal munch_)**, que continua consumindo caracteres enquanto houver transição válida (evitando que `==` vire dois `=` ou `while` vire `ID`), e (2) **prioridade de palavras reservadas**, que consulta a tabela `KEYWORDS` ao final do estado `q1` em vez de criar dezenas de estados exclusivos no autômato.
- **Redação do Grupo (base também para a seção "Análise Léxica" de `docs/relatorio.pdf`):**
  > [PREENCHER PELO GRUPO: Explique com suas palavras:
  >
  > 1. Como o AFD resolve o conflito de prefixo entre operadores simples (`=`, `<`, `>`, `/`) e compostos (`==`, `<=`, `>=`, `//`, `/*`) usando estados intermediários (`q3` a `q6`) e lookahead (`_peek()`).
  > 2. Por que tratar palavras reservadas (`while`, `for`, `if`) via dicionário `KEYWORDS` após o estado `q1` reduz o número de estados do AFD sem alterar a linguagem regular reconhecida.
  > 3. Como os estados de erro no AFD (como `q2` ao ler letra após dígito em `1x`, ou `q9`/`q10` ao atingir `EOF`) garantem que o lexer reconheça **exatamente** os tokens válidos da MiniLang e rejeite cadeias fora da linguagem.]

---

## 7. Análise Sintática (Parser Descendente Recursivo LL(1))

### 7.1. Árvores Sintáticas Concretas de Precedência: `1 + 2 * 3` vs. `(1 + 2) * 3`

#### Árvore 1: `1 + 2 * 3`

```text
expressao
  expr_igualdade
    expr_relacional
      expr_aritmetica
        termo
          fator
            INT_LITERAL ('1')
        PLUS ('+')
        termo
          fator
            INT_LITERAL ('2')
          STAR ('*')
          fator
            INT_LITERAL ('3')
```

#### Árvore 2: `1 + 2 * 3`

```text
expressao
  expr_igualdade
    expr_relacional
      expr_aritmetica
        termo
          fator
            LPAREN ('(')
            expressao
              expr_igualdade
                expr_relacional
                  expr_aritmetica
                    termo
                      fator
                        INT_LITERAL ('1')
                    PLUS ('+')
                    termo
                      fator
                        INT_LITERAL ('2')
            RPAREN (')')
          STAR ('*')
          fator
            INT_LITERAL ('3')
```

### 7.2 Árvores Sintáticas Concretas de Laços (while e for)

#### Árvore do Laço while (x < 10) { x = x + 1; }

```text
laco_while
  WHILE ('while')
  LPAREN ('(')
  expressao
    expr_igualdade
      expr_relacional
        expr_aritmetica -> termo -> fator -> ID ('x')
        LT ('<')
        expr_aritmetica -> termo -> fator -> INT_LITERAL ('10')
  RPAREN (')')
  bloco
    LBRACE ('{')
    comando
      atribuicao
        ID ('x')
        ASSIGN ('=')
        expressao -> ... -> expr_aritmetica (x + 1)
      SEMICOLON (';')
    RBRACE ('}')
```

#### Árvore do Laço for (i = 0; i < 10; i = i + 1) { print(i); }

```text
laco_for
  FOR ('for')
  LPAREN ('(')
  atribuicao                          <-- [1ª Cláusula: Inicialização obrigatório]
    ID ('i')
    ASSIGN ('=')
    expressao -> ... -> INT_LITERAL ('0')
  SEMICOLON (';')
  expressao                           <-- [2ª Cláusula: Condição booleana obrigatória]
    expr_igualdade
      expr_relacional
        expr_aritmetica -> ... -> ID ('i')
        LT ('<')
        expr_aritmetica -> ... -> INT_LITERAL ('10')
  SEMICOLON (';')
  atribuicao                          <-- [3ª Cláusula: Atualização obrigatória]
    ID ('i')
    ASSIGN ('=')
    expressao -> ... -> expr_aritmetica (i + 1)
  RPAREN (')')
  bloco                               <-- [Corpo do laço]
    LBRACE ('{')
    comando
      impressao
        PRINT ('print')
        LPAREN ('(')
        expressao -> ... -> ID ('i')
        RPAREN (')')
      SEMICOLON (';')
    RBRACE ('}')
```

## 7.3. Justificativas Formais da Análise Sintática (Construção do Grupo)

### A) Diferença entre as Árvores de `1 + 2 * 3` e `(1 + 2) * 3` (Precedência e Associatividade)

- **Conceito:** Em `1 + 2 * 3`, a multiplicação `2 * 3` fica aninhada mais profundamente sob `termo`, sendo reduzida antes da soma em `expr_aritmetica`. Em `(1 + 2) * 3`, os parênteses na produção `fator = "(" expressao ")"` reiniciam a derivação do topo da hierarquia, forçando `1 + 2` a ser agrupado dentro de `fator` antes da multiplicação externa.
- **Redação do Grupo (para `docs/relatorio.pdf`):**
  > [PREENCHER PELO GRUPO: Explique com suas palavras por que as duas árvores acima têm alturas e agrupamentos diferentes, e como os laços `while` dentro de `_parse_expr_aritmetica` e `_parse_termo` garantem associatividade à esquerda em expressões como `10 - 3 - 2`.]

---

### B) Tratamento de `while` e `for` e Rejeição de Entradas Inválidas

- **Conceito:** Como `while` e `for` começam por palavras reservadas exclusivas (`WHILE` e `FOR`), `_parse_comando` despacha imediatamente para `_parse_laco_while` e `_parse_laco_for` com 1 token de _lookahead_. No `for`, as chamadas sequenciais `_parse_atribuicao()` $\to$ `_expect(SEMICOLON)` $\to$ `_parse_expressao()` $\to$ `_expect(SEMICOLON)` $\to$ `_parse_atribuicao()` impõem estruturalmente as três cláusulas obrigatórias.
- **Redação do Grupo (para `docs/relatorio.pdf`):**
  > [PREENCHER PELO GRUPO: Explique passo a passo o que ocorre no parser ao processar `x = (1 + ;` e `for (i = 0; i < 10) { ... }`, indicando exatamente qual método falha e qual token era esperado vs. encontrado.]

---

### C) Comparação: Descendente Recursivo LL(1) vs. Análise Ascendente LR (Shift-Reduce)

- **Conceito:** Enquanto o parser descendente recursivo (_top-down_ LL(1)) parte do símbolo inicial `programa` tentando derivar a entrada usando a pilha de chamadas da linguagem hospedeira, um parser ascendente LR (_bottom-up_ _shift-reduce_, como SLR/LALR) empilha tokens (_shift_) e os reduz (_reduce_) ao lado esquerdo das produções usando autômatos de itens LR e tabelas `ACTION`/`GOTO`.
- **Redação do Grupo (para `docs/relatorio.pdf`):**
  > [PREENCHER PELO GRUPO: Compare as vantagens e limitações das duas abordagens (legibilidade do código manual, facilidade de gerar mensagens de erro sintático contextualizadas no LL(1) vs. maior poder expressivo de gramáticas com recursão à esquerda no LR) e justifique por que o grupo escolheu o descendente recursivo LL(1) para a MiniLang.]

---

## 8. Árvore Sintática Abstrata (AST)

### 8.1. Especificação dos Nós (`src/ast_nodes.py`)

| Classe AST | Superclasse | Campos Principais | Papel Semântico |
| :--- | :--- | :--- | :--- |
| `ProgramNode` | `ASTNode` | `statements: List[Statement]` | Raiz do programa; lista ordenada de comandos. |
| `AssignNode` | `Statement` | `name: str`, `value: Expression` | Atualiza/cria entrada na tabela de símbolos. |
| `PrintNode` | `Statement` | `expression: Expression` | Avalia expressão e emite valor na saída. |
| `BlockNode` | `Statement` | `statements: List[Statement]` | Sequência de comandos internos a `{ ... }`. |
| `IfNode` | `Statement` | `condition`, `then_block`, `else_block` | Desvio condicional com ramo `else` opcional. |
| `WhileNode` | `Statement` | `condition: Expression`, `body: BlockNode` | Repetição controlada por expressão booleana. |
| `ForNode` | `Statement` | `init`, `condition`, `update`, `body` | Laço contado com 3 cláusulas obrigatórias. |
| `BinaryOpNode` | `Expression` | `left`, `operator: str`, `right` | Operação binária aritmética, relacional ou igualdade. |
| `IntLiteralNode` | `Expression` | `value: int` | Valor inteiro constante já convertido para `int`. |
| `BoolLiteralNode` | `Expression` | `value: bool` | Valor booleano constante (`True` ou `False`). |
| `VarNode` | `Expression` | `name: str` | Leitura do valor associado ao identificador. |

---

### 8.2. Diagrama da AST de um Programa Completo com Laço

Considere o programa MiniLang:
```minilang
soma = 0;
for (i = 0; i < 3; i = i + 1) {
    soma = soma + i;
}
print(soma);

### 8.3. Justificativa Formal: Preservação Semântica ($\text{CST} \to \text{AST}$) *(Construção do Grupo)*

**Conceito:** A Árvore Sintática Concreta (CST) registra o processo de derivação gramatical completo (como uma palavra foi reconhecida), enquanto a Árvore Sintática Abstrata (AST) representa apenas a estrutura hierárquica necessária para interpretar o significado do programa.

#### Redação do Grupo *(base para `docs/relatorio.pdf`)*:

> **[PREENCHER PELO GRUPO:** Explique com suas palavras:
> 
> * Quais elementos presentes na CST são eliminados na AST (`;`, `(`, `)`, `{`, `}`, palavras-chave redundantes como `for`/`while`, e nós intermediários como `termo`, `fator`, `expr_aritmetica`).
> * Por que remover os parênteses `(` e `)` na AST de `(1 + 2) * 3` não perde informação de precedência (como a própria estrutura pai-filho dos `BinaryOpNode` preserva a ordem de avaliação).
> * Como os campos explícitos de `WhileNode` (`condition`, `body`) e `ForNode` (`init`, `condition`, `update`, `body`) preservam integralmente a semântica de execução dos laços da MiniLang.**]**