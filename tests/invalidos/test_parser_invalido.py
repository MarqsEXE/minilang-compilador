"""
Testes unitários para erros sintáticos da MiniLang.
Resultado esperado: todos os casos devem lançar MiniLangSyntaxError com linha e coluna exatas.
"""

from pathlib import Path
import pytest
from src.lexer import Lexer
from src.parser import Parser, MiniLangSyntaxError


def _parse_source(codigo: str):
    tokens = Lexer(codigo).tokenize()
    return Parser(tokens).parse_cst()


def test_expressao_incompleta_parenteses() -> None:
    with pytest.raises(MiniLangSyntaxError) as exc_info:
        _parse_source("x = (1 + ;")

    err = exc_info.value
    assert err.line == 1
    assert err.column == 10


def test_laco_for_sem_clausula_de_atualizacao() -> None:
    codigo = "for (i = 0; i < 10) {\n    print(i);\n}"
    with pytest.raises(MiniLangSyntaxError) as exc_info:
        _parse_source(codigo)

    err = exc_info.value
    assert err.line == 1
    assert err.column == 19
    assert "atualização" in err.message


def test_laco_for_com_clausula_vazia() -> None:
    with pytest.raises(MiniLangSyntaxError):
        _parse_source("for (; i < 10; i = i + 1) { print(i); }")


def test_falta_ponto_e_virgula_apos_atribuicao() -> None:
    codigo = "x = 10\ny = 20;"
    with pytest.raises(MiniLangSyntaxError) as exc_info:
        _parse_source(codigo)

    assert exc_info.value.line == 2


def test_if_sem_chaves_de_bloco() -> None:
    with pytest.raises(MiniLangSyntaxError) as exc_info:
        _parse_source("if (x > 0) print(x);")

    assert "bloco" in exc_info.value.message


def test_comparacao_encadeada_nao_associativa() -> None:
    with pytest.raises(MiniLangSyntaxError):
        _parse_source("ok = 1 < 2 < 3;")


def test_programa_invalido_exemplo_rejeitado() -> None: # retornou erro no test: adicionar alteração
    codigo = Path("exemplos/programa_invalido.ml").read_text(encoding="utf-8")
    linha_esperada = next(
        idx
        for idx, linha in enumerate(codigo.splitlines(), start=1)
        if linha.strip().startswith("for")
    )

    with pytest.raises(MiniLangSyntaxError) as exc_info:
        _parse_source(codigo)

    assert exc_info.value.line == linha_esperada
    assert "atualização" in exc_info.value.message
