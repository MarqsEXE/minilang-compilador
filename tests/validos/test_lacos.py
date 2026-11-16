"""
Testes unitários de cobertura e casos de borda para laços 'while' e 'for'.

Cobre obrigatoriamente:
- Laço que não executa (condição falsa logo na entrada: 0 iterações);
- Laço que executa exatamente 1 vez;
- Laço que executa N vezes;
- Laço 'for' cuja cláusula de atualização (e/ou corpo) altera a variável de controle;
- Laços aninhados compartilhando a tabela de símbolos global.
"""

from src.interpreter import Interpreter, run_source
from src.lexer import Lexer
from src.parser import Parser


def test_while_nao_executa_condicao_falsa_na_entrada() -> None:
    codigo = """
    x = 10;
    executou = false;
    while (x < 5) {
        executou = true;
        x = x + 1;
    }
    print(executou);
    print(x);
    """
    assert run_source(codigo) == ["false", "10"]


def test_for_nao_executa_condicao_falsa_na_entrada() -> None:
    codigo = """
    soma = 0;
    for (i = 10; i < 5; i = i + 1) {
        soma = soma + 1;
    }
    print(soma);
    print(i);
    """
    # A inicialização (i = 10) ocorre uma vez; a condição falha de imediato;
    # nem o corpo nem a atualização (i = i + 1) são executados.
    assert run_source(codigo) == ["0", "10"]


def test_while_executa_uma_vez() -> None:
    codigo = """
    passos = 0;
    ativo = true;
    while (ativo) {
        passos = passos + 1;
        ativo = false;
    }
    print(passos);
    """
    assert run_source(codigo) == ["1"]


def test_for_executa_uma_vez() -> None:
    codigo = """
    passos = 0;
    for (i = 0; i < 1; i = i + 1) {
        passos = passos + 1;
    }
    print(passos);
    print(i);
    """
    assert run_source(codigo) == ["1", "1"]


def test_while_executa_n_vezes() -> None:
    codigo = """
    i = 0;
    acumulado = 0;
    while (i < 6) {
        acumulado = acumulado + i;
        i = i + 1;
    }
    print(acumulado);
    """
    # 0 + 1 + 2 + 3 + 4 + 5 = 15
    assert run_source(codigo) == ["15"]


def test_for_executa_n_vezes() -> None:
    codigo = """
    prod = 1;
    for (k = 1; k <= 5; k = k + 1) {
        prod = prod * k;
    }
    print(prod);
    """
    # 1 * 2 * 3 * 4 * 5 = 120
    assert run_source(codigo) == ["120"]


def test_for_atualizacao_altera_variavel_de_controle_passo_customizado_e_decremento() -> None:
    codigo = """
    // 1) Atualizacao com passo +3
    for (i = 0; i < 10; i = i + 3) {
        print(i);
    }

    // 2) Atualizacao regressiva (decremento)
    for (j = 3; j > 0; j = j - 1) {
        print(j);
    }
    """
    assert run_source(codigo) == ["0", "3", "6", "9", "3", "2", "1"]


def test_for_com_alteracao_adicional_da_variavel_de_controle_no_corpo() -> None:
    codigo = """
    iteracoes = 0;
    for (i = 0; i < 10; i = i + 1) {
        iteracoes = iteracoes + 1;
        // Corpo altera a variavel de controle alem da clausula de atualizacao
        i = i + 2;
    }
    print(iteracoes);
    print(i);
    """
    # Iteração 1: i=0 -> corpo i=2 -> update i=3
    # Iteração 2: i=3 -> corpo i=5 -> update i=6
    # Iteração 3: i=6 -> corpo i=8 -> update i=9
    # Iteração 4: i=9 -> corpo i=11 -> update i=12 (encerra)
    assert run_source(codigo) == ["4", "12"]


def test_lacos_aninhados_for_e_while() -> None:
    codigo = """
    total = 0;
    for (i = 1; i <= 3; i = i + 1) {
        j = 1;
        while (j <= 2) {
            total = total + 1;
            j = j + 1;
        }
    }
    print(total);
    """
    tokens = Lexer(codigo).tokenize()
    ast = Parser(tokens).parse_ast()
    interp = Interpreter()
    assert interp.execute(ast) == ["6"]