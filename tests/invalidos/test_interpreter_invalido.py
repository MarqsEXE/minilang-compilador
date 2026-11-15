"""
Testes unitários para erros semânticos da MiniLang.
Resultado esperado: todos os casos devem lançar SemanticError com linha e coluna exatas.
"""

import pytest
from src.interpreter import SemanticError, run_source


def test_variavel_nao_definida_em_expressao() -> None:
    codigo = "x = 10;\ny = x + z;"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 2
    assert "z" in exc_info.value.message


def test_divisao_por_zero() -> None:
    codigo = "a = 10;\nb = 5 - 5;\nc = a / b;"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 3
    assert "Divisão por zero" in exc_info.value.message


def test_tipo_incompativel_soma_int_com_bool() -> None:
    codigo = "flag = true;\nx = 10 + flag;"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 2
    assert "int" in exc_info.value.message and "bool" in exc_info.value.message


def test_tipo_incompativel_relacional_com_bool() -> None:
    codigo = "b = true < 10;"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 1
    assert "relacional" in exc_info.value.message


def test_tipo_incompativel_igualdade_entre_int_e_bool() -> None:
    codigo = "b = (1 == true);"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 1
    assert "mesmo tipo" in exc_info.value.message


def test_condicao_nao_booleana_no_if() -> None:
    codigo = "x = 1;\nif (x) {\n    print(x);\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 2
    assert "'if'" in exc_info.value.message


def test_condicao_nao_booleana_no_while() -> None:
    codigo = "contador = 3;\nwhile (contador) {\n    contador = contador - 1;\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 2
    assert "'while'" in exc_info.value.message


def test_condicao_nao_booleana_no_for() -> None:
    codigo = "for (i = 0; i + 5; i = i + 1) {\n    print(i);\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 1
    assert "'for'" in exc_info.value.message


def test_variavel_de_controle_nao_definida_no_for() -> None:
    # A variável 'limite' usada na condição do 'for' nunca foi definida
    codigo = "for (i = 0; i < limite; i = i + 1) {\n    print(i);\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 1
    assert "limite" in exc_info.value.message


def test_variavel_de_controle_lida_antes_de_definir_na_inicializacao_do_for() -> None:
    # 'i' aparece no lado direito da inicialização antes de existir na tabela de símbolos
    codigo = "for (i = i + 1; i < 5; i = i + 1) {\n    print(i);\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo)

    assert exc_info.value.line == 1
    assert "i" in exc_info.value.message