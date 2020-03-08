class Position:
    def __init__(self, offset: int, line: int, line_offset: int) -> None:
        self.__offset = offset
        self.__line = line
        self.__line_offset = line_offset

    @staticmethod
    def initial() -> 'Position':
        return Position(0, 1, 1)

    def next(self) -> 'Position':
        return Position(self.offset + 1, self.line, self.line_offset + 1)

    def new_line(self) -> 'Position':
        return Position(self.offset + 1, self.line + 1, 1)

    @property
    def offset(self) -> int:
        return self.__offset

    @property
    def line(self) -> int:
        return self.__line

    @property
    def line_offset(self) -> int:
        return self.__line_offset

    def __str__(self):
        return "line {} offset {}".format(self.line, self.line_offset)


class SourcePosition:
    def __init__(self, source: str, position: Position) -> None:
        self.__source = source
        self.__position = position

    @staticmethod
    def initial(source: str) -> 'SourcePosition':
        return SourcePosition(source, Position.initial())

    def next(self) -> 'SourcePosition':
        return SourcePosition(self.source, self.position.next())

    def new_line(self) -> 'SourcePosition':
        return SourcePosition(self.source, self.position.new_line())

    @property
    def source(self) -> str:
        return self.__source

    @property
    def position(self) -> Position:
        return self.__position

    @property
    def is_at_end(self) -> bool:
        return self.position.offset >= len(self.source)


class SourceSpan:
    def __init__(self, source: str, start: Position, end: Position) -> None:
        self.__source = source
        self.__start = start
        self.__end = end

    @staticmethod
    def from_positions(start: SourcePosition, end: SourcePosition) -> 'SourceSpan':
        if start.source != end.source:
            raise Exception('Sources don\'t match')

        return SourceSpan(start.source, start.position, end.position)

    @staticmethod
    def from_spans(start: 'SourceSpan', end: 'SourceSpan'):
        if start.source != end.source:
            raise Exception('Sources don\'t match')

        return SourceSpan(start.source, start.start, end.end)

    def text(self):
        return self.source[self.start.offset:self.end.offset]

    @property
    def source(self) -> str:
        return self.__source

    @property
    def start(self) -> Position:
        return self.__start

    @property
    def end(self) -> Position:
        return self.__end

    def __str__(self) -> str:
        if self.start.line == self.end.line:
            return '{}-{}'.format(self.start, self.end.line_offset)

        return '{} - {}'.format(self.start, self.end)


