import pytest

from typing import List
from parsing.lexer import Lexer, LexerException
from parsing.token import Token, TokenType


def lex_all(lexer: Lexer) -> List[Token]:
    tokens = []

    while 1:
        token = lexer.next()
        if token is None:
            break
        tokens.append(token)

    return tokens


class TestLexer:
    def test_single_char_tokens(self):
        lexer = Lexer('+-/*')
        tokens = lex_all(lexer)

        assert list(map(lambda x: x.type, tokens)) == [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.SLASH,
            TokenType.STAR,
        ]

    def test_whitespace_is_ignored(self):
        lexer = Lexer('+ +')
        tokens = lex_all(lexer)

        assert list(map(lambda x: x.type, tokens)) == [
           TokenType.PLUS,
           TokenType.PLUS,
        ]

    def test_comment_is_ignored(self):
        lexer = Lexer('+ //hello this is a comment\n+')
        tokens = lex_all(lexer)

        assert list(map(lambda x: x.type, tokens)) == [
           TokenType.PLUS,
           TokenType.PLUS,
        ]

    def test_multichar_tokens(self):
        lexer = Lexer('! != = == < <= > >=')
        tokens = lex_all(lexer)

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
        lexer = Lexer('"Hello\nWorld\"')
        token = lexer.next()

        assert TokenType.STRING == token.type
        assert "Hello\nWorld" == token.literal

    def test_number_tokens(self):
        lexer = Lexer('1234 12.34')
        tokens = lex_all(lexer)

        assert all(map(lambda x: x.type == TokenType.NUMBER, tokens))
        assert list(map(lambda x: x.literal, tokens)) == [
           1234,
           12.34,
        ]

    def test_identifier_tokens(self):
        lexer = Lexer('a abc')
        tokens = lex_all(lexer)

        assert all(map(lambda x: x.type == TokenType.IDENTIFIER, tokens))
        assert list(map(lambda x: x.span.text(), tokens)) == [
            'a',
            'abc',
        ]

    def test_keyword_tokens(self):
        lexer = Lexer('and or')
        tokens = lex_all(lexer)

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
