from parsing.source import highlight, SourceSpan, Position


class TestSource:
    def test_highlight_single_line(self):
        source = 'hello world'
        span = SourceSpan(source, Position.initial(), Position(len(source) - 1, 1, len(source) + 1))

        result = highlight(span)

        assert result == '1. hello world\n   ~~~~~~~~~~~'

    def test_highlight_partial_single_line(self):
        source = 'hello world'
        span = SourceSpan(source, Position(0, 1, 4), Position(len(source) - 3, 1, len(source) - 1))

        result = highlight(span)

        assert result == '1. hello world\n      ~~~~~~'

    def test_highlight_two_lines(self):
        source = 'hello\nworld'
        span = SourceSpan(source, Position.initial(), Position(len(source) - 1, 2, 6))

        result = highlight(span)

        assert result == '1. hello\n   ~~~~~\n2. world\n   ~~~~~'

    def test_highlight_partial_two_lines(self):
        source = 'hello\nworld'
        span = SourceSpan(source, Position(0, 1, 3), Position(len(source) - 3, 2, 4))

        result = highlight(span)

        assert result == '1. hello\n     ~~~\n2. world\n   ~~~'

    def test_highlight_partial_three_lines(self):
        source = 'hello\ngreen\nworld'
        span = SourceSpan(source, Position(0, 1, 3), Position(len(source) - 3, 3, 4))

        result = highlight(span)

        assert result == '1. hello\n     ~~~\n2. green\n   ~~~~~\n3. world\n   ~~~'
