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
   - Comentários de bloco: `/\*([^*]|\*+[^*/])*\*/` (extensão adicional, encerrada no primeiro `*/`; não são aninháveis)
   - Um comentário de bloco sem fechamento antes de `EOF` gera `LexicalError`.
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
````
## 3. Tabela de Precedência e Associatividade

A hierarquia de precedência é garantida estruturalmente pela profundidade dos não terminais na gramática (quanto mais próximo de fator, maior a precedência):

| Precedência | Operadores | Categoria | Associatividade | Não terminal |
| :--- | :--- | :--- | :--- | :--- |
| **1 (Maior)** | `( ... )`, literais, `ID` | Agrupamento e átomos | — | `fator` |
| **2** | `*`, `/` | Multiplicativa | Esquerda (`{ ... }`) | `termo` |
| **3** | `+`, `-` | Aditiva | Esquerda (`{ ... }`) | `expr_aritmetica` |
| **4** | `<`, `>`, `<=`, `>=` | Relacional | Não associativa (`[ ... ]`) | `expr_relacional` |
| **5 (Menor)** | `==`, `!=` | Igualdade | Esquerda (`{ ... }`) | `expr_igualdade` |

## 4. Justificativas Formais da Gramática (Construção do Grupo)

### 4.1. Eliminação de Recursão à Esquerda e Associatividade

**Conceito:** Uma gramática recursiva à esquerda (ex.: $E \to E + T \mid T$) entra em loop infinito em analisadores descendentes recursivos. Ao reescrevê-la em EBNF como `expr_aritmetica = termo { ("+" | "-") termo }`, eliminamos a recursão direta à esquerda e preservamos o agrupamento à esquerda na construção da árvore.

**Redação do Grupo:**
> Em `termo = fator { ("*" | "/") fator }`, o símbolo à esquerda do primeiro fator é sempre o próprio fator; o fator não deriva recursivamente de `termo`. Assim, não existe uma derivação que comece por `termo -> termo "*" fator`, condição que faria o analisador entrar em recursão à esquerda. Cada operador multiplicativo é anexado à esquerda pela repetição do bloco: `10 / 2 * 5` torna-se `((10 / 2) * 5)`. O mesmo princípio vale para `+` e `-`. Em `expr_relacional`, usamos `[ oper_rel aritmetica ]`, não `{ ... }`, porque a gramática permite no máximo uma comparação. Dessa forma, `a < b < c` não pode ser derivado como uma expressão relacional encadeada.

---

### 4.2. Compatibilidade com Análise Preditiva LL(1)

**Conceito:** Uma gramática é LL(1) quando, para qualquer não terminal $A \to \alpha_1 \mid \alpha_2 \mid \dots \mid \alpha_n$, os conjuntos $\text{FIRST}(\alpha_i)$ são mutuamente disjuntos (e, se algum $\alpha_i \Rightarrow^* \varepsilon$, $\text{FIRST}(\alpha_j) \cap \text{FOLLOW}(A) = \emptyset$).

**Redação do Grupo:**
> As seis alternativas de `comando` têm conjuntos FIRST disjuntos:
> `FIRST(atribuicao ";") = {ID}`, `FIRST(impressao ";") = {PRINT}`, `FIRST(condicional) = {IF}`, `FIRST(laco_while) = {WHILE}`, `FIRST(laco_for) = {FOR}` e `FIRST(bloco) = {{}}`. Esses conjuntos não se interceptam, permitindo a seleção da produção pelo próximo token. Como `if` e `else` exigem um `bloco` delimitado por chaves, não há corpo sem bloco pendente de associação. Assim, o *dangling else* não pode ocorrer: o `else` que segue um bloco pertence diretamente ao `if` mais próximo cuja estrutura já foi fechada.

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
> `n = 5`, `fat = 1` e `soma_pares = 0` são derivações de `atribuicao ";"`. `while` deriva pela produção `laco_while`; seu corpo contém atribuições válidas. `for` deriva por `laco_for`, com inicialização `i = 0`, condição `i <= 6` e atualização `i = i + 2`, todas obrigatórias e com tipos compatíveis. `if (fat == 120)` deriva de `condicional`, e os dois ramos são blocos. Todas as variáveis são inicialmente criadas antes do uso, as condições são booleanas e a expressão aritmética respeita a precedência da EBNF.

---

### Exemplo 2 — Inválido: Erro Léxico (Caractere Fora do Alfabeto e Token Mal Formado)

```c
taxa@ = 10;
1x = 20;
```

**Classificação:** Erro Léxico.

**Justificativa do Grupo:**
> O símbolo `@` não pertence às classes de `WS`, `LET`, `DIG`, operadores ou delimitadores e, portanto, não possui transição no estado inicial do lexer. A sequência `1x` começa em um estado de inteiro `[0-9]+`, mas encontra uma letra sem um delimitador. Ela não pode formar `INT_LITERAL`, pois essa expressão termina antes da letra, e também não pode formar `ID`, cuja expressão exige uma letra ou `_` como primeiro caractere.

---

### Exemplo 3 — Inválido: Erro Sintático em Expressão Aritmética

```c
x = (1 + ;
print(x);
```

**Classificação:** Erro Sintático.

**Justificativa do Grupo:**
> `x = (1 + ;` corresponde inicialmente à produção `atribuicao = ID "=" expressao`. Dentro dos parênteses, `_parse_expressao()` chega a `expr_aritmetica -> termo -> fator`. Depois de consumir `+`, `_parse_termo()` espera um novo `fator`; o próximo token é `;`, que não pertence ao FIRST de `fator`. O método `_parse_fator()` lança `MiniLangSyntaxError` em `_parse_expressao()`, antes que `_parse_comando()` possa completar a atribuição.

---

### Exemplo 4 — Inválido: Erro Sintático em Laço Mal Formado

```c
for (i = 0; i < 10) {
    print(i);
}
```

**Classificação:** Erro Sintático (laço mal formado).

**Justificativa do Grupo:**
> A entrada contém inicialização (`i = 0`) e condição (`i < 10`), mas chega ao token `)` sem o segundo `;` e sem uma terceira atribuição. Ela viola `laco_for = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco`. O parser encontra `)` durante `_parse_laco_for()` enquanto tenta esperar o `SEMICOLON` que separa a condição da atualização obrigatória; por isso informa que a cláusula de atualização está ausente.

---

### Exemplo 5 — Inválido: Erro Semântico de Incompatibilidade de Tipos e Divisão por Zero

```c
flag = true;
resultado = 10 + flag;
quociente = 50 / 0;
```

**Classificação:** Erro Semântico.

**Justificativa do Grupo:**
> O parser aceita `true` e `0` como alternativas válidas de `fator`, e reconhece `10 + flag` e `50 / 0` como expressões sintaticamente completas. Na semântica, `+` exige dois valores inteiros e encontra `int` com `bool`; além disso, o divisor avaliado em `/` é zero, operação fora do domínio da divisão inteira. Cada violação é detectada pelo interpretador por meio da inspeção de tipos e do valor do operando direito.

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
> Na primeira instrução, `contador` foi atribuído o valor inteiro `3`; `while` exige uma expressão cujo valor seja `bool`, portanto a condição viola a restrição semântica do laço. Na segunda instrução, `i` recebe `0`, mas `limite` nunca é inserido na tabela de símbolos. Ao avaliar `i < limite`, `_eval_expression()` solicita `limite` e `SymbolTable.lookup()` lança `SemanticError` por variável não definida.

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

O comentário `//` é a forma exigida pelo escopo obrigatório: começa em `//` e termina na quebra
de linha ou em `EOF`. Comentários de bloco `/* ... */` são uma extensão adicional, encerrada no
primeiro `*/` (não são aninháveis); se não houver fechamento antes de `EOF`, o lexer gera
`LexicalError`.

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

Os comentários de bloco `/* ... */` são uma extensão adicional, encerrada no primeiro `*/`
(não são aninháveis); se não houver fechamento antes de `EOF`, o lexer gera `LexicalError`.
Assim, `q9` e `q10` não aceitam `EOF`: essa transição produz o erro de comentário não fechado.

---

### 6.3. Justificativa Formal: Expressões Regulares $\leftrightarrow$ AFD $\leftrightarrow$ Lexer (Construção do Grupo)

- **Conceito:** Pelo Teorema de Kleene, toda linguagem regular descrita por uma Expressão Regular pode ser reconhecida por um Autômato Finito Determinístico (AFD). Na implementação prática de um lexer, a união das ERs de todos os tokens forma um único AFD com dois mecanismos adicionais: (1) **regra do casamento mais longo (_maximal munch_)**, que continua consumindo caracteres enquanto houver transição válida (evitando que `==` vire dois `=` ou `while` vire `ID`), e (2) **prioridade de palavras reservadas**, que consulta a tabela `KEYWORDS` ao final do estado `q1` em vez de criar dezenas de estados exclusivos no autômato.
- **Justificativa do Grupo:**
  > Para operadores com prefixo comum, o estado inicial envia `=`, `<`, `>` e `/` para estados intermediários `q4` a `q7`. Nesses estados, `_peek()` olha o próximo caractere: `==`, `<=`, `>=` e `!=` são emitidos como um único token composto; caso não haja o sufixo correspondente, é emitido o operador simples ou lançado erro. Após `/`, o estado `q3` separa divisão, comentário de linha `//` e a extensão de bloco `/*`.
  >
  > Palavras reservadas são reconhecidas pela expressão regular de identificador em `q1` e, ao fechar o lexema, consultadas em `KEYWORDS`. Isso evita estados separados para cada reservada sem alterar a linguagem reconhecida: `whilex` continua sendo `ID`, enquanto `while` vira `WHILE`.
  >
  > O estado `q2` aceita somente dígitos e rejeita ao encontrar letra ou sublinhado, produzindo o erro de `1x`. Os estados `q9` e `q10` reconhecem a extensão de comentário de bloco; alcançar `EOF` nesses estados indica comentário não fechado. Essa construção distingue exatamente os tokens declarados e rejeita caracteres fora das transições.

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
  > As duas CSTs diferem porque a primeira deriva `2 * 3` dentro de `termo`, enquanto a segunda deriva `1 + 2` dentro de `fator` após encontrar `(`. Os parênteses reiniciam `expressao`, alterando explicitamente a ordem das derivações. Em `_parse_expr_aritmetica()` e `_parse_termo()`, os blocos `while` leem repetidamente operadores e operandos; cada iteração constrói o nó combinado à esquerda. Assim, `10 - 3 - 2` é analisado como `(10 - 3) - 2`, e `10 / 2 * 5` como `(10 / 2) * 5`.

---

### B) Tratamento de `while` e `for` e Rejeição de Entradas Inválidas

- **Conceito:** Como `while` e `for` começam por palavras reservadas exclusivas (`WHILE` e `FOR`), `_parse_comando` despacha imediatamente para `_parse_laco_while` e `_parse_laco_for` com 1 token de _lookahead_. No `for`, as chamadas sequenciais `_parse_atribuicao()` $\to$ `_expect(SEMICOLON)` $\to$ `_parse_expressao()` $\to$ `_expect(SEMICOLON)` $\to$ `_parse_atribuicao()` impõem estruturalmente as três cláusulas obrigatórias.
- **Redação do Grupo (para `docs/relatorio.pdf`):**
  > Ao processar `x = (1 + ;`, `_parse_atribuicao()` chega a `_parse_expressao()`, passa por `_parse_termo()` e tenta `_parse_fator()` após `+`; encontra `;` e lança `MiniLangSyntaxError`, informando que esperava um fator. Ao processar `for (i = 0; i < 10)`, `_parse_laco_for()` consome a inicialização, espera `;`, consome a condição e espera o segundo `;`; encontra `)` e gera erro antes da atualização, indicando que a terceira cláusula é obrigatória.

---

### C) Comparação: Descendente Recursivo LL(1) vs. Análise Ascendente LR (Shift-Reduce)

- **Conceito:** Enquanto o parser descendente recursivo (_top-down_ LL(1)) parte do símbolo inicial `programa` tentando derivar a entrada usando a pilha de chamadas da linguagem hospedeira, um parser ascendente LR (_bottom-up_ _shift-reduce_, como SLR/LALR) empilha tokens (_shift_) e os reduz (_reduce_) ao lado esquerdo das produções usando autômatos de itens LR e tabelas `ACTION`/`GOTO`.
- **Redação do Grupo (para `docs/relatorio.pdf`):**
  > A descida recursiva foi escolhida porque a gramática foi fatorada em não terminais por nível de precedência e possui tokens de despacho distintos. Suas funções são legíveis, correspondem às produções e permitem erros contextualizados. As técnicas LR, como SLR ou LALR, conseguem tratar gramáticas mais expressivas e algumas recursões à esquerda, mas exigem tabelas geradas e tornam o fluxo de diagnóstico menos direto em um projeto didático. Como a gramática da MiniLang cabe em um parser preditivo LL(1), não se justificou o custo adicional de uma tabela LR.

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
```

```text
ProgramNode
  AssignNode(var="soma")
    IntLiteralNode(0)
  ForNode
    [init]
      AssignNode(var="i")
        IntLiteralNode(0)
    [condition]
      BinaryOpNode(op="<")
        VarNode("i")
        IntLiteralNode(3)
    [update]
      AssignNode(var="i")
        BinaryOpNode(op="+")
          VarNode("i")
          IntLiteralNode(1)
    [body]
      BlockNode
        AssignNode(var="soma")
          BinaryOpNode(op="+")
            VarNode("soma")
            VarNode("i")
  PrintNode
    VarNode("soma")
```

### 8.3. Justificativa Formal: Preservação Semântica ($\text{CST} \to \text{AST}$) *(Construção do Grupo)*

**Conceito:** A Árvore Sintática Concreta (CST) registra o processo de derivação gramatical completo (como uma palavra foi reconhecida), enquanto a Árvore Sintática Abstrata (AST) representa apenas a estrutura hierárquica necessária para interpretar o significado do programa.

#### Justificativa do Grupo

> A CST preserva a derivação completa, incluindo delimitadores, palavras-chave e nós intermediários de hierarquia. Na AST, eliminamos ponto e vírgula, parênteses e chaves quando a relação já está representada por campos ou composição de nós. Nós concretos como `termo`, `fator` e `expr_aritmetica` são colapsados em `BinaryOpNode`, literais ou referências de variável.
>
> Em `(1 + 2) * 3`, os parênteses não precisam ser guardados como nós: o nó `BinaryOpNode("*")` tem como filho esquerdo outro `BinaryOpNode("+")`. Essa estrutura pai-filho preserva o agrupamento e a precedência. A AST não perde valores necessários à execução.
>
> `WhileNode` mantém `condition` e `body`, enquanto `ForNode` mantém `init`, `condition`, `update` e `body`. Esses campos correspondem diretamente aos passos operacionais e permitem ao interpretador executar inicialização uma vez, testar a condição, executar o corpo e atualizar antes da próxima repetição.


---

## 9. Tabela de Símbolos e Semântica Operacional

### 9.1. Estrutura e Operações da Tabela de Símbolos (`SymbolTable`)

A tabela de símbolos é implementada pela classe `SymbolTable` em `src/interpreter.py`, utilizando uma tabela de dispersão (`dict[str, SymbolEntry]`) para o escopo global único da MiniLang:

| Componente / Operação | Assinatura / Estrutura | Complexidade | Descrição |
| :--- | :--- | :---: | :--- |
| **Entrada (`SymbolEntry`)** | `(name, var_type, value, defined_line)` | — | Armazena o identificador, tipo inferido (`"int"` ou `"bool"`), valor corrente e linha de definição. |
| **Inserção (`insert`)** | `insert(name, value, line) -> SymbolEntry` | $O(1)$ médio | Infere o tipo do valor (`int` ou `bool`) e cria ou sobrescreve o registro da variável na tabela. |
| **Busca (`lookup`)** | `lookup(name, line, column) -> SymbolEntry` | $O(1)$ médio | Recupera a entrada associada a `name`; dispara `SemanticError` se a variável não existir. |
| **Existência (`exists`)** | `exists(name) -> bool` | $O(1)$ médio | Verifica se o identificador já foi registrado no ambiente atual. |

---

### 9.2. Semântica Operacional dos Comandos

Seja $\sigma$ o estado corrente da Tabela de Símbolos (`SymbolTable`) e $\langle e, \sigma \rangle \Downarrow v$ a relação de avaliação de uma expressão $e$ para um valor $v \in \mathbb{Z} \cup \{\text{true}, \text{false}\}$:

1. **Atribuição (`AssignNode(x, e)`):**
   Avalia primeiro a expressão $e$ no estado $\sigma$ ($\langle e, \sigma \rangle \Downarrow v$) e atualiza o estado para $\sigma' = \sigma[x \mapsto (v, \text{tipo}(v))]$. Se $e$ referenciar $x$ antes de $x$ existir (ex.: `x = x + 1;`), a avaliação falha com `SemanticError`.
2. **Impressão (`PrintNode(e)`):**
   Avalia $\langle e, \sigma \rangle \Downarrow v$ e registra a representação textual de $v$ no fluxo de saída sem alterar $\sigma$.
3. **Bloco (`BlockNode([c_1, ..., c_k])`):**
   Executa sequencialmente $c_1, c_2, \dots, c_k$, propagando o estado atualizado $\sigma_0 \to \sigma_1 \to \dots \to \sigma_k$ no mesmo escopo global.
4. **Condicional (`IfNode(cond, B_then, B_else)`):**
   Avalia $\langle \text{cond}, \sigma \rangle \Downarrow v$. Exige $\text{tipo}(v) = \text{bool}$ (caso contrário, lança `SemanticError`). Se $v = \text{true}$, executa $B_{\text{then}}$; se $v = \text{false}$ e $B_{\text{else}}$ existir, executa $B_{\text{else}}$.
5. **Laço `while` (`WhileNode(cond, B)`):**
   - Passo 1: Avalia $\langle \text{cond}, \sigma \rangle \Downarrow v$ e verifica $\text{tipo}(v) = \text{bool}$.
   - Passo 2: Se $v = \text{false}$, encerra o laço mantendo $\sigma$.
   - Passo 3: Se $v = \text{true}$ (e o contador de iterações não excedeu `max_iterations`), executa o bloco $B$ produzindo $\sigma'$ e retorna ao Passo 1 com o novo estado $\sigma'$.
6. **Laço `for` (`ForNode(init, cond, update, B)`):**
   - Passo 1 (**Inicialização**): Executa `init` ($\sigma \to \sigma_1$).
   - Passo 2 (**Teste de Condição**): Avalia $\langle \text{cond}, \sigma_1 \rangle \Downarrow v$ e verifica $\text{tipo}(v) = \text{bool}$. Se $v = \text{false}$, encerra o laço.
   - Passo 3 (**Corpo**): Executa o bloco $B$ ($\sigma_1 \to \sigma_2$).
   - Passo 4 (**Atualização e Repetição**): Executa `update` ($\sigma_2 \to \sigma_3$) e retorna ao Passo 2 com o estado $\sigma_3$.

---

### 9.3. Justificativas Formais: Tabela de Símbolos e Correção Semântica (Construção do Grupo)

* **Conceito:** A tabela de símbolos é a estrutura de dados central que conecta a declaração/atribuição de identificadores aos seus usos posteriores. Como a MiniLang não possui funções recursivas nem sombreamento de escopo local (*shadowing*), uma única tabela global indexada pelo nome do identificador é suficiente para validar todas as restrições semânticas.
* **Redação do Grupo (base para `docs/relatorio.pdf`):**
  > Uma única `SymbolTable` global é suficiente porque a MiniLang não define funções, sombreamento ou escopo local. `insert` cria uma entrada para um nome novo ou substitui seu valor e tipo em atualizações dentro de `while` e `for`. `lookup` verifica se o nome existe antes de retornar o valor.
  >
  > Em Python, `bool` é subclasse de `int`; portanto, `isinstance(True, int)` seria verdadeiro sem uma distinção explícita. O interpretador testa `isinstance(value, bool)` antes de `type(value) is int`, garantindo que verdadeiro/falso sejam classificados como `bool`.
  >
  > O `for` executa `init`, avalia `condition`, executa `body` e só então `update`. Se a condição inicial é falsa, o interpretador sai antes de corpo e atualização. Uma variável não definida usada na condição ou inicialização é encontrada por `lookup` e gera `SemanticError`; uma atribuição como `i = i + 1` falha na inicialização se `i` ainda não existe.

  ---

## 10. Catálogo de Erros e Estratégia de Diagnóstico

### 10.1. Erros Léxicos (`LexicalError` — `src/lexer.py`)

Ocorrem quando a entrada contém caracteres fora do alfabeto $\Sigma$ ou cadeias que não correspondem a nenhuma Expressão Regular dos tokens válidos:

| ID | Mensagem Emitida | Causa Formal | Exemplo de Entrada |
| :---: | :--- | :--- | :--- |
| **L1** | `Erro Léxico [linha 2, coluna 5]: Caractere inválido '@' fora do alfabeto da linguagem.` | No estado inicial `q0`, o símbolo `@` não possui transição definida na função $\delta(q_0, c)$. | `x = 10;`<br>`taxa@ = 20;` |
| **L2** | `Erro Léxico [linha 1, coluna 1]: Identificador ou literal numérico mal formado '1x'.` | No estado `q2` (leitura de `INT_LITERAL`), o AFD encontrou uma letra sem delimitador, violando `[0-9]+` e `[a-zA-Z_][a-zA-Z0-9_]*`. | `1x = 10;` |
| **L3** | `Erro Léxico [linha 2, coluna 1]: Comentário de bloco '/* ... */' não fechado antes do fim do arquivo.` | O AFD atingiu `EOF` permanecendo nos estados `q9` ou `q10` sem ler a sequência de fechamento `*/`. | `x = 1;`<br>`/* sem fim` |
| **L4** | `Erro Léxico [linha 1, coluna 5]: Operador '!' isolado não é suportado; esperado '!='.` | No estado intermediário `q7` (após ler `!`), o próximo caractere não foi `=`, único sufixo válido. | `if (!x) { print(1); }` |

---

### 10.2. Erros Sintáticos (`MiniLangSyntaxError` — `src/parser.py`)

Ocorrem quando os tokens são validados pelo lexer, mas a sequência viola alguma regra de produção da gramática EBNF:

| ID | Mensagem Emitida | Causa Formal | Exemplo de Entrada |
| :---: | :--- | :--- | :--- |
| **S1** | `Erro Sintático [linha 1, coluna 10]: Expressão inválida: esperado número inteiro, booleano, identificador ou '(', encontrado ';'.` | Em `_parse_fator()`, após consumir `+`, o lookahead encontra `;`, que não pertence ao conjunto `FIRST(fator)`. | `x = (1 + ;` |
| **S2 (Laço)** | `Erro Sintático [linha 1, coluna 19]: Esperado ';' após a condição do 'for' (a cláusula de atualização é obrigatória). Encontrado: ')'.` | Viola a produção `laco_for = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco`, omitindo a 3ª cláusula obrigatória. | `for (i = 0; i < 10) {`<br>`    print(i);`<br>`}` |
| **S3** | `Erro Sintático [linha 2, coluna 1]: Esperado ';' ao final do comando de atribuição. Encontrado: 'y'.` | Viola a produção `comando = atribuicao ";"` pela ausência do delimitador `;` antes do comando seguinte. | `x = 10`<br>`y = 20;` |
| **S4** | `Erro Sintático [linha 1, coluna 12]: Esperado '{' para iniciar bloco de comandos. Encontrado: 'print'.` | Viola a produção `condicional = "if" "(" expressao ")" bloco [ "else" bloco ]`, que exige `{ ... }` no corpo do `if`. | `if (x > 0) print(x);` |

---

### 10.3. Erros Semânticos (`SemanticError` — `src/interpreter.py`)

Ocorrem em programas sintaticamente válidos que violam restrições sensíveis ao contexto (escopo/definição, sistema de tipos ou domínio aritmético):

| ID | Mensagem Emitida | Causa Formal | Exemplo de Entrada |
| :---: | :--- | :--- | :--- |
| **M1** | `Erro Semântico [linha 2, coluna 9]: Variável 'z' não definida antes do uso.` | A operação `SymbolTable.lookup('z')` falha porque o identificador não foi inserido previamente na tabela de símbolos. | `x = 10;`<br>`y = x + z;` |
| **M2** | `Erro Semântico [linha 3, coluna 7]: Divisão por zero.` | Na avaliação de `BinaryOpNode('/')`, o operando direito avalia para `0`, fora do domínio da divisão inteira. | `a = 10;`<br>`b = 5 - 5;`<br>`c = a / b;` |
| **M3** | `Erro Semântico [linha 2, coluna 8]: Operador aritmético '+' exige operandos inteiros (int), mas recebeu 'int' e 'bool'.` | Viola a regra de tipagem estrita da operação `+ : int x int -> int`. | `flag = true;`<br>`x = 10 + flag;` |
| **M4 (Laço)** | `Erro Semântico [linha 2, coluna 8]: Condição do laço 'while' deve ser booleana (bool), mas recebeu 'int'.` | Viola a restrição semântica de `while (cond)`, que exige expressão de guarda do tipo `bool`. | `contador = 3;`<br>`while (contador) {`<br>`    contador = contador - 1;`<br>`}` |
| **M5 (Laço)** | `Erro Semântico [linha 1, coluna 17]: Variável 'limite' não definida antes do uso.` | Na avaliação da 2ª cláusula do `for`, `SymbolTable.lookup('limite')` não encontra a variável de controle/limite. | `for (i = 0; i < limite; i = i + 1) {`<br>`    print(i);`<br>`}` |

---

### 10.4. Demonstração por Execução via CLI

Todos os erros acima são verificados automaticamente pela suíte `pytest tests/invalidos/ -v` e podem ser reproduzidos diretamente na linha de comando:

```bash
# Demonstração via arquivo de exemplo inválido (Erro Sintático S2 em laço for):
python3 -m src.interpreter exemplos/programa_invalido.ml

# Demonstração rápida de Erro Léxico (L1):
python3 -c "from src.interpreter import run_source; run_source('taxa@ = 10;')"

# Demonstração rápida de Erro Semântico em Laço (M4):
python3 -c "from src.interpreter import run_source; run_source('x = 1; while (x) { x = 0; }')"
```

### 10.5. Justificativa da Estratégia de Recuperação/Diagnóstico de Erros (Construção do Grupo)

**Conceito:** Existem duas abordagens principais para tratamento de erros em compiladores educacionais:

* **Parada no Primeiro Erro (*Fail-Fast* com Diagnóstico Contextualizado):** interrompe a compilação imediatamente na primeira falha detectada, informando a fase (Léxico, Sintático ou Semântico), a posição exata (linha, coluna) e o contraste entre o que era esperado e o que foi encontrado.
* **Recuperação em Modo Pânico (*Panic-Mode Recovery*):** descarta tokens até encontrar um símbolo de sincronização (como `;` ou `}`) para tentar continuar a análise sintática e reportar múltiplos erros de uma só vez.

#### Justificativa do Grupo

> O projeto adota *Fail-Fast* com exceções tipadas por fase. A primeira falha é interrompida imediatamente, evitando que erros sintáticos derivados produzam novos diagnósticos que pareçam erros reais. Exceções distintas (`LexicalError`, `MiniLangSyntaxError`, `SemanticError`) permitem identificar rapidamente em qual etapa ocorreu o problema e localizar linha e coluna. `_expect_token()` informa o token esperado e o encontrado, como a atualização obrigatória do `for`.
>
> O modo pânico poderia continuar após `;` ou `}` e apresentar vários erros em uma única execução. Isso é útil em IDEs, mas aumenta o risco de diagnósticos em cascata. Na plataforma educacional da MiniLang, o objetivo é apresentar ao aluno uma causa precisa e verificável, portanto a parada no primeiro erro é mais didática.