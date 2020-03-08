from typing import List

import pytest

from parsing.lexer import get_all_tokens, Lexer, LexerException
from parsing.token import TokenType, Token


def tokenize(input: str) -> List[Token]:
    lexer = Lexer(input)
    tokens = get_all_tokens(lexer)
    return tokens[:-1]  # remove the EOF token


class TestLexer:
    def test_single_char_tokens(self):
        tokens = tokenize('()+-/*')

        assert list(map(lambda x: x.type, tokens)) == [
            TokenType.LEFT_PAREN,
            TokenType.RIGHT_PAREN,
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.SLASH,
            TokenType.STAR,
        ]

    def test_whitespace_is_ignored(self):
        tokens = tokenize('+ +')

        assert list(map(lambda x: x.type, tokens)) == [
            TokenType.PLUS,
            TokenType.PLUS,
        ]

    def test_comment_is_ignored(self):
        tokens = tokenize('+ //hello this is a comment\n+')

        assert list(map(lambda x: x.type, tokens)) == [
            TokenType.PLUS,
            TokenType.PLUS,
        ]

    def test_multichar_tokens(self):
        tokens = tokenize('! != = == < <= > >=')

        assert list(map(lambda x: x.type, tokens)) == [
            TokenType.BANG,
            TokenType.BANG_EQUAL,
            TokenType.EQUAL,
            TokenType.EQUAL_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ]

    def test_string_tokens(self):
        tokens = tokenize('"Hello\nWorld\"')
        token = tokens[0]

        assert TokenType.STRING == token.type
        assert "Hello\nWorld" == token.literal

    def test_number_tokens(self):
        tokens = tokenize('1234 12.34')

        assert all(map(lambda x: x.type == TokenType.NUMBER, tokens))
        assert list(map(lambda x: x.literal, tokens)) == [
            1234,
            12.34,
        ]

    def test_identifier_tokens(self):
        tokens = tokenize('a abc')

        assert all(map(lambda x: x.type == TokenType.IDENTIFIER, tokens))
        assert list(map(lambda x: x.span.text(), tokens)) == [
            'a',
            'abc',
        ]

    def test_keyword_tokens(self):
        tokens = tokenize('and or')

        assert list(map(lambda x: x.type, tokens)) == [
            TokenType.AND,
            TokenType.OR,
        ]

    def test_invalid_char_should_throw(self):
        lexer = Lexer('@')

        with pytest.raises(LexerException):
            lexer.next()

    def test_unterminated_string_should_throw(self):
        lexer = Lexer('"Hello\nWorld')

        with pytest.raises(LexerException):
            lexer.next()
