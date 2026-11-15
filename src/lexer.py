"""
Analisador Léxico (Lexer) da linguagem MiniLang.

Implementa um Autômato Finito Determinístico (AFD) explícito com 11 estados
(q0 a q10), estratégia de casamento mais longo (maximal munch) e rastreamento
de linha e coluna para diagnóstico preciso de erros léxicos.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional


class TokenType(Enum):

    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    PRINT = auto()
    TRUE = auto()
    FALSE = auto()


    ID = auto()
    INT_LITERAL = auto()


    PLUS = auto()       
    MINUS = auto()      
    STAR = auto()       
    SLASH = auto()      

    LT = auto()        
    GT = auto()        
    LE = auto()        
    GE = auto()        
    EQ = auto()      
    NEQ = auto()      

    ASSIGN = auto()    

    LPAREN = auto()     
    RPAREN = auto()     
    LBRACE = auto()     
    RBRACE = auto()     
    SEMICOLON = auto()  

    EOF = auto()


KEYWORDS: Dict[str, TokenType] = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "print": TokenType.PRINT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}

SINGLE_CHAR_TOKENS: Dict[str, TokenType] = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    ";": TokenType.SEMICOLON,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.lexeme!r}, {self.line}:{self.column})"


class LexicalError(Exception):
    """Exceção lançada quando a entrada viola as regras léxicas da MiniLang."""

    def __init__(self, message: str, line: int, column: int) -> None:
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Erro Léxico [linha {line}, coluna {column}]: {message}")


class Lexer:
    """
    AFD explícito para reconhecimento léxico de MiniLang.

    Estados do AFD:
      q0  : Estado inicial (ignora espaços e despacha início de lexema)
      q1  : Reconhecendo identificador ou palavra reservada [a-zA-Z_][a-zA-Z0-9_]*
      q2  : Reconhecendo literal inteiro [0-9]+
      q3  : Leu '/' (decide entre divisão '/', comentário '//' ou bloco '/*')
      q4  : Leu '=' (decide entre atribuição '=' e igualdade '==')
      q5  : Leu '<' (decide entre '<' e '<=')
      q6  : Leu '>' (decide entre '>' e '>=')
      q7  : Leu '!' (exige '=' para formar '!=')
      q8  : Dentro de comentário de linha '//' até '\\n' ou EOF
      q9  : Dentro de comentário de bloco '/*'
      q10 : Leu '*' dentro de comentário de bloco (aguarda '/' para fechar)
    """

    def __init__(self, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.pos = 0
        self.line = 1
        self.column = 1

    def _peek(self) -> Optional[str]:
        if self.pos >= self.length:
            return None
        return self.source[self.pos]

    def _advance(self) -> Optional[str]:
        if self.pos >= self.length:
            return None
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        state = "q0"
        lexeme_chars: List[str] = []
        start_line = 1
        start_col = 1

        while True:
            ch = self._peek()


            if state == "q0":
                if ch is None:
                    tokens.append(Token(TokenType.EOF, "", self.line, self.column))
                    break

                if ch in (" ", "\t", "\r", "\n"):
                    self._advance()
                    continue

                start_line = self.line
                start_col = self.column

                if ch.isalpha() or ch == "_":
                    lexeme_chars = [self._advance()] 
                    state = "q1"
                elif ch.isdigit():
                    lexeme_chars = [self._advance()]  
                    state = "q2"
                elif ch in SINGLE_CHAR_TOKENS:
                    self._advance()
                    tokens.append(Token(SINGLE_CHAR_TOKENS[ch], ch, start_line, start_col))
                elif ch == "/":
                    self._advance()
                    state = "q3"
                elif ch == "=":
                    self._advance()
                    state = "q4"
                elif ch == "<":
                    self._advance()
                    state = "q5"
                elif ch == ">":
                    self._advance()
                    state = "q6"
                elif ch == "!":
                    self._advance()
                    state = "q7"
                else:
                    raise LexicalError(
                        f"Caractere inválido '{ch}' fora do alfabeto da linguagem.",
                        start_line,
                        start_col,
                    )


            elif state == "q1":
                if ch is not None and (ch.isalnum() or ch == "_"):
                    lexeme_chars.append(self._advance()) 
                else:
                    lexeme = "".join(lexeme_chars)
                    token_type = KEYWORDS.get(lexeme, TokenType.ID)
                    tokens.append(Token(token_type, lexeme, start_line, start_col))
                    lexeme_chars = []
                    state = "q0"


            elif state == "q2":
                if ch is not None and ch.isdigit():
                    lexeme_chars.append(self._advance()) 
                elif ch is not None and (ch.isalpha() or ch == "_"):
                    while (nxt := self._peek()) is not None and (nxt.isalnum() or nxt == "_"):
                        lexeme_chars.append(self._advance())  
                    invalid_lexeme = "".join(lexeme_chars)
                    raise LexicalError(
                        f"Identificador ou literal numérico mal formado '{invalid_lexeme}'.",
                        start_line,
                        start_col,
                    )
                else:
                    lexeme = "".join(lexeme_chars)
                    tokens.append(Token(TokenType.INT_LITERAL, lexeme, start_line, start_col))
                    lexeme_chars = []
                    state = "q0"

            elif state == "q3":
                if ch == "/":
                    self._advance()
                    state = "q8"
                elif ch == "*":
                    self._advance()
                    state = "q9"
                else:
                    tokens.append(Token(TokenType.SLASH, "/", start_line, start_col))
                    state = "q0"


            elif state == "q4":
                if ch == "=":
                    self._advance()
                    tokens.append(Token(TokenType.EQ, "==", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.ASSIGN, "=", start_line, start_col))
                state = "q0"


            elif state == "q5":
                if ch == "=":
                    self._advance()
                    tokens.append(Token(TokenType.LE, "<=", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.LT, "<", start_line, start_col))
                state = "q0"


            elif state == "q6":
                if ch == "=":
                    self._advance()
                    tokens.append(Token(TokenType.GE, ">=", start_line, start_col))
                else:
                    tokens.append(Token(TokenType.GT, ">", start_line, start_col))
                state = "q0"


            elif state == "q7":
                if ch == "=":
                    self._advance()
                    tokens.append(Token(TokenType.NEQ, "!=", start_line, start_col))
                    state = "q0"
                else:
                    raise LexicalError(
                        "Operador '!' isolado não é suportado; esperado '!='.",
                        start_line,
                        start_col,
                    )


            elif state == "q8":
                if ch is None or ch == "\n":
                    state = "q0"
                else:
                    self._advance()


            elif state == "q9":
                if ch is None:
                    raise LexicalError(
                        "Comentário de bloco '/* ... */' não fechado antes do fim do arquivo.",
                        start_line,
                        start_col,
                    )
                if ch == "*":
                    self._advance()
                    state = "q10"
                else:
                    self._advance()


            elif state == "q10":
                if ch is None:
                    raise LexicalError(
                        "Comentário de bloco '/* ... */' não fechado antes do fim do arquivo.",
                        start_line,
                        start_col,
                    )
                if ch == "/":
                    self._advance()
                    state = "q0"
                elif ch == "*":
                    self._advance()
                else:
                    self._advance()
                    state = "q9"

        return tokens