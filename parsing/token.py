from enum import Enum, auto
from typing import Union, Optional

from parsing.source import SourceSpan


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
    def __init__(self, type: TokenType, span: SourceSpan, literal: Optional[Union[str, float, bool]]):
        self.__type = type
        self.__span = span
        self.__literal = literal

    @property
    def type(self):
        return self.__type

    @property
    def span(self):
        return self.__span

    @property
    def literal(self):
        return self.__literal

    def __str__(self) -> str:
        return '{} {} {}'.format(self.type, self.span.start, self.literal)


