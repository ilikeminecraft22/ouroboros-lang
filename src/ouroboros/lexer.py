from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    REQUIRE = auto()
    FUNC = auto()
    LET = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    OPEN = auto()
    END = auto()

    # Types
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STRING_TYPE = auto()
    VOID = auto()
    CHAR = auto()

    # Literals
    IDENTIFIER = auto()
    INTEGER = auto()
    FLOAT_LITERAL = auto()
    STRING = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()

    # Other
    NEWLINE = auto()
    EOF = auto()
    CPP = auto()

    # Boolean
    TRUE = auto()
    FALSE = auto()



KEYWORDS = {
    "require": TokenType.REQUIRE,
    "func": TokenType.FUNC,
    "let": TokenType.LET,
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "return": TokenType.RETURN,
    "open": TokenType.OPEN,
    "end": TokenType.END,

    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "bool": TokenType.BOOL,
    "string": TokenType.STRING_TYPE,
    "void": TokenType.VOID,
    "char": TokenType.CHAR,

    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        return (
            f"Token({self.type.name}, "
            f"{self.value!r}, "
            f"{self.line}:{self.column})"
        )


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def peek(self, offset=0):
        index = self.pos + offset

        if index >= len(self.source):
            return "\0"

        return self.source[index]

    def advance(self):
        char = self.peek()

        if char == "\0":
            return char

        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def error(self, message):
        raise LexerError(
            f"{message} at {self.line}:{self.column}"
        )

    def tokenize(self):
        tokens = []

        while self.peek() != "\0":
            token = self.next_token()

            if token is not None:
                tokens.append(token)

        tokens.append(
            Token(
                TokenType.EOF,
                "",
                self.line,
                self.column,
            )
        )

        return tokens

    def next_token(self):
        char = self.peek()

        # Whitespace
        if char in " \t\r":
            self.advance()
            return None

        # Newline
        if char == "\n":
            line = self.line
            column = self.column

            self.advance()

            return Token(
                TokenType.NEWLINE,
                "\\n",
                line,
                column,
            )

        # Comments
        if char == "/" and self.peek(1) == "/":
            self.skip_comment()
            return None

        # Identifier / keyword
        if char.isalpha() or char == "_":
            return self.read_identifier()

        # Number
        if char.isdigit():
            return self.read_number()

        # String
        if char == '"':
            return self.read_string()

        # Two-character operators
        two_char = char + self.peek(1)

        operators = {
            "==": TokenType.EQUAL,
            "!=": TokenType.NOT_EQUAL,
            "<=": TokenType.LESS_EQUAL,
            ">=": TokenType.GREATER_EQUAL,
        }

        if two_char in operators:
            line = self.line
            column = self.column

            self.advance()
            self.advance()

            return Token(
                operators[two_char],
                two_char,
                line,
                column,
            )

        # Single-character tokens
        single_char = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,

            "=": TokenType.ASSIGN,
            "<": TokenType.LESS,
            ">": TokenType.GREATER,

            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
        }

        if char in single_char:
            line = self.line
            column = self.column

            self.advance()

            return Token(
                single_char[char],
                char,
                line,
                column,
            )

        self.error(f"Unexpected character {char!r}")

    def skip_comment(self):
        while self.peek() not in ("\n", "\0"):
            self.advance()

    def read_identifier(self):
        line = self.line
        column = self.column

        value = ""

        while True:
            char = self.peek()

            if not (char.isalnum() or char == "_"):
                break

            value += self.advance()

        token_type = KEYWORDS.get(
            value,
            TokenType.IDENTIFIER,
        )

        return Token(
            token_type,
            value,
            line,
            column,
        )

    def read_number(self):
        line = self.line
        column = self.column

        value = ""

        while self.peek().isdigit():
            value += self.advance()

        # Decimal number
        if self.peek() == "." and self.peek(1).isdigit():
            value += self.advance()

            while self.peek().isdigit():
                value += self.advance()

            return Token(
                TokenType.FLOAT_LITERAL,
                value,
                line,
                column,
            )

        return Token(
            TokenType.INTEGER,
            value,
            line,
            column,
        )

    def read_string(self):
        line = self.line
        column = self.column

        self.advance()  # opening "

        value = ""

        while True:
            char = self.peek()

            if char == "\0":
                self.error("Unterminated string")

            if char == "\n":
                self.error("Unterminated string")

            if char == '"':
                self.advance()
                break

            # Basic escape sequences
            if char == "\\":
                self.advance()

                escaped = self.peek()

                escapes = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    '"': '"',
                    "\\": "\\",
                }

                if escaped not in escapes:
                    self.error(
                        f"Unknown escape sequence '\\{escaped}'"
                    )

                value += escapes[escaped]
                self.advance()
                continue

            value += self.advance()

        return Token(
            TokenType.STRING,
            value,
            line,
            column,
        )