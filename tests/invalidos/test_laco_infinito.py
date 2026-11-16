"""
Categoria: Controle de Terminação / Laço Infinito (tests/invalidos/test_laco_infinito.py)

Resultados esperados documentados (todos devem lançar SemanticError sem travar a suíte):
1. test_while_infinito_condicao_constante_true:
   - Entrada: "x = 0;\\nwhile (true) { x = x + 1; }" (com max_iterations=50)
   - Resultado esperado: SemanticError [linha 2, coluna 1] -> Limite máximo de iterações (50) excedido no laço 'while'.
2. test_while_infinito_variavel_nao_converge:
   - Entrada: "x = 1;\\nwhile (x > 0) { x = x + 1; }" (com max_iterations=100)
   - Resultado esperado: SemanticError [linha 2, coluna 1] -> Limite máximo de iterações (100) excedido no laço 'while'.
3. test_for_infinito_atualizacao_estagnada:
   - Entrada: "for (i = 0; i < 10; i = i + 0) { x = i; }" (com max_iterations=50)
   - Resultado esperado: SemanticError [linha 1, coluna 1] -> Limite máximo de iterações (50) excedido no laço 'for'.
4. test_for_infinito_atualizacao_divergente:
   - Entrada: "for (i = 1; i > 0; i = i + 1) { x = i; }" (com max_iterations=50)
   - Resultado esperado: SemanticError [linha 1, coluna 1] -> Limite máximo de iterações (50) excedido no laço 'for'.
"""

import pytest
from src.interpreter import SemanticError, run_source


def test_while_infinito_condicao_constante_true() -> None:
    codigo = "x = 0;\nwhile (true) {\n    x = x + 1;\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo, max_iterations=50)

    err = exc_info.value
    assert err.line == 2
    assert "Limite máximo de iterações (50)" in err.message
    assert "'while'" in err.message


def test_while_infinito_variavel_nao_converge() -> None:
    codigo = "x = 1;\nwhile (x > 0) {\n    x = x + 1;\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo, max_iterations=100)

    assert "Limite máximo de iterações (100)" in exc_info.value.message


def test_for_infinito_atualizacao_estagnada() -> None:
    codigo = "for (i = 0; i < 10; i = i + 0) {\n    x = i;\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo, max_iterations=50)

    err = exc_info.value
    assert err.line == 1
    assert "Limite máximo de iterações (50)" in err.message
    assert "'for'" in err.message


def test_for_infinito_atualizacao_divergente() -> None:
    codigo = "for (i = 1; i > 0; i = i + 1) {\n    x = i;\n}"
    with pytest.raises(SemanticError) as exc_info:
        run_source(codigo, max_iterations=50)

    assert "'for'" in exc_info.value.message