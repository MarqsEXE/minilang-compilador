# Especificação Formal da Linguagem MiniLang

## 1. Alfabeto (Tokens)

O alfabeto de símbolos terminais $\Sigma$ da MiniLang é dividido nas seguintes categorias léxicas:

1. **Palavras Reservadas (Keywords):**
   `if`, `else`, `while`, `for`, `print`, `true`, `false`
2. **Identificadores (`ID`):**
   Sequências iniciadas por letra (`a-z`, `A-Z`) ou sublinhado (`_`), seguidas de zero ou mais letras, dígitos (`0-9`) ou sublinhados, desde que não coincidam com palavras reservadas.
   - *Expressão regular:* `[a-zA-Z_][a-zA-Z0-9_]*`
3. **Literais Inteiros (`INT_LITERAL`):**
   Sequências não vazias de dígitos decimais.
   - *Expressão regular:* `[0-9]+`
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

```ebnf
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
```

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

