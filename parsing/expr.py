# autogenerated by ast_gen.py
import abc
from enum import auto, Enum
from typing import Optional
from parsing.source import SourceSpan
from typing import Any


class Expr(abc.ABC):
    __span: Optional[SourceSpan]

    @abc.abstractmethod
    def accept(self, visitor: 'ExprVisitor'):
        pass

    @property
    def span(self) -> Optional[SourceSpan]:
        return self.__span

    @span.setter
    def span(self, value: Optional[SourceSpan]):
        self.__span = value


class BinaryOperatorType(Enum):
    MINUS = auto()
    PLUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    NOT_EQUAL = auto()
    EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()


class BinaryOperator:
    def __init__(self, type: BinaryOperatorType, span: SourceSpan) -> None:
        self.__type = type
        self.__span = span

    @property
    def type(self) -> BinaryOperatorType:
        return self.__type
    @property
    def type(self) -> BinaryOperatorType:
        return self.__type

    @property
    def span(self) -> Optional[SourceSpan]:
        return self.__span


class UnaryOperatorType(Enum):
    NEGATE = auto()
    NOT = auto()


class UnaryOperator:
    def __init__(self, type: UnaryOperatorType, span: SourceSpan) -> None:
        self.__type = type
        self.__span = span

    @property
    def type(self) -> UnaryOperatorType:
        return self.__type
    @property
    def type(self) -> UnaryOperatorType:
        return self.__type

    @property
    def span(self) -> Optional[SourceSpan]:
        return self.__span


class Binary(Expr):
    def __init__(self, left: Expr, operator: BinaryOperator, right: Expr) -> None:
        self.__left = left
        self.__operator = operator
        self.__right = right

    def accept(self, visitor: 'ExprVisitor'):
        return visitor.visit_binary(self)

    @property
    def left(self) -> Expr:
        return self.__left

    @property
    def operator(self) -> BinaryOperator:
        return self.__operator

    @property
    def right(self) -> Expr:
        return self.__right


class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        self.__expression = expression

    def accept(self, visitor: 'ExprVisitor'):
        return visitor.visit_grouping(self)

    @property
    def expression(self) -> Expr:
        return self.__expression


class Literal(Expr):
    def __init__(self, value: Any) -> None:
        self.__value = value

    def accept(self, visitor: 'ExprVisitor'):
        return visitor.visit_literal(self)

    @property
    def value(self) -> Any:
        return self.__value


class Unary(Expr):
    def __init__(self, operator: UnaryOperator, expression: Expr) -> None:
        self.__operator = operator
        self.__expression = expression

    def accept(self, visitor: 'ExprVisitor'):
        return visitor.visit_unary(self)

    @property
    def operator(self) -> UnaryOperator:
        return self.__operator

    @property
    def expression(self) -> Expr:
        return self.__expression


class ExprVisitor:

    def visit_binary(self, node: Binary):
        pass

    def visit_grouping(self, node: Grouping):
        pass

    def visit_literal(self, node: Literal):
        pass

    def visit_unary(self, node: Unary):
        pass
