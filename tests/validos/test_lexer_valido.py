"""Testes unitários para entradas léxicas válidas da MiniLang."""

from pathlib import Path
from src.lexer import Lexer, TokenType


def test_tokens_basicos_e_palavras_reservadas() -> None:
    codigo = "if else while for print true false x _var1 42"
    tokens = Lexer(codigo).tokenize()

    tipos = [t.type for t in tokens]
    assert tipos == [
        TokenType.IF,
        TokenType.ELSE,
        TokenType.WHILE,
        TokenType.FOR,
        TokenType.PRINT,
        TokenType.TRUE,
        TokenType.FALSE,
        TokenType.ID,
        TokenType.ID,
        TokenType.INT_LITERAL,
        TokenType.EOF,
    ]


def test_operadores_simples_e_compostos_maximal_munch() -> None:
    codigo = "+ - * / = == != < <= > >= ( ) { } ;"
    tokens = Lexer(codigo).tokenize()

    tipos = [t.type for t in tokens]
    assert tipos == [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.ASSIGN,
        TokenType.EQ,
        TokenType.NEQ,
        TokenType.LT,
        TokenType.LE,
        TokenType.GT,
        TokenType.GE,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]


def test_comentarios_de_linha_e_bloco_ignorados() -> None:
    codigo = """
    // Comentario de linha no inicio
    x = 10; // Comentario apos comando
    /* Comentario de bloco
       com multiplas linhas e * asteriscos ** internos */
    y = x / 2;
    """
    tokens = Lexer(codigo).tokenize()
    pares = [(t.type, t.lexeme) for t in tokens]

    assert pares == [
        (TokenType.ID, "x"),
        (TokenType.ASSIGN, "="),
        (TokenType.INT_LITERAL, "10"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.ID, "y"),
        (TokenType.ASSIGN, "="),
        (TokenType.ID, "x"),
        (TokenType.SLASH, "/"),
        (TokenType.INT_LITERAL, "2"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.EOF, ""),
    ]


def test_rastreamento_de_linha_e_coluna() -> None:
    codigo = "x = 10;\nwhile (x > 0) {\n  x = x - 1;\n}"
    tokens = Lexer(codigo).tokenize()

    # 'x' na linha 1, coluna 1
    assert (tokens[0].lexeme, tokens[0].line, tokens[0].column) == ("x", 1, 1)
    # 'while' na linha 2, coluna 1
    assert (tokens[4].lexeme, tokens[4].line, tokens[4].column) == ("while", 2, 1)
    # '-' na linha 3, coluna 9
    menos = [t for t in tokens if t.type == TokenType.MINUS][0]
    assert (menos.line, menos.column) == (3, 9)


def test_programa_valido_exemplo_completo() -> None:
    caminho = Path("exemplos/programa_valido.ml")
    codigo = caminho.read_text(encoding="utf-8")
    tokens = Lexer(codigo).tokenize()

    assert tokens[-1].type == TokenType.EOF
    assert any(t.type == TokenType.WHILE for t in tokens)
    assert any(t.type == TokenType.FOR for t in tokens)