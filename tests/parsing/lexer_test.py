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

        assert [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.SLASH,
            TokenType.STAR,
        ] == list(map(lambda x: x.type, tokens))

    def test_whitespace_is_ignored(self):
        lexer = Lexer('+ +')
        tokens = lex_all(lexer)

        assert [
           TokenType.PLUS,
           TokenType.PLUS,
        ] == list(map(lambda x: x.type, tokens))

    def test_comment_is_ignored(self):
        lexer = Lexer('+ //hello this is a comment\n+')
        tokens = lex_all(lexer)

        assert [
           TokenType.PLUS,
           TokenType.PLUS,
        ] == list(map(lambda x: x.type, tokens))

    def test_multichar_tokens(self):
        lexer = Lexer('! != = == < <= > >=')
        tokens = lex_all(lexer)

        assert [
            TokenType.BANG,
            TokenType.BANG_EQUAL,
            TokenType.EQUAL,
            TokenType.EQUAL_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
        ] == list(map(lambda x: x.type, tokens))

    def test_string_tokens(self):
        lexer = Lexer('"Hello\nWorld\"')
        token = lexer.next()

        assert TokenType.STRING == token.type
        assert "Hello\nWorld" == token.literal

    def test_invalid_char_should_throw(self):
        lexer = Lexer('@')

        with pytest.raises(LexerException):
            lexer.next()

    def test_unterminated_string_should_throw(self):
        lexer = Lexer('"Hello\nWorld')

        with pytest.raises(LexerException):
            lexer.next()
