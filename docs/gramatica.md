| Tipo de Token (`TokenType`) | Expressão Regular / Padrão | Exemplos |
| :--- | :--- | :--- |
| `IF` | `if` | `if` |
| `ELSE` | `else` | `else` |
| `WHILE` | `while` | `while` |
| `FOR` | `for` | `for` |
| `PRINT` | `print` | `print` |
| `TRUE` | `true` | `true` |
| `FALSE` | `false` | `false` |
| `ID` | `[a-zA-Z_][a-zA-Z0-9_]*` (exceto reservadas) | `x`, `soma_pares`, `_aux1` |
| `INT_LITERAL` | `[0-9]+` | `0`, `42`, `120` |
| `PLUS` | `\+` | `+` |
| `MINUS` | `-` | `-` |
| `STAR` | `\*` | `*` |
| `SLASH` | `/` | `/` |
| `LT` | `<` | `<` |
| `GT` | `>` | `>` |
| `LE` | `<=` | `<=` |
| `GE` | `>=` | `>=` |
| `EQ` | `==` | `==` |
| `NEQ` | `!=` | `!=` |
| `ASSIGN` | `=` | `=` |
| `LPAREN` | `\(` | `(` |
| `RPAREN` | `\)` | `)` |
| `LBRACE` | `\{` | `{` |
| `RBRACE` | `\}` | `}` |
| `SEMICOLON` | `;` | `;` |
| `EOF` | Fim da entrada | `""` (fim de arquivo) |
| *(Ignorado)* | `[ \t\r\n]+` \| `//[^\n]*` \| `/\*([^*]\|\*+[^*/])*\*/` | espaços, `// obs`, `/* bloco */` |

---

### 6.2. Tabela de Transições do AFD ($\delta: Q \times \Sigma \to Q$)

Legenda de classes de caracteres:
- `WS`: espaço, `\t`, `\r`, `\n`
- `LET`: `[a-zA-Z_]`
- `DIG`: `[0-9]`
- `OP1`: `+`, `-`, `*`, `(`, `)`, `{`, `}`, `;`
- `OUTRO`: qualquer caractere válido que não continua o lexema atual (aciona lookahead / aceitação com retrocesso de 1 posição)

| Estado | `WS` | `LET` | `DIG` | `OP1` | `/` | `*` | `=` | `<` | `>` | `!` | `\n` | `EOF` | `OUTRO` | Ação / Aceitação |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`q0`** | `q0` | `q1` | `q2` | Aceita `OP1` | `q3` | Aceita `STAR` | `q4` | `q5` | `q6` | `q7` | `q0` | Aceita `EOF` | **Erro** | Estado inicial |
| **`q1`** | Aceita* | `q1` | `q1` | Aceita* | Aceita* | Aceita* | Aceita* | Aceita* | Aceita* | Aceita* | Aceita* | Aceita* | Aceita* | `*`: busca em `KEYWORDS` ou `ID` |
| **`q2`** | Aceita `INT` | **Erro** (`1x`) | `q2` | Aceita `INT` | Aceita `INT` | Aceita `INT` | Aceita `INT` | Aceita `INT` | Aceita `INT` | Aceita `INT` | Aceita `INT` | Aceita `INT` | Aceita `INT` | Aceita `INT_LITERAL` |
| **`q3`** | Aceita `SLASH` | Aceita `SLASH` | Aceita `SLASH` | Aceita `SLASH` | `q8` | `q9` | Aceita `SLASH` | Aceita `SLASH` | Aceita `SLASH` | Aceita `SLASH` | Aceita `SLASH` | Aceita `SLASH` | Aceita `SLASH` | `/` vs `//` vs `/*` |
| **`q4`** | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `EQ` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | Aceita `ASSIGN` | `=` vs `==` |
| **`q5`** | Aceita `LT` | Aceita `LT` | Aceita `LT` | Aceita `LT` | Aceita `LT` | Aceita `LT` | Aceita `LE` | Aceita `LT` | Aceita `LT` | Aceita `LT` | Aceita `LT` | Aceita `LT` | Aceita `LT` | `<` vs `<=` |
| **`q6`** | Aceita `GT` | Aceita `GT` | Aceita `GT` | Aceita `GT` | Aceita `GT` | Aceita `GT` | Aceita `GE` | Aceita `GT` | Aceita `GT` | Aceita `GT` | Aceita `GT` | Aceita `GT` | Aceita `GT` | `>` vs `>=` |
| **`q7`** | **Erro** | **Erro** | **Erro** | **Erro** | **Erro** | **Erro** | Aceita `NEQ` | **Erro** | **Erro** | **Erro** | **Erro** | **Erro** | **Erro** | Exige `=` após `!` |
| **`q8`** | `q8` | `q8` | `q8` | `q8` | `q8` | `q8` | `q8` | `q8` | `q8` | `q8` | `q0` | `q0` | `q8` | Comentário `//` |
| **`q9`** | `q9` | `q9` | `q9` | `q9` | `q9` | `q10` | `q9` | `q9` | `q9` | `q9` | `q9` | **Erro** | `q9` | Comentário `/*` |
| **`q10`** | `q9` | `q9` | `q9` | `q9` | `q0` | `q10` | `q9` | `q9` | `q9` | `q9` | `q9` | **Erro** | `q9` | Fecha `*/` ou volta `q9` |

---

### 6.3. Justificativa Formal: Expressões Regulares $\leftrightarrow$ AFD $\leftrightarrow$ Lexer (Construção do Grupo)

* **Conceito:** Pelo Teorema de Kleene, toda linguagem regular descrita por uma Expressão Regular pode ser reconhecida por um Autômato Finito Determinístico (AFD). Na implementação prática de um lexer, a união das ERs de todos os tokens forma um único AFD com dois mecanismos adicionais: (1) **regra do casamento mais longo (*maximal munch*)**, que continua consumindo caracteres enquanto houver transição válida (evitando que `==` vire dois `=` ou `while` vire `ID`), e (2) **prioridade de palavras reservadas**, que consulta a tabela `KEYWORDS` ao final do estado `q1` em vez de criar dezenas de estados exclusivos no autômato.
* **Redação do Grupo (base também para a seção "Análise Léxica" de `docs/relatorio.pdf`)[cite: 4]:**
  > [PREENCHER PELO GRUPO: Explique com suas palavras:
  > 1. Como o AFD resolve o conflito de prefixo entre operadores simples (`=`, `<`, `>`, `/`) e compostos (`==`, `<=`, `>=`, `//`, `/*`) usando estados intermediários (`q3` a `q6`) e lookahead (`_peek()`).
  > 2. Por que tratar palavras reservadas (`while`, `for`, `if`) via dicionário `KEYWORDS` após o estado `q1` reduz o número de estados do AFD sem alterar a linguagem regular reconhecida.
  > 3. Como os estados de erro no AFD (como `q2` ao ler letra após dígito em `1x`, ou `q9`/`q10` ao atingir `EOF`) garantem que o lexer reconheça **exatamente** os tokens válidos da MiniLang e rejeite cadeias fora da linguagem.]