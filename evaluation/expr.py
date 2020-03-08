from typing import Any, Callable, Dict

import parsing.expr as exprs
from parsing.expr import Expr, ExprVisitor


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


class ExprEvaluator(ExprVisitor):
    __binary_switch: Dict[exprs.BinaryOperator, Callable[['ExpressionEvaluator', Any, Any], Any]] = {
        exprs.BinaryOperator.PLUS: lambda self, left, right: self.__handle_plus(left, right),
        exprs.BinaryOperator.MINUS: lambda self, left, right: left - right,
        exprs.BinaryOperator.MULTIPLY: lambda self, left, right: left * right,
        exprs.BinaryOperator.DIVIDE: lambda self, left, right: left / right,
        exprs.BinaryOperator.EQUAL: lambda self, left, right: is_equal(left, right),
        exprs.BinaryOperator.NOT_EQUAL: lambda self, left, right: not is_equal(left, right),
        exprs.BinaryOperator.GREATER: lambda self, left, right: left >= right,
        exprs.BinaryOperator.GREATER_EQUAL: lambda self, left, right: left >= right,
        exprs.BinaryOperator.LESS: lambda self, left, right: left < right,
        exprs.BinaryOperator.LESS_EQUAL: lambda self, left, right: left <= right,
    }
    __unary_switch: Dict[exprs.UnaryOperator, Callable[['ExpressionEvaluator', Any], Any]] = {
        exprs.UnaryOperator.NEGATE: lambda self, value: -value,
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
            return '{}{}'.format(left, right)

        return left + right
