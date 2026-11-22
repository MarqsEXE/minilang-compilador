"""
Tabela de Símbolos e Interpretador sobre a AST da linguagem MiniLang.

Executa programas validados sintaticamente por meio de percurso em profundidade
na Árvore Sintática Abstrata (AST), realizando verificação estática/dinâmica de
tipos (int e bool), controle de tabela de símbolos global e diagnóstico preciso
de erros semânticos com linha e coluna.
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union

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
from src.lexer import Lexer, LexicalError
from src.parser import Parser, MiniLangSyntaxError

RuntimeValue = Union[int, bool]


class SemanticError(Exception):
    """Exceção lançada quando o programa viola regras semânticas da MiniLang."""

    def __init__(self, message: str, line: int, column: int) -> None:
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Erro Semântico [linha {line}, coluna {column}]: {message}")


@dataclass
class SymbolEntry:
    """Registro armazenado na Tabela de Símbolos para cada variável."""

    name: str
    var_type: str  # "int" ou "bool"
    value: RuntimeValue
    defined_line: int


class SymbolTable:
    """
    Tabela de Símbolos global da MiniLang baseada em tabela hash (dict).

    Como a especificação da MiniLang define escopo global único (sem funções e
    sem escopo aninhado em blocos), um mapeamento plano identificador -> SymbolEntry
    oferece inserção e busca em tempo médio O(1).
    """

    def __init__(self) -> None:
        self._symbols: Dict[str, SymbolEntry] = {}

    @staticmethod
    def infer_type(value: RuntimeValue) -> str:
        # Em Python, bool é subclasse de int (isinstance(True, int) == True);
        # por isso testamos bool explicitamente antes de int.
        if isinstance(value, bool):
            return "bool"
        if type(value) is int:
            return "int"
        raise TypeError(f"Tipo de dado não suportado em tempo de execução: {type(value).__name__}")

    def insert(self, name: str, value: RuntimeValue, line: int) -> SymbolEntry:
        """Insere uma nova variável ou atualiza seu valor e tipo na tabela."""
        var_type = self.infer_type(value)
        entry = SymbolEntry(
            name=name,
            var_type=var_type,
            value=value,
            defined_line=line,
        )
        self._symbols[name] = entry
        return entry

    def lookup(self, name: str, line: int, column: int) -> SymbolEntry:
        """Busca uma variável pelo identificador; falha se não foi definida."""
        if name not in self._symbols:
            raise SemanticError(
                f"Variável '{name}' não definida antes do uso.",
                line,
                column,
            )
        return self._symbols[name]

    def exists(self, name: str) -> bool:
        return name in self._symbols

    def snapshot(self) -> Dict[str, SymbolEntry]:
        return dict(self._symbols)


class Interpreter:
    """
    Interpretador AST da MiniLang.

    Implementa a semântica operacional de comandos (atribuição, print, blocos,
    if/else, while, for) e expressões tipadas (int e bool), com proteção contra
    laços infinitos via limite configurável de iterações.
    """

    def __init__(self, max_iterations: int = 100_000, echo_stdout: bool = False) -> None:
        self.symbol_table = SymbolTable()
        self.max_iterations = max_iterations
        self.echo_stdout = echo_stdout
        self.outputs: List[str] = []

    @staticmethod
    def _is_bool(val: RuntimeValue) -> bool:
        return isinstance(val, bool)

    @staticmethod
    def _is_int(val: RuntimeValue) -> bool:
        return type(val) is int

    @staticmethod
    def _type_label(val: RuntimeValue) -> str:
        return "bool" if isinstance(val, bool) else "int"

    @staticmethod
    def _format_value(val: RuntimeValue) -> str:
        if isinstance(val, bool):
            return "true" if val else "false"
        return str(val)

    # ------------------------------------------------------------------
    # Ponto de entrada da execução
    # ------------------------------------------------------------------

    def execute(self, program: ProgramNode) -> List[str]:
        """Executa toda a AST de um programa e retorna a lista de saídas emitidas."""
        for stmt in program.statements:
            self._exec_statement(stmt)
        return self.outputs

    # ------------------------------------------------------------------
    # Semântica Operacional dos Comandos (Statements)
    # ------------------------------------------------------------------

    def _exec_statement(self, stmt: Statement) -> None:
        if isinstance(stmt, AssignNode):
            self._exec_assign(stmt)
        elif isinstance(stmt, PrintNode):
            self._exec_print(stmt)
        elif isinstance(stmt, BlockNode):
            self._exec_block(stmt)
        elif isinstance(stmt, IfNode):
            self._exec_if(stmt)
        elif isinstance(stmt, WhileNode):
            self._exec_while(stmt)
        elif isinstance(stmt, ForNode):
            self._exec_for(stmt)
        else:
            raise SemanticError(
                f"Nó de comando desconhecido na AST: {type(stmt).__name__}.",
                stmt.line,
                stmt.column,
            )

    def _exec_assign(self, node: AssignNode) -> None:
        # Avalia o lado direito primeiro (garante que 'x = x + 1;' falhe se 'x' não existir)
        value = self._eval_expression(node.value)
        self.symbol_table.insert(node.name, value, node.line)

    def _exec_print(self, node: PrintNode) -> None:
        value = self._eval_expression(node.expression)
        formatted = self._format_value(value)
        self.outputs.append(formatted)
        if self.echo_stdout:
            print(formatted)

    def _exec_block(self, node: BlockNode) -> None:
        for stmt in node.statements:
            self._exec_statement(stmt)

    def _exec_if(self, node: IfNode) -> None:
        cond_val = self._eval_expression(node.condition)
        if not self._is_bool(cond_val):
            raise SemanticError(
                f"Condição do comando 'if' deve ser booleana (bool), mas recebeu '{self._type_label(cond_val)}'.",
                node.condition.line,
                node.condition.column,
            )
        if cond_val:
            self._exec_block(node.then_block)
        elif node.else_block is not None:
            self._exec_block(node.else_block)

    def _exec_while(self, node: WhileNode) -> None:
        iterations = 0
        while True:
            cond_val = self._eval_expression(node.condition)
            if not self._is_bool(cond_val):
                raise SemanticError(
                    f"Condição do laço 'while' deve ser booleana (bool), mas recebeu '{self._type_label(cond_val)}'.",
                    node.condition.line,
                    node.condition.column,
                )
            if not cond_val:
                break

            iterations += 1
            if iterations > self.max_iterations:
                raise SemanticError(
                    f"Limite máximo de iterações ({self.max_iterations}) excedido no laço 'while' (possível laço infinito).",
                    node.line,
                    node.column,
                )

            self._exec_block(node.body)

    def _exec_for(self, node: ForNode) -> None:
        # 1. Executa a cláusula de inicialização (atribuição)
        self._exec_assign(node.init)

        iterations = 0
        while True:
            # 2. Testa a condição (obrigatoriamente booleana)
            cond_val = self._eval_expression(node.condition)
            if not self._is_bool(cond_val):
                raise SemanticError(
                    f"Condição do laço 'for' deve ser booleana (bool), mas recebeu '{self._type_label(cond_val)}'.",
                    node.condition.line,
                    node.condition.column,
                )
            if not cond_val:
                break

            iterations += 1
            if iterations > self.max_iterations:
                raise SemanticError(
                    f"Limite máximo de iterações ({self.max_iterations}) excedido no laço 'for' (possível laço infinito).",
                    node.line,
                    node.column,
                )

            # 3. Executa o corpo do laço
            self._exec_block(node.body)

            # 4. Executa a cláusula de atualização (atribuição) e repete
            self._exec_assign(node.update)

    # ------------------------------------------------------------------
    # Avaliação Tipada de Expressões
    # ------------------------------------------------------------------

    def _eval_expression(self, expr: Expression) -> RuntimeValue:
        if isinstance(expr, IntLiteralNode):
            return expr.value

        if isinstance(expr, BoolLiteralNode):
            return expr.value

        if isinstance(expr, VarNode):
            entry = self.symbol_table.lookup(expr.name, expr.line, expr.column)
            return entry.value

        if isinstance(expr, BinaryOpNode):
            return self._eval_binary_op(expr)

        raise SemanticError(
            f"Nó de expressão desconhecido na AST: {type(expr).__name__}.",
            expr.line,
            expr.column,
        )

    def _eval_binary_op(self, node: BinaryOpNode) -> RuntimeValue:
        left = self._eval_expression(node.left)
        right = self._eval_expression(node.right)
        op = node.operator

        # Operadores aritméticos: exigem (int, int) -> int
        if op in ("+", "-", "*", "/"):
            if not (self._is_int(left) and self._is_int(right)):
                raise SemanticError(
                    f"Operador aritmético '{op}' exige operandos inteiros (int), "
                    f"mas recebeu '{self._type_label(left)}' e '{self._type_label(right)}'.",
                    node.line,
                    node.column,
                )
            assert isinstance(left, int) and isinstance(right, int)
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                if right == 0:
                    raise SemanticError(
                        "Divisão por zero.",
                        node.line,
                        node.column,
                    )
                # Divisão inteira truncada em direção a zero
                quotient = abs(left) // abs(right)
                if (left < 0) != (right < 0):
                    quotient = -quotient
                return quotient

        # Operadores relacionais: exigem (int, int) -> bool
        if op in ("<", ">", "<=", ">="):
            if not (self._is_int(left) and self._is_int(right)):
                raise SemanticError(
                    f"Operador relacional '{op}' exige operandos inteiros (int), "
                    f"mas recebeu '{self._type_label(left)}' e '{self._type_label(right)}'.",
                    node.line,
                    node.column,
                )
            assert isinstance(left, int) and isinstance(right, int)
            if op == "<":
                return left < right
            if op == ">":
                return left > right
            if op == "<=":
                return left <= right
            if op == ">=":
                return left >= right

        # Operadores de igualdade: exigem dois operandos do mesmo tipo (T, T) -> bool
        if op in ("==", "!="):
            left_type = self._type_label(left)
            right_type = self._type_label(right)
            if left_type != right_type:
                raise SemanticError(
                    f"Operador '{op}' exige operandos do mesmo tipo, "
                    f"mas recebeu '{left_type}' e '{right_type}'.",
                    node.line,
                    node.column,
                )
            return (left == right) if op == "==" else (left != right)

        raise SemanticError(
            f"Operador binário não suportado: '{op}'.",
            node.line,
            node.column,
        )


def run_source(source: str, max_iterations: int = 100_000, echo_stdout: bool = False) -> List[str]:
    """Pipeline completo: código-fonte -> Lexer -> Parser (AST) -> Interpreter."""
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse_ast()
    interpreter = Interpreter(max_iterations=max_iterations, echo_stdout=echo_stdout)
    return interpreter.execute(ast)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python3 -m src.interpreter <arquivo.ml>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Arquivo não encontrado: {file_path}", file=sys.stderr)
        sys.exit(1)

    source = file_path.read_text(encoding="utf-8")
    try:
        run_source(source, echo_stdout=True)
    except (LexicalError, MiniLangSyntaxError, SemanticError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()