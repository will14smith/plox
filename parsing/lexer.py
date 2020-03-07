from typing import Callable, Dict, Optional

from parsing.token import Token, TokenType


class Lexer:
    __token_start_switch: Dict[str, Callable[['Lexer'], Token]] = {
        '-': lambda self: self.__create_token(TokenType.MINUS),
        '+': lambda self: self.__create_token(TokenType.PLUS),
        '/': lambda self: self.__create_token(TokenType.SLASH),
        '*': lambda self: self.__create_token(TokenType.STAR),
    }

    def __init__(self, input: str):
        self.__input = input
        self.__start = 0
        self.__offset = 0

    def next(self) -> Optional[Token]:
        if self.is_at_end:
            return None

        self.__start = self.__offset
        return self.__scan_token()

    def __scan_token(self):
        c = self.__advance()
        handler = self.__token_start_switch.get(c)
        if handler is None:
            raise self.__error(InvalidLexerCharException, 'Invalid char \'{}\''.format(c))

        return handler(self)

    def __advance(self) -> str:
        self.__offset += 1
        return self.__input[self.__offset - 1]

    def __create_token(self, token_type: TokenType) -> Token:
        return Token(token_type, self.__input[self.__start:self.__offset], None, 1, self.__start)

    def __error(self, exception_cls, message):
        return exception_cls(message, self.__offset)

    @property
    def is_at_end(self) -> bool:
        return self.__offset >= len(self.__input)


class LexerException(Exception):
    def __init__(self, message, offset):
        self.message = message
        self.offset = offset

    def __str__(self) -> str:
        return '{} at offset {}'.format(self.message, self.offset)


class InvalidLexerCharException(LexerException):
    def __init__(self, message, offset):
        super().__init__(message, offset)
