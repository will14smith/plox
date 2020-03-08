from typing import Callable, Dict, List, Optional, Union

from parsing.source import SourcePosition, SourceSpan
from parsing.token import Token, TokenType


def is_whitespace(c: str) -> bool:
    return c == ' ' or c == '\r' or c == '\t'


def is_newline(c: str) -> bool:
    return c == '\n'


def is_digit(c: str) -> bool:
    return '0' <= c <= '9'


def is_alpha(c: str) -> bool:
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_'


def is_alphanumeric(c: str) -> bool:
    return is_alpha(c) or is_digit(c)


def get_all_tokens(lexer: 'Lexer') -> List[Token]:
    tokens = []

    while 1:
        token = lexer.next()
        if token is None:
            break
        tokens.append(token)

    return tokens


class Lexer:
    __token_start_switch: Dict[str, Callable[['Lexer'], Token]] = {
        '(': lambda self: self.__create_token(TokenType.LEFT_PAREN),
        ')': lambda self: self.__create_token(TokenType.RIGHT_PAREN),
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

    __keywords: Dict[str, TokenType] = {
        'and': TokenType.AND,
        'false': TokenType.FALSE,
        'or': TokenType.OR,
        'true': TokenType.TRUE,
    }

    def __init__(self, input: str):
        self.__current = SourcePosition.initial(input)
        self.__start = self.__current

    def next(self) -> Optional[Token]:
        if self.is_at_end:
            return None

        self.__skip_whitespace()
        self.__start = self.__current
        return self.__scan_token()

    def __scan_token(self):
        c = self.__advance()
        handler = self.__token_start_switch.get(c)
        if handler is not None:
            return handler(self)

        if is_digit(c):
            return self.__handle_number()

        if is_alpha(c):
            return self.__handle_identifier()

        raise self.__error(InvalidLexerCharException, 'Invalid char \'{}\''.format(c))

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

    def __handle_number(self):
        while is_digit(self.__peek()):
            self.__advance()

        if self.__peek() == '.' and is_digit(self.__peek(1)):
            # consume the decimal point
            self.__advance()

            while is_digit(self.__peek()):
                self.__advance()

        literal_span = SourceSpan.from_positions(self.__start, self.__current)
        literal = float(literal_span.text())
        return self.__create_token(TokenType.NUMBER, literal)

    def __handle_identifier(self):
        while is_alphanumeric(self.__peek()):
            self.__advance()

        identifier_span = SourceSpan.from_positions(self.__start, self.__current)
        keyword = self.__keywords.get(identifier_span.text())
        if keyword is not None:
            return self.__create_token(keyword)

        return self.__create_token(TokenType.IDENTIFIER)

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

    def __peek(self, offset: int = 0) -> str:
        if self.__current.position.offset + offset >= len(self.__current.source):
            return '\0'
        return self.__current.source[self.__current.position.offset + offset]

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
