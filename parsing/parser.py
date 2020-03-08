from typing import List

import parsing.expr as exprs
from parsing.expr import Expr
from parsing.source import SourceSpan
from parsing.token import Token, TokenType


token_type_to_binary_operator = {
    TokenType.PLUS: exprs.BinaryOperatorType.PLUS,
    TokenType.MINUS: exprs.BinaryOperatorType.MINUS,
    TokenType.SLASH: exprs.BinaryOperatorType.DIVIDE,
    TokenType.STAR: exprs.BinaryOperatorType.MULTIPLY,
    TokenType.BANG_EQUAL: exprs.BinaryOperatorType.NOT_EQUAL,
    TokenType.EQUAL_EQUAL: exprs.BinaryOperatorType.EQUAL,
    TokenType.GREATER: exprs.BinaryOperatorType.GREATER,
    TokenType.GREATER_EQUAL: exprs.BinaryOperatorType.GREATER_EQUAL,
    TokenType.LESS: exprs.BinaryOperatorType.LESS,
    TokenType.LESS_EQUAL: exprs.BinaryOperatorType.LESS_EQUAL,
}
token_type_to_unary_operator = {
    TokenType.BANG: exprs.UnaryOperatorType.NOT,
    TokenType.MINUS: exprs.UnaryOperatorType.NEGATE,
}


def token_to_binary_operator(token: Token) -> exprs.BinaryOperator:
    type = token_type_to_binary_operator[token.type]
    return exprs.BinaryOperator(type, token.span)


def token_to_unary_operator(token: Token) -> exprs.UnaryOperator:
    type = token_type_to_unary_operator[token.type]
    return exprs.UnaryOperator(type, token.span)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.__tokens = tokens
        self.__current = 0

    # expressions
    def expression(self) -> Expr:
        return self.__equality()

    def __equality(self) -> Expr:
        expr = self.__comparison()

        while self.__match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = token_to_binary_operator(self.__previous())
            right = self.__comparison()
            new_expr = exprs.Binary(expr, operator, right)
            new_expr.span = SourceSpan.from_spans(expr.span, right.span)
            expr = new_expr

        return expr

    def __comparison(self) -> Expr:
        expr = self.__addition()

        while self.__match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = token_to_binary_operator(self.__previous())
            right = self.__addition()
            new_expr = exprs.Binary(expr, operator, right)
            new_expr.span = SourceSpan.from_spans(expr.span, right.span)
            expr = new_expr

        return expr

    def __addition(self) -> Expr:
        expr = self.__multiplication()

        while self.__match(TokenType.PLUS, TokenType.MINUS):
            operator = token_to_binary_operator(self.__previous())
            right = self.__multiplication()
            new_expr = exprs.Binary(expr, operator, right)
            new_expr.span = SourceSpan.from_spans(expr.span, right.span)
            expr = new_expr

        return expr

    def __multiplication(self) -> Expr:
        expr = self.__unary()

        while self.__match(TokenType.SLASH, TokenType.STAR):
            operator = token_to_binary_operator(self.__previous())
            right = self.__unary()
            new_expr = exprs.Binary(expr, operator, right)
            new_expr.span = SourceSpan.from_spans(expr.span, right.span)
            expr = new_expr

        return expr

    def __unary(self) -> Expr:
        if self.__match(TokenType.BANG, TokenType.MINUS):
            operator = token_to_unary_operator(self.__previous())
            inner_expr = self.__unary()
            expr = exprs.Unary(operator, inner_expr)
            expr.span = SourceSpan.from_spans(operator.span, inner_expr.span)
            return expr

        return self.__primary()

    def __primary(self) -> Expr:
        def literal(value) -> Expr:
            expr = exprs.Literal(value)
            expr.span = self.__previous().span
            return expr

        if self.__match(TokenType.FALSE):
            return literal(False)
        if self.__match(TokenType.TRUE):
            return literal(True)

        if self.__match(TokenType.NUMBER, TokenType.STRING):
            return literal(self.__previous().literal)

        if self.__match(TokenType.LEFT_PAREN):
            start = self.__previous()
            expr = exprs.Grouping(self.expression())
            end = self.__consume(TokenType.RIGHT_PAREN, 'Expected \')\' after expression')
            expr.span = SourceSpan.from_spans(start.span, end.span)
            return expr

        raise ParserException(self.__peek(), 'Expected expression')

    # helpers
    def __match(self, *args: TokenType) -> bool:
        for token_type in args:
            if self.__check(token_type):
                self.__advance()
                return True

        return False

    def __check(self, token_type: TokenType) -> bool:
        if self.is_at_end:
            return False

        return self.__peek().type == token_type

    def __consume(self, token_type: TokenType, error_message: str) -> Token:
        if self.__check(token_type):
            return self.__advance()

        raise UnexpectedTokenError(token_type, self.__peek(), error_message)

    def __advance(self) -> Token:
        if not self.is_at_end:
            self.__current += 1

        return self.__previous()

    def __peek(self) -> Token:
        return self.__tokens[self.__current]

    def __previous(self) -> Token:
        return self.__tokens[self.__current - 1]

    @property
    def is_at_end(self) -> bool:
        return self.__current >= len(self.__tokens)


class ParserException(Exception):
    def __init__(self, token: Token, message: str) -> None:
        self.__token = token
        self.__message = message

    @property
    def token(self) -> Token:
        return self.__token

    def __str__(self) -> str:
        return '{} ({} at {})'.format(self.__message, self.__token.type, self.token.span)


class UnexpectedTokenError(ParserException):
    def __init__(self, expected_type: TokenType, token: Token, message: str) -> None:
        super().__init__(token, message)
        self.__expected_type = expected_type

    def __str__(self) -> str:
        return '{} (expected {} but got {} at {})'.format(self.__message, self.__expected_type, self.token.type, self.token.span)
