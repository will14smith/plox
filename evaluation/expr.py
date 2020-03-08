from typing import Any, Callable, Dict

import parsing.expr as exprs
from parsing.expr import Expr, ExprVisitor
from parsing.source import SourceSpan

BinaryOpHandler = Callable[['ExpressionEvaluator', exprs.Binary, Any, Any], Any]
UnaryOpHandler = Callable[['ExpressionEvaluator', exprs.Unary, Any], Any]


def is_truthy(value: Any) -> bool:
    if value is None:
        return False
    if not value:
        return False

    return True


def is_equal(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None:
        return False

    return a == b


def to_string(value: Any) -> str:
    if value is None:
        return "nil"

    text = str(value)

    if isinstance(value, float) and text.endswith(".0"):
        text = text[:-2]

    return text


def number_binary_op(handler: BinaryOpHandler) -> BinaryOpHandler:
    def wrapped(self: 'ExprEvaluator', node: exprs.Binary, left: Any, right: Any):
        self.assert_numeric(node.left.span, left)
        self.assert_numeric(node.right.span, right)

        return handler(self, node, left, right)

    return wrapped


def number_unary_op(handler: UnaryOpHandler) -> UnaryOpHandler:
    def wrapped(self: 'ExprEvaluator', node: exprs.Unary, value: Any):
        self.assert_numeric(node.expression.span, value)

        return handler(self, node, value)

    return wrapped


class ExprEvaluator(ExprVisitor):
    __binary_switch: Dict[exprs.BinaryOperatorType, BinaryOpHandler] = {
        exprs.BinaryOperatorType.PLUS: lambda self, node, left, right: self.__handle_plus(node, left, right),
        exprs.BinaryOperatorType.MINUS: number_binary_op(lambda self, _, left, right: left - right),
        exprs.BinaryOperatorType.MULTIPLY: number_binary_op(lambda self, _, left, right: left * right),
        exprs.BinaryOperatorType.DIVIDE: number_binary_op(lambda self, _, left, right: left / right),
        exprs.BinaryOperatorType.EQUAL: number_binary_op(lambda self, _, left, right: is_equal(left, right)),
        exprs.BinaryOperatorType.NOT_EQUAL: number_binary_op(lambda self, _, left, right: not is_equal(left, right)),
        exprs.BinaryOperatorType.GREATER: number_binary_op(lambda self, _, left, right: left >= right),
        exprs.BinaryOperatorType.GREATER_EQUAL: number_binary_op(lambda self, _, left, right: left >= right),
        exprs.BinaryOperatorType.LESS: number_binary_op(lambda self, _, left, right: left < right),
        exprs.BinaryOperatorType.LESS_EQUAL: number_binary_op(lambda self, _, left, right: left <= right),
    }
    __unary_switch: Dict[exprs.UnaryOperatorType, UnaryOpHandler] = {
        exprs.UnaryOperatorType.NEGATE: number_unary_op(lambda self, _, value: -value),
        exprs.UnaryOperatorType.NOT: lambda self, _, value: not is_truthy(value),
    }

    def evaluate(self, expression: Expr):
        return expression.accept(self)

    def visit_binary(self, node: exprs.Binary):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        handler = self.__binary_switch.get(node.operator.type)
        if handler is None:
            raise Exception('Handler for {} was None'.format(node.operator))

        return handler(self, node, left, right)

    def visit_grouping(self, node: exprs.Grouping):
        return self.evaluate(node.expression)

    def visit_literal(self, node: exprs.Literal):
        return node.value

    def visit_unary(self, node: exprs.Unary):
        value = self.evaluate(node.expression)

        handler = self.__unary_switch.get(node.operator.type)
        if handler is None:
            raise Exception('Handler for {} was None'.format(node.operator))

        return handler(self, node, value)

    def __handle_plus(self, node: exprs.Binary, left: Any, right: Any) -> Any:
        if isinstance(left, str) or isinstance(right, str):
            return '{}{}'.format(to_string(left), to_string(right))

        return left + right

    def assert_numeric(self, span: SourceSpan, value: Any):
        # TODO track where value is from/used in the source
        if isinstance(value, int) or isinstance(value, float):
            return

        raise RuntimeException(span, "Expected a number")


class RuntimeException(Exception):
    def __init__(self, span: SourceSpan, message: str) -> None:
        self.__span = span
        self.__message = message

    def __str__(self) -> str:
        return "{} at {}".format(self.__message, self.__span)

