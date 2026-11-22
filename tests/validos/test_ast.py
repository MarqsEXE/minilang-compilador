"""Testes unitários para construção e estrutura da Árvore Sintática Abstrata (AST)."""

from pathlib import Path
from src.ast_nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolLiteralNode,
    ForNode,
    IfNode,
    IntLiteralNode,
    PrintNode,
    ProgramNode,
    VarNode,
    WhileNode,
)
from src.lexer import Lexer
from src.parser import Parser


def _build_ast(codigo: str) -> ProgramNode:
    tokens = Lexer(codigo).tokenize()
    return Parser(tokens).parse_ast()


def test_ast_precedencia_1_mais_2_vezes_3() -> None:
    ast = _build_ast("r = 1 + 2 * 3;")
    assert len(ast.statements) == 1

    assign = ast.statements[0]
    assert isinstance(assign, AssignNode)
    assert assign.name == "r"

    # Raiz da expressão deve ser '+' com '1' à esquerda e '(2 * 3)' à direita
    expected_expr = BinaryOpNode(
        line=1,
        column=7,
        left=IntLiteralNode(line=1, column=5, value=1),
        operator="+",
        right=BinaryOpNode(
            line=1,
            column=11,
            left=IntLiteralNode(line=1, column=9, value=2),
            operator="*",
            right=IntLiteralNode(line=1, column=13, value=3),
        ),
    )
    assert assign.value == expected_expr


def test_ast_associatividade_esquerda_subtracao() -> None:
    ast = _build_ast("r = 10 - 3 - 2;")
    assign = ast.statements[0]
    assert isinstance(assign, AssignNode)
    assert isinstance(assign.value, BinaryOpNode)
    assert assign.value.operator == "-"
    assert isinstance(assign.value.left, BinaryOpNode)
    assert assign.value.left.operator == "-"


def test_ast_parenteses_elimina_delimitadores_preservando_agrupamento() -> None:
    ast = _build_ast("r = (1 + 2) * 3;")
    assign = ast.statements[0]
    assert isinstance(assign, AssignNode)

    # Raiz da expressão deve ser '*' com '(1 + 2)' à esquerda e '3' à direita
    expected_expr = BinaryOpNode(
        line=1,
        column=13,
        left=BinaryOpNode(
            line=1,
            column=8,
            left=IntLiteralNode(line=1, column=6, value=1),
            operator="+",
            right=IntLiteralNode(line=1, column=10, value=2),
        ),
        operator="*",
        right=IntLiteralNode(line=1, column=15, value=3),
    )
    assert assign.value == expected_expr


def test_ast_laco_while() -> None:
    ast = _build_ast("while (x < 10) { x = x + 1; }")
    stmt = ast.statements[0]

    assert isinstance(stmt, WhileNode)
    assert isinstance(stmt.condition, BinaryOpNode)
    assert stmt.condition.operator == "<"
    assert isinstance(stmt.body, BlockNode)
    assert len(stmt.body.statements) == 1
    assert isinstance(stmt.body.statements[0], AssignNode)


def test_ast_laco_for_tres_clausulas() -> None:
    ast = _build_ast("for (i = 0; i < 10; i = i + 1) { print(i); }")
    stmt = ast.statements[0]

    assert isinstance(stmt, ForNode)
    # 1ª cláusula: init
    assert isinstance(stmt.init, AssignNode)
    assert stmt.init.name == "i"
    assert stmt.init.value == IntLiteralNode(line=1, column=10, value=0)

    # 2ª cláusula: condition
    assert isinstance(stmt.condition, BinaryOpNode)
    assert stmt.condition.operator == "<"

    # 3ª cláusula: update
    assert isinstance(stmt.update, AssignNode)
    assert stmt.update.name == "i"
    assert isinstance(stmt.update.value, BinaryOpNode)
    assert stmt.update.value.operator == "+"

    # Corpo do laço
    assert isinstance(stmt.body, BlockNode)
    assert len(stmt.body.statements) == 1
    assert isinstance(stmt.body.statements[0], PrintNode)


def test_ast_condicional_e_literais_booleanos() -> None:
    ast = _build_ast("if (true) { x = 1; } else { x = 2; }")
    stmt = ast.statements[0]

    assert isinstance(stmt, IfNode)
    assert stmt.condition == BoolLiteralNode(line=1, column=5, value=True)
    assert isinstance(stmt.then_block, BlockNode)
    assert isinstance(stmt.else_block, BlockNode)


def test_ast_programa_valido_completo_e_pretty_print() -> None:
    codigo = Path("exemplos/programa_valido.ml").read_text(encoding="utf-8")
    ast = _build_ast(codigo)

    assert isinstance(ast, ProgramNode)
    assert any(isinstance(s, WhileNode) for s in ast.statements)
    assert any(isinstance(s, ForNode) for s in ast.statements)

    diagrama = ast.pretty_print()
    assert "ProgramNode" in diagrama
    assert "WhileNode" in diagrama
    assert "ForNode" in diagrama