"""
Categoria: Erros Léxicos (tests/invalidos/test_lexer_invalido.py)

Resultados esperados documentados (todos devem lançar LexicalError):
1. test_caractere_invalido_arroba:
   - Entrada: "x = 10;\\ntaxa@ = 20;"
   - Resultado esperado: LexicalError [linha 2, coluna 5] -> Caractere inválido '@' fora do alfabeto.
2. test_identificador_iniciado_por_digito_1x:
   - Entrada: "1x = 10;"
   - Resultado esperado: LexicalError [linha 1, coluna 1] -> Identificador ou literal numérico mal formado '1x'.
3. test_comentario_de_bloco_nao_fechado:
   - Entrada: "x = 1;\\n/* comentario aberto sem fechamento\\ny = 2;"
   - Resultado esperado: LexicalError [linha 2, coluna 1] -> Comentário de bloco '/* ... */' não fechado antes do fim do arquivo.
4. test_operador_exclamacao_isolado:
   - Entrada: "if (!x) { print(1); }"
   - Resultado esperado: LexicalError [linha 1, coluna 5] -> Operador '!' isolado não é suportado; esperado '!='.
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