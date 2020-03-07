from typing import Callable, Dict, Optional, Union

from parsing.source import SourcePosition, SourceSpan
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

        '"': lambda self: self.__handle_string(),
    }

    def __init__(self, input: str):
        self.__current = SourcePosition.initial(input)
        self.__start = self.__current

    def next(self) -> Optional[Token]:
        if self.is_at_end:
            return None

        self.__start = self.__current
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

    def __handle_string(self):
        literal_start = self.__current

        while self.__peek() != '"' and not self.is_at_end:
            self.__advance()

        if self.is_at_end:
            raise self.__error(UnterminatedStringException, 'Unterminated string')

        literal_end = self.__current

        # consume the closing quote
        self.__advance()

        # trim the quotes
        literal_span = SourceSpan.from_positions(literal_start, literal_end)
        return self.__create_token(TokenType.STRING, literal_span.text())

    def __skip_whitespace(self):
        while is_whitespace(self.current) or is_newline(self.current):
            self.__advance()

    def __advance(self) -> str:
        c = self.current
        if is_newline(c):
            self.__current = self.__current.new_line()
        else:
            self.__current = self.__current.next()
        return c

    def __advance_if(self, expected: str) -> bool:
        if self.is_at_end:
            return False
        if self.current != expected:
            return False

        self.__advance()
        return True

    def __peek(self) -> str:
        if self.is_at_end:
            return '\0'
        return self.current

    def __create_token(self, token_type: TokenType, value: Optional[Union[str, float, bool]] = None) -> Token:
        span = SourceSpan.from_positions(self.__start, self.__current)
        return Token(token_type, span, value)

    def __error(self, exception_cls, message):
        span = SourceSpan.from_positions(self.__start, self.__current)
        return exception_cls(message, span)

    @property
    def current(self):
        return self.__current.source[self.__current.position.offset]

    @property
    def is_at_end(self) -> bool:
        return self.__current.is_at_end


class LexerException(Exception):
    def __init__(self, message: str, span: SourceSpan):
        self.message = message
        self.span = span

    def __str__(self) -> str:
        return '{} at line {} - {}'.format(self.message, self.span.start, self.span.end)


class InvalidLexerCharException(LexerException):
    pass


class UnterminatedStringException(LexerException):
    pass
