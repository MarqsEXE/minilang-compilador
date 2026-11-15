"""
Definição formal dos nós da Árvore Sintática Abstrata (AST) da MiniLang.

Cada nó representa uma construção semântica relevante para a execução do programa,
descartando tokens puramente delimitadores (';', '(', ')', '{', '}') e níveis
intermediários de precedência da gramática, mas preservando linha e coluna
para diagnóstico preciso de erros semânticos.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ASTNode:
    """Classe base para todos os nós da Árvore Sintática Abstrata."""

    line: int
    column: int

    def pretty_print(self, indent: int = 0) -> str:
        """Retorna representação textual hierárquica da AST para inspeção e relatórios."""
        prefix = "  " * indent
        return f"{prefix}{self.__class__.__name__}"


class Statement(ASTNode):
    """Classe base para comandos (instruções que produzem efeito de estado ou controle)."""


class Expression(ASTNode):
    """Classe base para expressões (construtos que avaliam para um valor int ou bool)."""


@dataclass
class ProgramNode(ASTNode):
    """Nó raiz da AST: sequência ordenada de comandos do programa."""

    statements: List[Statement]

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}ProgramNode"]
        for stmt in self.statements:
            lines.append(stmt.pretty_print(indent + 1))
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Comandos (Statements)
# ----------------------------------------------------------------------


@dataclass
class AssignNode(Statement):
    """Atribuição de expressão a uma variável: <name> = <value>"""

    name: str
    value: Expression

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return (
            f"{prefix}AssignNode(var={self.name!r})\n"
            f"{self.value.pretty_print(indent + 1)}"
        )


@dataclass
class PrintNode(Statement):
    """Comando de saída padrão: print(<expression>)"""

    expression: Expression

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}PrintNode\n{self.expression.pretty_print(indent + 1)}"


@dataclass
class BlockNode(Statement):
    """Bloco sequencial de comandos delimitado por chaves: { <statements> }"""

    statements: List[Statement]

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [f"{prefix}BlockNode"]
        for stmt in self.statements:
            lines.append(stmt.pretty_print(indent + 1))
        return "\n".join(lines)


@dataclass
class IfNode(Statement):
    """Estrutura condicional: if (<condition>) <then_block> [else <else_block>]"""

    condition: Expression
    then_block: BlockNode
    else_block: Optional[BlockNode] = None

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        lines = [
            f"{prefix}IfNode",
            f"{prefix}  [condition]",
            self.condition.pretty_print(indent + 2),
            f"{prefix}  [then]",
            self.then_block.pretty_print(indent + 2),
        ]
        if self.else_block is not None:
            lines.append(f"{prefix}  [else]")
            lines.append(self.else_block.pretty_print(indent + 2))
        return "\n".join(lines)


@dataclass
class WhileNode(Statement):
    """Laço condicional: while (<condition>) <body>"""

    condition: Expression
    body: BlockNode

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return (
            f"{prefix}WhileNode\n"
            f"{prefix}  [condition]\n"
            f"{self.condition.pretty_print(indent + 2)}\n"
            f"{prefix}  [body]\n"
            f"{self.body.pretty_print(indent + 2)}"
        )


@dataclass
class ForNode(Statement):
    """
    Laço contado com três cláusulas obrigatórias:
    for (<init>; <condition>; <update>) <body>
    """

    init: AssignNode
    condition: Expression
    update: AssignNode
    body: BlockNode

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return (
            f"{prefix}ForNode\n"
            f"{prefix}  [init]\n"
            f"{self.init.pretty_print(indent + 2)}\n"
            f"{prefix}  [condition]\n"
            f"{self.condition.pretty_print(indent + 2)}\n"
            f"{prefix}  [update]\n"
            f"{self.update.pretty_print(indent + 2)}\n"
            f"{prefix}  [body]\n"
            f"{self.body.pretty_print(indent + 2)}"
        )


# ----------------------------------------------------------------------
# Expressões (Expressions)
# ----------------------------------------------------------------------


@dataclass
class BinaryOpNode(Expression):
    """Operação binária: <left> <operator> <right>"""

    left: Expression
    operator: str
    right: Expression

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return (
            f"{prefix}BinaryOpNode(op={self.operator!r})\n"
            f"{self.left.pretty_print(indent + 1)}\n"
            f"{self.right.pretty_print(indent + 1)}"
        )


@dataclass
class IntLiteralNode(Expression):
    """Literal numérico inteiro (ex.: 42)."""

    value: int

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}IntLiteralNode({self.value})"


@dataclass
class BoolLiteralNode(Expression):
    """Literal booleano (true ou false)."""

    value: bool

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}BoolLiteralNode({self.value})"


@dataclass
class VarNode(Expression):
    """Referência de leitura a uma variável (ex.: x)."""

    name: str

    def pretty_print(self, indent: int = 0) -> str:
        prefix = "  " * indent
        return f"{prefix}VarNode({self.name!r})"