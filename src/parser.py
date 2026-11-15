"""
Analisador Sintático (Parser) Descendente Recursivo Preditivo LL(1) da MiniLang.

Constrói a Árvore Sintática Concreta (CST) a partir da lista de tokens produzida
pelo Lexer, respeitando a hierarquia de precedência e associatividade definida
na gramática EBNF da linguagem.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from src.ast_nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolLiteralNode,
    Expression,
    ForNode,
    IfNode,
    IntLiteralNode,
    PrintNode,
    ProgramNode,
    Statement,
    VarNode,
    WhileNode,
)
from src.lexer import Token, TokenType

class MiniLangSyntaxError(Exception):
    """Exceção lançada quando a sequência de tokens viola a gramática da MiniLang."""

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        found_token: Optional[Token] = None,
    ) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.found_token = found_token
        super().__init__(f"Erro Sintático [linha {line}, coluna {column}]: {message}")


@dataclass
class ParseNode:
    """
    Nó da Árvore Sintática Concreta (CST).
    Representa tanto símbolos não terminais (regras da gramática) quanto
    folhas terminais (tokens consumidos).
    """

    symbol: str
    token: Optional[Token] = None
    children: List["ParseNode"] = field(default_factory=list)

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        if self.token is not None:
            return f"{prefix}{self.symbol} ({self.token.lexeme!r})"
        lines = [f"{prefix}{self.symbol}"]
        for child in self.children:
            lines.append(child.pretty_print(indent + 1))
        return "\n".join(lines)


class Parser:
    """
    Parser Descendente Recursivo LL(1) escrito à mão para a MiniLang.
    Cada método _parse_<nao_terminal> corresponde diretamente a uma produção da EBNF.
    """

    def __init__(self, tokens: List[Token]) -> None:
        if not tokens:
            raise MiniLangSyntaxError("Lista de tokens vazia.", 1, 1)
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------------
    # Primitivas de navegação e consumo de tokens (Lookahead LL(1))
    # ------------------------------------------------------------------

    def _current(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self._current()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> bool:
        return self._current().type in types

    def _expect_token(self, expected_type: TokenType, error_message: str) -> Token:
        tok = self._current()
        if tok.type != expected_type:
            found_desc = "fim de arquivo (EOF)" if tok.type == TokenType.EOF else f"'{tok.lexeme}'"
            raise MiniLangSyntaxError(
                f"{error_message} Encontrado: {found_desc}.",
                tok.line,
                tok.column,
                tok,
            )
        return self._advance()

   def _expect(self, expected_type: TokenType, error_message: str) -> ParseNode:
        consumed = self._expect_token(expected_type, error_message)
        return ParseNode(symbol=consumed.type.name, token=consumed)


    # ------------------------------------------------------------------
    # Ponto de entrada público
    # ------------------------------------------------------------------

    def parse_cst(self) -> ParseNode:
        """Analisa todo o programa e retorna a raiz da Árvore Sintática Concreta."""
       self.pos = 0
        return self._parse_programa()

    def parse(self) -> ParseNode:
        """Ponto de entrada principal da fase sintática."""
        return self.parse_cst()
    
    def parse_ast(self) -> ProgramNode:
        """Analisa o programa e retorna a raiz da Árvore Sintática Abstrata (AST)."""
        self.pos = 0
        return self._ast_programa()

    # ------------------------------------------------------------------
    # Produções da Gramática EBNF
    # ------------------------------------------------------------------

    def _parse_programa(self) -> ParseNode:
        # programa = { comando } EOF ;
        children: List[ParseNode] = []
        while not self._match(TokenType.EOF):
            children.append(self._parse_comando())
        children.append(self._expect(TokenType.EOF, "Esperado fim de arquivo."))
        return ParseNode("programa", children=children)

    def _parse_comando(self) -> ParseNode:
        # comando = atribuicao ";"
        #         | impressao ";"
        #         | condicional
        #         | laco_while
        #         | laco_for
        #         | bloco ;
        tok = self._current()

        if tok.type == TokenType.ID:
            attr_node = self._parse_atribuicao()
            semi_node = self._expect(
                TokenType.SEMICOLON,
                "Esperado ';' ao final do comando de atribuição.",
            )
            return ParseNode("comando", children=[attr_node, semi_node])

        if tok.type == TokenType.PRINT:
            print_node = self._parse_impressao()
            semi_node = self._expect(
                TokenType.SEMICOLON,
                "Esperado ';' ao final do comando 'print'.",
            )
            return ParseNode("comando", children=[print_node, semi_node])

        if tok.type == TokenType.IF:
            return ParseNode("comando", children=[self._parse_condicional()])

        if tok.type == TokenType.WHILE:
            return ParseNode("comando", children=[self._parse_laco_while()])

        if tok.type == TokenType.FOR:
            return ParseNode("comando", children=[self._parse_laco_for()])

        if tok.type == TokenType.LBRACE:
            return ParseNode("comando", children=[self._parse_bloco()])

        found_desc = "fim de arquivo (EOF)" if tok.type == TokenType.EOF else f"'{tok.lexeme}'"
        raise MiniLangSyntaxError(
            f"Início de comando inválido: {found_desc}. Esperado identificador, 'print', 'if', 'while', 'for' ou '{{'.",
            tok.line,
            tok.column,
            tok,
        )

    def _parse_atribuicao(self) -> ParseNode:
        # atribuicao = ID "=" expressao ;
        id_node = self._expect(TokenType.ID, "Esperado identificador na atribuição.")
        assign_node = self._expect(TokenType.ASSIGN, "Esperado '=' após o identificador na atribuição.")
        expr_node = self._parse_expressao()
        return ParseNode("atribuicao", children=[id_node, assign_node, expr_node])

    def _parse_impressao(self) -> ParseNode:
        # impressao = "print" "(" expressao ")" ;
        print_kw = self._expect(TokenType.PRINT, "Esperado palavra reservada 'print'.")
        lparen = self._expect(TokenType.LPAREN, "Esperado '(' após 'print'.")
        expr = self._parse_expressao()
        rparen = self._expect(TokenType.RPAREN, "Esperado ')' após a expressão de 'print'.")
        return ParseNode("impressao", children=[print_kw, lparen, expr, rparen])

    def _parse_condicional(self) -> ParseNode:
        # condicional = "if" "(" expressao ")" bloco [ "else" bloco ] ;
        if_kw = self._expect(TokenType.IF, "Esperado palavra reservada 'if'.")
        lparen = self._expect(TokenType.LPAREN, "Esperado '(' após 'if'.")
        cond = self._parse_expressao()
        rparen = self._expect(TokenType.RPAREN, "Esperado ')' após a condição do 'if'.")
        then_block = self._parse_bloco()

        children = [if_kw, lparen, cond, rparen, then_block]
        if self._match(TokenType.ELSE):
            else_kw = self._expect(TokenType.ELSE, "Esperado 'else'.")
            else_block = self._parse_bloco()
            children.extend([else_kw, else_block])

        return ParseNode("condicional", children=children)

    def _parse_laco_while(self) -> ParseNode:
        # laco_while = "while" "(" expressao ")" bloco ;
        while_kw = self._expect(TokenType.WHILE, "Esperado palavra reservada 'while'.")
        lparen = self._expect(TokenType.LPAREN, "Esperado '(' após 'while'.")
        cond = self._parse_expressao()
        rparen = self._expect(TokenType.RPAREN, "Esperado ')' após a condição do 'while'.")
        body = self._parse_bloco()
        return ParseNode("laco_while", children=[while_kw, lparen, cond, rparen, body])

    def _parse_laco_for(self) -> ParseNode:
        # laco_for = "for" "(" atribuicao ";" expressao ";" atribuicao ")" bloco ;
        for_kw = self._expect(TokenType.FOR, "Esperado palavra reservada 'for'.")
        lparen = self._expect(TokenType.LPAREN, "Esperado '(' após 'for'.")
        init_clause = self._parse_atribuicao()
        semi1 = self._expect(
            TokenType.SEMICOLON,
            "Esperado ';' após a cláusula de inicialização do 'for'.",
        )
        cond_clause = self._parse_expressao()
        semi2 = self._expect(
            TokenType.SEMICOLON,
            "Esperado ';' após a condição do 'for' (a cláusula de atualização é obrigatória).",
        )
        update_clause = self._parse_atribuicao()
        rparen = self._expect(
            TokenType.RPAREN,
            "Esperado ')' após a cláusula de atualização do 'for'.",
        )
        body = self._parse_bloco()
        return ParseNode(
            "laco_for",
            children=[for_kw, lparen, init_clause, semi1, cond_clause, semi2, update_clause, rparen, body],
        )

    def _parse_bloco(self) -> ParseNode:
        # bloco = "{" { comando } "}" ;
        lbrace = self._expect(TokenType.LBRACE, "Esperado '{' para iniciar bloco de comandos.")
        children: List[ParseNode] = [lbrace]
        while not self._match(TokenType.RBRACE, TokenType.EOF):
            children.append(self._parse_comando())
        rbrace = self._expect(TokenType.RBRACE, "Esperado '}' para fechar bloco de comandos.")
        children.append(rbrace)
        return ParseNode("bloco", children=children)

    # ------------------------------------------------------------------
    # Hierarquia de Expressões (Precedência e Associatividade)
    # ------------------------------------------------------------------

    def _parse_expressao(self) -> ParseNode:
        # expressao = expr_igualdade ;
        return ParseNode("expressao", children=[self._parse_expr_igualdade()])

    def _parse_expr_igualdade(self) -> ParseNode:
        # expr_igualdade = expr_relacional { ( "==" | "!=" ) expr_relacional } ;
        children = [self._parse_expr_relacional()]
        while self._match(TokenType.EQ, TokenType.NEQ):
            op_tok = self._advance()
            children.append(ParseNode(op_tok.type.name, token=op_tok))
            children.append(self._parse_expr_relacional())
        return ParseNode("expr_igualdade", children=children)

    def _parse_expr_relacional(self) -> ParseNode:
        # expr_relacional = expr_aritmetica [ ( "<" | ">" | "<=" | ">=" ) expr_aritmetica ] ;
        children = [self._parse_expr_aritmetica()]
        if self._match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_tok = self._advance()
            children.append(ParseNode(op_tok.type.name, token=op_tok))
            children.append(self._parse_expr_aritmetica())
        return ParseNode("expr_relacional", children=children)

    def _parse_expr_aritmetica(self) -> ParseNode:
        # expr_aritmetica = termo { ( "+" | "-" ) termo } ;
        children = [self._parse_termo()]
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            children.append(ParseNode(op_tok.type.name, token=op_tok))
            children.append(self._parse_termo())
        return ParseNode("expr_aritmetica", children=children)

    def _parse_termo(self) -> ParseNode:
        # termo = fator { ( "*" | "/" ) fator } ;
        children = [self._parse_fator()]
        while self._match(TokenType.STAR, TokenType.SLASH):
            op_tok = self._advance()
            children.append(ParseNode(op_tok.type.name, token=op_tok))
            children.append(self._parse_fator())
        return ParseNode("termo", children=children)

    def _parse_fator(self) -> ParseNode:
        # fator = INT_LITERAL | "true" | "false" | ID | "(" expressao ")" ;
        tok = self._current()

        if tok.type in (TokenType.INT_LITERAL, TokenType.TRUE, TokenType.FALSE, TokenType.ID):
            consumed = self._advance()
            return ParseNode("fator", children=[ParseNode(consumed.type.name, token=consumed)])

        if tok.type == TokenType.LPAREN:
            lparen = self._expect(TokenType.LPAREN, "Esperado '('.")
            expr = self._parse_expressao()
            rparen = self._expect(TokenType.RPAREN, "Esperado ')' para fechar expressão entre parênteses.")
            return ParseNode("fator", children=[lparen, expr, rparen])

        found_desc = "fim de arquivo (EOF)" if tok.type == TokenType.EOF else f"'{tok.lexeme}'"
        raise MiniLangSyntaxError(
            f"Expressão inválida: esperado número inteiro, booleano, identificador ou '(', encontrado {found_desc}.",
            tok.line,
            tok.column,
            tok,
        )
        
    # ------------------------------------------------------------------
    # Construção Direta da Árvore Sintática Abstrata (AST)
    # ------------------------------------------------------------------

    def _ast_programa(self) -> ProgramNode:
        first_tok = self._current()
        statements: List[Statement] = []
        while not self._match(TokenType.EOF):
            statements.append(self._ast_comando())
        self._expect_token(TokenType.EOF, "Esperado fim de arquivo.")
        return ProgramNode(line=first_tok.line, column=first_tok.column, statements=statements)

    def _ast_comando(self) -> Statement:
        tok = self._current()

        if tok.type == TokenType.ID:
            stmt = self._ast_atribuicao()
            self._expect_token(TokenType.SEMICOLON, "Esperado ';' ao final do comando de atribuição.")
            return stmt

        if tok.type == TokenType.PRINT:
            stmt = self._ast_impressao()
            self._expect_token(TokenType.SEMICOLON, "Esperado ';' ao final do comando 'print'.")
            return stmt

        if tok.type == TokenType.IF:
            return self._ast_condicional()

        if tok.type == TokenType.WHILE:
            return self._ast_laco_while()

        if tok.type == TokenType.FOR:
            return self._ast_laco_for()

        if tok.type == TokenType.LBRACE:
            return self._ast_bloco()

        found_desc = "fim de arquivo (EOF)" if tok.type == TokenType.EOF else f"'{tok.lexeme}'"
        raise MiniLangSyntaxError(
            f"Início de comando inválido: {found_desc}. Esperado identificador, 'print', 'if', 'while', 'for' ou '{{'.",
            tok.line,
            tok.column,
            tok,
        )

    def _ast_atribuicao(self) -> AssignNode:
        id_tok = self._expect_token(TokenType.ID, "Esperado identificador na atribuição.")
        self._expect_token(TokenType.ASSIGN, "Esperado '=' após o identificador na atribuição.")
        expr = self._ast_expressao()
        return AssignNode(line=id_tok.line, column=id_tok.column, name=id_tok.lexeme, value=expr)

    def _ast_impressao(self) -> PrintNode:
        print_tok = self._expect_token(TokenType.PRINT, "Esperado palavra reservada 'print'.")
        self._expect_token(TokenType.LPAREN, "Esperado '(' após 'print'.")
        expr = self._ast_expressao()
        self._expect_token(TokenType.RPAREN, "Esperado ')' após a expressão de 'print'.")
        return PrintNode(line=print_tok.line, column=print_tok.column, expression=expr)

    def _ast_condicional(self) -> IfNode:
        if_tok = self._expect_token(TokenType.IF, "Esperado palavra reservada 'if'.")
        self._expect_token(TokenType.LPAREN, "Esperado '(' após 'if'.")
        cond = self._ast_expressao()
        self._expect_token(TokenType.RPAREN, "Esperado ')' após a condição do 'if'.")
        then_block = self._ast_bloco()

        else_block: Optional[BlockNode] = None
        if self._match(TokenType.ELSE):
            self._expect_token(TokenType.ELSE, "Esperado 'else'.")
            else_block = self._ast_bloco()

        return IfNode(
            line=if_tok.line,
            column=if_tok.column,
            condition=cond,
            then_block=then_block,
            else_block=else_block,
        )

    def _ast_laco_while(self) -> WhileNode:
        while_tok = self._expect_token(TokenType.WHILE, "Esperado palavra reservada 'while'.")
        self._expect_token(TokenType.LPAREN, "Esperado '(' após 'while'.")
        cond = self._ast_expressao()
        self._expect_token(TokenType.RPAREN, "Esperado ')' após a condição do 'while'.")
        body = self._ast_bloco()
        return WhileNode(line=while_tok.line, column=while_tok.column, condition=cond, body=body)

    def _ast_laco_for(self) -> ForNode:
        for_tok = self._expect_token(TokenType.FOR, "Esperado palavra reservada 'for'.")
        self._expect_token(TokenType.LPAREN, "Esperado '(' após 'for'.")
        init_clause = self._ast_atribuicao()
        self._expect_token(
            TokenType.SEMICOLON,
            "Esperado ';' após a cláusula de inicialização do 'for'.",
        )
        cond_clause = self._ast_expressao()
        self._expect_token(
            TokenType.SEMICOLON,
            "Esperado ';' após a condição do 'for' (a cláusula de atualização é obrigatória).",
        )
        update_clause = self._ast_atribuicao()
        self._expect_token(
            TokenType.RPAREN,
            "Esperado ')' após a cláusula de atualização do 'for'.",
        )
        body = self._ast_bloco()
        return ForNode(
            line=for_tok.line,
            column=for_tok.column,
            init=init_clause,
            condition=cond_clause,
            update=update_clause,
            body=body,
        )

    def _ast_bloco(self) -> BlockNode:
        lbrace_tok = self._expect_token(TokenType.LBRACE, "Esperado '{' para iniciar bloco de comandos.")
        statements: List[Statement] = []
        while not self._match(TokenType.RBRACE, TokenType.EOF):
            statements.append(self._ast_comando())
        self._expect_token(TokenType.RBRACE, "Esperado '}' para fechar bloco de comandos.")
        return BlockNode(line=lbrace_tok.line, column=lbrace_tok.column, statements=statements)

    def _ast_expressao(self) -> Expression:
        return self._ast_expr_igualdade()

    def _ast_expr_igualdade(self) -> Expression:
        left = self._ast_expr_relacional()
        while self._match(TokenType.EQ, TokenType.NEQ):
            op_tok = self._advance()
            right = self._ast_expr_relacional()
            left = BinaryOpNode(line=op_tok.line, column=op_tok.column, left=left, operator=op_tok.lexeme, right=right)
        return left

    def _ast_expr_relacional(self) -> Expression:
        left = self._ast_expr_aritmetica()
        if self._match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_tok = self._advance()
            right = self._ast_expr_aritmetica()
            left = BinaryOpNode(line=op_tok.line, column=op_tok.column, left=left, operator=op_tok.lexeme, right=right)
        return left

    def _ast_expr_aritmetica(self) -> Expression:
        left = self._ast_termo()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._ast_termo()
            left = BinaryOpNode(line=op_tok.line, column=op_tok.column, left=left, operator=op_tok.lexeme, right=right)
        return left

    def _ast_termo(self) -> Expression:
        left = self._ast_fator()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op_tok = self._advance()
            right = self._ast_fator()
            left = BinaryOpNode(line=op_tok.line, column=op_tok.column, left=left, operator=op_tok.lexeme, right=right)
        return left

    def _ast_fator(self) -> Expression:
        tok = self._current()

        if tok.type == TokenType.INT_LITERAL:
            self._advance()
            return IntLiteralNode(line=tok.line, column=tok.column, value=int(tok.lexeme))

        if tok.type == TokenType.TRUE:
            self._advance()
            return BoolLiteralNode(line=tok.line, column=tok.column, value=True)

        if tok.type == TokenType.FALSE:
            self._advance()
            return BoolLiteralNode(line=tok.line, column=tok.column, value=False)

        if tok.type == TokenType.ID:
            self._advance()
            return VarNode(line=tok.line, column=tok.column, name=tok.lexeme)

        if tok.type == TokenType.LPAREN:
            self._expect_token(TokenType.LPAREN, "Esperado '('.")
            expr = self._ast_expressao()
            self._expect_token(TokenType.RPAREN, "Esperado ')' para fechar expressão entre parênteses.")
            return expr

        found_desc = "fim de arquivo (EOF)" if tok.type == TokenType.EOF else f"'{tok.lexeme}'"
        raise MiniLangSyntaxError(
            f"Expressão inválida: esperado número inteiro, booleano, identificador ou '(', encontrado {found_desc}.",
            tok.line,
            tok.column,
            tok,
        )

