from typing import Any

import pytest

from evaluation.expr import RuntimeException
from parsing.expr import Expr


def parse_expr(input: str) -> Expr:
    from parsing.lexer import get_all_tokens, Lexer
    from parsing.parser import Parser

    lexer = Lexer(input)
    tokens = get_all_tokens(lexer)

    parser = Parser(tokens)
    return parser.expression()


def eval_expr(input: str) -> Any:
    from evaluation.expr import ExprEvaluator

    expr = parse_expr(input)
    eval = ExprEvaluator()

    return eval.evaluate(expr)


class TestExprEvaluator:
    def test_number(self):
        result = eval_expr('123')

        assert result == 123

    def test_grouping(self):
        result = eval_expr('(123)')

        assert result == 123

    def test_unary(self):
        result = eval_expr('-123')

        assert result == -123

    def test_binary(self):
        result = eval_expr('1 + 2')

        assert result == 3

    def test_minus_string_should_throw(self):
        with pytest.raises(RuntimeException):
            eval_expr('1 - "a"')

    def test_string_addition(self):
        result = eval_expr('"a" + "b"')

        assert result == 'ab'

    def test_string_number_addition(self):
        result = eval_expr('"a" + 1')

        assert result == 'a1'
