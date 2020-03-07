from typing import Callable, Dict, Optional

from parsing.token import Token, TokenType


def is_whitespace(c: str) -> bool:
    return c == ' ' or c == '\r' or c == '\t'


def is_newline(c: str) -> bool:
    return c == '\n'


class Lexer:
    __token_start_switch: Dict[str, Callable[['Lexer'], Token]] = {
        '-': lambda self: self.__create_token(TokenType.MINUS),
        '+': lambda self: self.__create_token(TokenType.PLUS),
        '/': lambda self: self.__handle_slash(),
        '*': lambda self: self.__create_token(TokenType.STAR),

        '!': lambda self: self.__create_token(TokenType.BANG_EQUAL if self.__advance_if('=') else TokenType.BANG),
        '=': lambda self: self.__create_token(TokenType.EQUAL_EQUAL if self.__advance_if('=') else TokenType.EQUAL),
        '<': lambda self: self.__create_token(TokenType.LESS_EQUAL if self.__advance_if('=') else TokenType.LESS),
        '>': lambda self: self.__create_token(TokenType.GREATER_EQUAL if self.__advance_if('=') else TokenType.GREATER),
    }

    def __init__(self, input: str):
        self.__input = input
        self.__start = 0
        self.__offset = 0
        self.__line = 1
        self.__line_offset_start = 0

    def next(self) -> Optional[Token]:
        if self.is_at_end:
            return None

        self.__start = self.__offset
        return self.__scan_token()

    def __scan_token(self):
        self.__skip_whitespace()

        c = self.__advance()
        handler = self.__token_start_switch.get(c)
        if handler is None:
            raise self.__error(InvalidLexerCharException, 'Invalid char \'{}\''.format(c))

        return handler(self)

    def __handle_slash(self):
        if not self.__advance_if('/'):
            return self.__create_token(TokenType.SLASH)

        while self.__peek() != '\n' and not self.is_at_end:
            self.__advance()

        # comments are discarded so return the next token
        return self.next()

    def __skip_whitespace(self):
        while is_whitespace(self.current) or is_newline(self.current):
            self.__offset += 1
            if is_newline(self.current):
                self.__line += 1
                self.__line_offset_start += self.__offset

    def __advance(self) -> str:
        self.__offset += 1
        return self.__input[self.__offset - 1]

    def __advance_if(self, expected: str) -> bool:
        if self.is_at_end:
            return False
        if self.__input[self.__offset] != expected:
            return False

        self.__offset += 1
        return True

    def __peek(self) -> str:
        if self.is_at_end:
            return '\0'
        return self.__input[self.__offset]

    def __create_token(self, token_type: TokenType) -> Token:
        return Token(token_type, self.__input[self.__start:self.__offset], None, 1, self.__start)

    def __error(self, exception_cls, message):
        return exception_cls(message, self.__line, self.__offset - self.__line_offset_start)

    @property
    def current(self):
        return self.__input[self.__offset]

    @property
    def is_at_end(self) -> bool:
        return self.__offset >= len(self.__input)


class LexerException(Exception):
    def __init__(self, message, line, line_offset):
        self.message = message
        self.line = line
        self.line_offset = line_offset

    def __str__(self) -> str:
        return '{} at line {}:{}'.format(self.message, self.line, self.line_offset)


class InvalidLexerCharException(LexerException):
    def __init__(self, message, line, line_offset):
        super().__init__(message, line, line_offset)
