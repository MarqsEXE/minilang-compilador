"""Testes unitários para entradas sintáticas válidas da MiniLang."""

from pathlib import Path
from src.lexer import Lexer
from src.parser import Parser


def _parse_source(codigo: str):
    tokens = Lexer(codigo).tokenize()
    return Parser(tokens).parse_cst()


def test_precedencia_1_mais_2_vezes_3_vs_parenteses() -> None:
    cst_sem_paren = _parse_source("r = 1 + 2 * 3;")
    cst_com_paren = _parse_source("r = (1 + 2) * 3;")

    # Navega até expr_aritmetica da atribuição:
    # programa -> comando -> atribuicao -> expressao -> expr_igualdade -> expr_relacional -> expr_aritmetica
    expr_arit_1 = (
        cst_sem_paren.children[0]
        .children[0]
        .children[2]
        .children[0]
        .children[0]
        .children[0]
    )
    # Em 1 + 2 * 3, expr_aritmetica tem 3 filhos: termo(1), PLUS(+), termo(2 * 3)
    assert expr_arit_1.symbol == "expr_aritmetica"
    assert len(expr_arit_1.children) == 3
    assert expr_arit_1.children[1].symbol == "PLUS"
    assert len(expr_arit_1.children[2].children) == 3  # 2 * 3 agrupado no termo direito

    expr_arit_2 = (
        cst_com_paren.children[0]
        .children[0]
        .children[2]
        .children[0]
        .children[0]
        .children[0]
    )
    # Em (1 + 2) * 3, expr_aritmetica tem apenas 1 filho: termo((1 + 2) * 3)
    assert expr_arit_2.symbol == "expr_aritmetica"
    assert len(expr_arit_2.children) == 1
    termo_2 = expr_arit_2.children[0]
    assert len(termo_2.children) == 3
    assert termo_2.children[1].symbol == "STAR"


def test_parsing_laco_while() -> None:
    cst = _parse_source("while (x < 10) { x = x + 1; }")
    cmd_while = cst.children[0].children[0]

    assert cmd_while.symbol == "laco_while"
    assert [c.symbol for c in cmd_while.children] == [
        "WHILE",
        "LPAREN",
        "expressao",
        "RPAREN",
        "bloco",
    ]


def test_parsing_laco_for_tres_clausulas() -> None:
    cst = _parse_source("for (i = 0; i < 10; i = i + 1) { print(i); }")
    cmd_for = cst.children[0].children[0]

    assert cmd_for.symbol == "laco_for"
    assert [c.symbol for c in cmd_for.children] == [
        "FOR",
        "LPAREN",
        "atribuicao",   # 1ª cláusula: inicialização
        "SEMICOLON",
        "expressao",    # 2ª cláusula: condição
        "SEMICOLON",
        "atribuicao",   # 3ª cláusula: atualização
        "RPAREN",
        "bloco",
    ]


def test_parsing_condicional_if_else_e_bloco() -> None:
    codigo = """
    if (x >= 0) {
        print(x);
    } else {
        {
            x = 0;
        }
    }
    """
    cst = _parse_source(codigo)
    cmd_if = cst.children[0].children[0]

    assert cmd_if.symbol == "condicional"
    assert [c.symbol for c in cmd_if.children] == [
        "IF",
        "LPAREN",
        "expressao",
        "RPAREN",
        "bloco",
        "ELSE",
        "bloco",
    ]


def test_parsing_programa_valido_completo() -> None:
    codigo = Path("exemplos/programa_valido.ml").read_text(encoding="utf-8")
    cst = _parse_source(codigo)

    assert cst.symbol == "programa"
    assert cst.children[-1].symbol == "EOF"