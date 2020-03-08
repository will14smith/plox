from typing import List

import parsing.expr as exprs
from parsing.expr import Expr
from parsing.token import Token, TokenType


token_type_to_binary_operator = {
    TokenType.PLUS: exprs.BinaryOperator.PLUS,
    TokenType.MINUS: exprs.BinaryOperator.MINUS,
    TokenType.SLASH: exprs.BinaryOperator.DIVIDE,
    TokenType.STAR: exprs.BinaryOperator.MULTIPLY,
    TokenType.BANG_EQUAL: exprs.BinaryOperator.NOT_EQUAL,
    TokenType.EQUAL_EQUAL: exprs.BinaryOperator.EQUAL,
    TokenType.GREATER: exprs.BinaryOperator.GREATER,
    TokenType.GREATER_EQUAL: exprs.BinaryOperator.GREATER_EQUAL,
    TokenType.LESS: exprs.BinaryOperator.LESS,
    TokenType.LESS_EQUAL: exprs.BinaryOperator.LESS_EQUAL,
}
token_type_to_unary_operator = {
    TokenType.BANG: exprs.UnaryOperator.NOT,
    TokenType.MINUS: exprs.UnaryOperator.NEGATE,
}


def token_to_binary_operator(token: Token) -> exprs.BinaryOperator:
    # TODO we probably want to track the original token for error reporting
    return token_type_to_binary_operator[token.type]


def token_to_unary_operator(token: Token) -> exprs.UnaryOperator:
    # TODO we probably want to track the original token for error reporting
    return token_type_to_unary_operator[token.type]


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
            expr = exprs.Binary(expr, operator, right)

        return expr

    def __comparison(self) -> Expr:
        expr = self.__addition()

        while self.__match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = token_to_binary_operator(self.__previous())
            right = self.__addition()
            expr = exprs.Binary(expr, operator, right)

        return expr

    def __addition(self) -> Expr:
        expr = self.__multiplication()

        while self.__match(TokenType.PLUS, TokenType.MINUS):
            operator = token_to_binary_operator(self.__previous())
            right = self.__multiplication()
            expr = exprs.Binary(expr, operator, right)

        return expr

    def __multiplication(self) -> Expr:
        expr = self.__unary()

        while self.__match(TokenType.SLASH, TokenType.STAR):
            operator = token_to_binary_operator(self.__previous())
            right = self.__unary()
            expr = exprs.Binary(expr, operator, right)

        return expr

    def __unary(self) -> Expr:
        if self.__match(TokenType.BANG, TokenType.MINUS):
            operator = token_to_unary_operator(self.__previous())
            expr = self.__unary()
            return exprs.Unary(operator, expr)

        return self.__primary()

    def __primary(self) -> Expr:
        if self.__match(TokenType.FALSE):
            return exprs.Literal(False)
        if self.__match(TokenType.TRUE):
            return exprs.Literal(True)

        if self.__match(TokenType.NUMBER, TokenType.STRING):
            return exprs.Literal(self.__previous().literal)

        if self.__match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.__consume(TokenType.RIGHT_PAREN, 'Expected \')\' after expression')
            return exprs.Grouping(expr)

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
