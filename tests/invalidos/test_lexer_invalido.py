"""
Testes unitários para erros léxicos da MiniLang.
Resultado esperado: todos os casos devem lançar LexicalError com linha e coluna exatas.
"""

import pytest
from src.lexer import Lexer, LexicalError


def test_caractere_invalido_arroba() -> None:
    codigo = "x = 10;\ntaxa@ = 20;"
    with pytest.raises(LexicalError) as exc_info:
        Lexer(codigo).tokenize()

    err = exc_info.value
    assert err.line == 2
    assert err.column == 5
    assert "@" in err.message


def test_identificador_iniciado_por_digito_1x() -> None:
    codigo = "1x = 10;"
    with pytest.raises(LexicalError) as exc_info:
        Lexer(codigo).tokenize()

    err = exc_info.value
    assert err.line == 1
    assert err.column == 1
    assert "1x" in err.message


def test_comentario_de_bloco_nao_fechado() -> None:
    codigo = "x = 1;\n/* comentario aberto sem fechamento\ny = 2;"
    with pytest.raises(LexicalError) as exc_info:
        Lexer(codigo).tokenize()

    err = exc_info.value
    assert err.line == 2
    assert err.column == 1
    assert "não fechado" in err.message


def test_operador_exclamacao_isolado() -> None:
    codigo = "if (!x) { print(1); }"
    with pytest.raises(LexicalError) as exc_info:
        Lexer(codigo).tokenize()

    err = exc_info.value
    assert err.line == 1
    assert err.column == 5
    assert "!=" in err.message