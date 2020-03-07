import unittest

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


class LexerTests(unittest.TestCase):
    def test_single_char_tokens(self):
        lexer = Lexer('+-/*')
        tokens = lex_all(lexer)

        self.assertEqual([
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.SLASH,
            TokenType.STAR,
        ], list(map(lambda x: x.type, tokens)))

    def test_invalid_char_should_throw(self):
        lexer = Lexer('@')

        with self.assertRaises(LexerException):
            lexer.next()

    def assertType(self, expected: TokenType, actual_token: Token):
        self.assertEqual(expected, actual_token.type)


if __name__ == '__main__':
    unittest.main()
