from enum import Enum, auto
from typing import Union, Optional


class TokenType(Enum):
    # single char
    MINUS = auto()
    PLUS = auto()
    SLASH = auto()
    STAR = auto()

    # one/two char
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # keywords
    AND = auto()
    FALSE = auto()
    OR = auto()
    TRUE = auto()


class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: Optional[Union[str, float, bool]], line: int, offset: int):
        self._type = type
        self._lexeme = lexeme
        self._literal = literal
        self._line = line
        self._offset = offset

    @property
    def type(self):
        return self._type

    @property
    def lexeme(self):
        return self._lexeme

    @property
    def literal(self):
        return self._literal

    @property
    def line(self):
        return self._line

    @property
    def offset(self):
        return self._offset

    def __str__(self) -> str:
        return '{} {} {}'.format(self.type, self.lexeme, self.literal)


