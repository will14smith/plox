from typing import Any, Callable, Dict

import parsing.expr as exprs
from parsing.expr import Expr, ExprVisitor

BinaryOpHandler = Callable[['ExpressionEvaluator', Any, Any], Any]
UnaryOpHandler = Callable[['ExpressionEvaluator', Any], Any]


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
    def wrapped(self: 'ExprEvaluator', left: Any, right: Any):
        self.assert_numeric(left)
        self.assert_numeric(right)

        return handler(self, left, right)

    return wrapped


def number_unary_op(handler: UnaryOpHandler) -> UnaryOpHandler:
    def wrapped(self: 'ExprEvaluator', value: Any):
        self.assert_numeric(value)

        return handler(self, value)

    return wrapped


class ExprEvaluator(ExprVisitor):
    __binary_switch: Dict[exprs.BinaryOperator, BinaryOpHandler] = {
        exprs.BinaryOperator.PLUS: lambda self, left, right: self.__handle_plus(left, right),
        exprs.BinaryOperator.MINUS: number_binary_op(lambda self, left, right: left - right),
        exprs.BinaryOperator.MULTIPLY: number_binary_op(lambda self, left, right: left * right),
        exprs.BinaryOperator.DIVIDE: number_binary_op(lambda self, left, right: left / right),
        exprs.BinaryOperator.EQUAL: number_binary_op(lambda self, left, right: is_equal(left, right)),
        exprs.BinaryOperator.NOT_EQUAL: number_binary_op(lambda self, left, right: not is_equal(left, right)),
        exprs.BinaryOperator.GREATER: number_binary_op(lambda self, left, right: left >= right),
        exprs.BinaryOperator.GREATER_EQUAL: number_binary_op(lambda self, left, right: left >= right),
        exprs.BinaryOperator.LESS: number_binary_op(lambda self, left, right: left < right),
        exprs.BinaryOperator.LESS_EQUAL: number_binary_op(lambda self, left, right: left <= right),
    }
    __unary_switch: Dict[exprs.UnaryOperator, Callable[['ExpressionEvaluator', Any], Any]] = {
        exprs.UnaryOperator.NEGATE: number_unary_op(lambda self, value: -value),
        exprs.UnaryOperator.NOT: lambda self, value: not is_truthy(value),
    }

    def evaluate(self, expression: Expr):
        return expression.accept(self)

    def visit_binary(self, node: exprs.Binary):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        handler = self.__binary_switch.get(node.operator)
        if handler is None:
            raise Exception('Handler for {} was None'.format(node.operator))

        return handler(self, left, right)

    def visit_grouping(self, node: exprs.Grouping):
        return self.evaluate(node.expression)

    def visit_literal(self, node: exprs.Literal):
        return node.value

    def visit_unary(self, node: exprs.Unary):
        value = self.evaluate(node.expression)

        handler = self.__unary_switch.get(node.operator)
        if handler is None:
            raise Exception('Handler for {} was None'.format(node.operator))

        return handler(self, value)

    def __handle_plus(self, left: Any, right: Any) -> Any:
        if isinstance(left, str) or isinstance(right, str):
            return '{}{}'.format(to_string(left), to_string(right))

        return left + right

    def assert_numeric(self, value: Any):
        # TODO track where value is from/used in the source
        if isinstance(value, int) or isinstance(value, float):
            return

        raise RuntimeException("Expected a number")


class RuntimeException(Exception):
    pass
