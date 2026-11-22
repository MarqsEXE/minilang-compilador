"""Testes unitários para execução semântica de programas válidos da MiniLang."""

from pathlib import Path
from src.interpreter import Interpreter, SymbolTable, run_source
from src.lexer import Lexer
from src.parser import Parser


def test_tabela_de_simbolos_insercao_e_busca() -> None:
    st = SymbolTable()
    st.insert("x", 42, line=1)
    st.insert("flag", True, line=2)

    entry_x = st.lookup("x", line=3, column=1)
    assert entry_x.var_type == "int"
    assert entry_x.value == 42

    entry_flag = st.lookup("flag", line=4, column=1)
    assert entry_flag.var_type == "bool"
    assert entry_flag.value is True

    # Atualização de valor existente
    st.insert("x", 100, line=5)
    assert st.lookup("x", line=6, column=1).value == 100


def test_aritmetica_precedencia_e_divisao_inteira_truncada() -> None:
    codigo = """
    a = 1 + 2 * 3;
    b = (1 + 2) * 3;
    c = 7 / 2;
    d = (0 - 7) / 2;
    print(a);
    print(b);
    print(c);
    print(d);
    """
    assert run_source(codigo) == ["7", "9", "3", "-3"]


def test_divisao_inteira_grande_sem_conversao_para_float() -> None:
    codigo = "a = " + ("9" * 400) + "; print(a / 2);"
    saidas = run_source(codigo)
    assert len(saidas) == 1
    assert saidas[0].isdigit()


def test_operadores_relacionais_e_igualdade() -> None:
    codigo = """
    print(10 > 5);
    print(10 <= 10);
    print(true == true);
    print(true != false);
    print(5 == 5);
    """
    assert run_source(codigo) == ["true", "true", "true", "true", "true"]


def test_condicional_if_else() -> None:
    codigo = """
    x = 15;
    if (x > 10) {
        print(1);
    } else {
        print(0);
    }

    if (x < 5) {
        print(1);
    } else {
        print(2);
    }
    """
    assert run_source(codigo) == ["1", "2"]


def test_execucao_laco_while() -> None:
    codigo = """
    n = 4;
    fat = 1;
    while (n > 1) {
        fat = fat * n;
        n = n - 1;
    }
    print(fat);
    """
    assert run_source(codigo) == ["24"]


def test_execucao_laco_for_e_escopo_global() -> None:
    codigo = """
    soma = 0;
    for (i = 1; i <= 4; i = i + 1) {
        soma = soma + i;
    }
    print(soma);
    print(i);
    """
    # soma = 1 + 2 + 3 + 4 = 10; após o laço, i == 5 no escopo global
    assert run_source(codigo) == ["10", "5"]


def test_execucao_programa_valido_completo() -> None:
    codigo = Path("exemplos/programa_valido.ml").read_text(encoding="utf-8")
    tokens = Lexer(codigo).tokenize()
    ast = Parser(tokens).parse_ast()
    interp = Interpreter()
    saidas = interp.execute(ast)

    assert saidas == ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "10"]
    assert interp.symbol_table.lookup("soma", 1, 1).value == 10