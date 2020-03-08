from typing import List

from evaluation.expr import ExprEvaluator, RuntimeException
from parsing.expr import Expr
from parsing.lexer import get_all_tokens, Lexer, LexerException
from parsing.parser import Parser, ParserException
from parsing.token import Token


def tokenize(input: str) -> List[Token]:
    lexer = Lexer(input)
    return get_all_tokens(lexer)


def parse(tokens: List[Token]) -> Expr:
    parser = Parser(tokens)
    return parser.expression()


def main():
    eval = ExprEvaluator()

    while True:
        command = input("> ")
        try:
            tokens = tokenize(command)
            expr = parse(tokens)
            result = eval.evaluate(expr)
            print(result)
        except LexerException as e:
            print(e)
        except ParserException as e:
            print(e)
        except RuntimeException as e:
            print(e)


if __name__ == '__main__':
    main()
