from typing import cast

import parsing.expr as exprs
from parsing.expr import Expr


def parse_expr(input: str) -> Expr:
    from parsing.lexer import get_all_tokens, Lexer
    from parsing.parser import Parser

    lexer = Lexer(input)
    tokens = get_all_tokens(lexer)

    parser = Parser(tokens)
    return parser.expression()


def assert_number(expr: Expr, value: float):
    __tracebackhide__ = True
    assert isinstance(expr, exprs.Literal)
    assert expr.value == value


def assert_binary(expr: Expr, operator: exprs.BinaryOperator) -> exprs.Binary:
    __tracebackhide__ = True
    assert isinstance(expr, exprs.Binary)
    assert expr.operator == operator
    return expr


class TestParser:
    def test_numbers(self):
        expr = parse_expr('123')

        assert_number(expr, 123)

    def test_strings(self):
        expr = parse_expr('"abc"')

        assert isinstance(expr, exprs.Literal)
        assert expr.value == 'abc'

    def test_boolean(self):
        expr = parse_expr('false')

        assert isinstance(expr, exprs.Literal)
        assert not expr.value

    def test_grouping(self):
        expr = parse_expr('(123)')

        assert isinstance(expr, exprs.Grouping)
        assert_number(expr.expression, 123)

    def test_unary(self):
        expr = parse_expr('-123')

        assert isinstance(expr, exprs.Unary)
        assert expr.operator == exprs.UnaryOperator.NEGATE
        assert_number(expr.expression, 123)

    def test_binary(self):
        expr = parse_expr('123 * 456')

        expr = assert_binary(expr, exprs.BinaryOperator.MULTIPLY)
        assert_number(expr.left, 123)
        assert_number(expr.right, 456)

    def test_precedence(self):
        expr = parse_expr('123 + 456 * 789')

        expr = assert_binary(expr, exprs.BinaryOperator.PLUS)
        assert_number(expr.left, 123)
        expr = assert_binary(expr.right, exprs.BinaryOperator.MULTIPLY)
        assert_number(expr.left, 456)
        assert_number(expr.right, 789)
