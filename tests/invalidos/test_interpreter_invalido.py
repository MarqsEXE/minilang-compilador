"""
Categoria: Erros Semânticos (tests/invalidos/test_interpreter_invalido.py)

Resultados esperados documentados (todos devem lançar SemanticError):
1. test_variavel_nao_definida_em_expressao:
   - Entrada: "x = 10;\\ny = x + z;"
   - Resultado esperado: SemanticError [linha 2, coluna 9] -> Variável 'z' não definida antes do uso.
2. test_divisao_por_zero:
   - Entrada: "a = 10;\\nb = 5 - 5;\\nc = a / b;"
   - Resultado esperado: SemanticError [linha 3, coluna 7] -> Divisão por zero.
3. test_tipo_incompativel_soma_int_com_bool:
   - Entrada: "flag = true;\\nx = 10 + flag;"
   - Resultado esperado: SemanticError [linha 2, coluna 8] -> Operador '+' exige (int, int), recebeu 'int' e 'bool'.
4. test_tipo_incompativel_relacional_com_bool:
   - Entrada: "b = true < 10;"
   - Resultado esperado: SemanticError [linha 1, coluna 10] -> Operador relacional '<' exige (int, int).
5. test_tipo_incompativel_igualdade_entre_int_e_bool:
   - Entrada: "b = (1 == true);"
   - Resultado esperado: SemanticError [linha 1, coluna 8] -> Operador '==' exige operandos do mesmo tipo.
6. test_condicao_nao_booleana_no_if:
   - Entrada: "x = 1;\\nif (x) { print(x); }"
   - Resultado esperado: SemanticError [linha 2, coluna 5] -> Condição do 'if' deve ser booleana (bool).
7. test_condicao_nao_booleana_no_while (Erro semântico em laço):
   - Entrada: "contador = 3;\\nwhile (contador) { contador = contador - 1; }"
   - Resultado esperado: SemanticError [linha 2, coluna 8] -> Condição do laço 'while' deve ser booleana (bool).
8. test_condicao_nao_booleana_no_for (Erro semântico em laço):
   - Entrada: "for (i = 0; i + 5; i = i + 1) { print(i); }"
   - Resultado esperado: SemanticError [linha 1, coluna 15] -> Condição do laço 'for' deve ser booleana (bool).
9. test_variavel_de_controle_nao_definida_no_for (Erro semântico em laço):
   - Entrada: "for (i = 0; i < limite; i = i + 1) { print(i); }"
   - Resultado esperado: SemanticError [linha 1, coluna 17] -> Variável 'limite' não definida antes do uso.
10. test_variavel_de_controle_lida_antes_de_definir_na_inicializacao_do_for (Erro semântico em laço):
   - Entrada: "for (i = i + 1; i < 5; i = i + 1) { print(i); }"
   - Resultado esperado: SemanticError [linha 1, coluna 10] -> Variável 'i' não definida antes do uso.
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