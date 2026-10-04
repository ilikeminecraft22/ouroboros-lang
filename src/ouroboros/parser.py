from .nodes import *
from .lexer import Lexer, TokenType, Token, LexerError


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        index = self.pos + offset

        if index >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[index]

    def advance(self):
        token = self.current()

        if self.pos < len(self.tokens) - 1:
            self.pos += 1

        return token

    def check(self, token_type):
        return self.current().type == token_type

    def match(self, *token_types):
        if self.current().type in token_types:
            return self.advance()

        return None

    def expect(self, token_type):
        token = self.current()

        if token.type != token_type:
            raise ParserError(
                f"Expected {token_type.name}, "
                f"got {token.type.name} "
                f"at {token.line}:{token.column}"
            )

        return self.advance()

    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            pass

    def parse(self):
        statements = []

        self.skip_newlines()

        while not self.check(TokenType.EOF):
            statements.append(self.parse_top_level())
            self.skip_newlines()

        return Program(statements)

    def parse_top_level(self):
        if self.match(TokenType.REQUIRE):
            return self.parse_require()

        if self.match(TokenType.FUNC):
            return self.parse_function()

        raise ParserError(
            f"Unexpected token {self.current().type.name} "
            f"at {self.current().line}:{self.current().column}"
        )

    def parse_require(self):
        module = self.expect(TokenType.IDENTIFIER)

        return Require(module.value)

    def parse_function(self):
        return_type = self.parse_type()

        name = self.expect(TokenType.IDENTIFIER)

        self.expect(TokenType.LPAREN)

        parameters = []

        if not self.check(TokenType.RPAREN):
            while True:
                param_type = self.parse_type()
                param_name = self.expect(TokenType.IDENTIFIER)

                parameters.append(
                    Parameter(
                        param_type,
                        param_name.value,
                    )
                )

                if not self.match(TokenType.COMMA):
                    break

        self.expect(TokenType.RPAREN)
        self.expect(TokenType.OPEN)

        body = self.parse_block()

        # parse_block stops BEFORE the closing `end`.
        self.expect(TokenType.END)

        return Function(
            return_type=return_type,
            name=name.value,
            parameters=parameters,
            body=body,
        )

    def parse_type(self):
        if self.match(TokenType.INT):
            type_name = "int"
        elif self.match(TokenType.FLOAT):
            type_name = "float"
        elif self.match(TokenType.BOOL):
            type_name = "bool"
        elif self.match(TokenType.STRING_TYPE):
            type_name = "string"
        elif self.match(TokenType.CHAR):
            type_name = "char"
        elif self.match(TokenType.VOID):
            type_name = "void"
        else:
            raise ParserError(
                f"Expected type, got {self.current().type.name}"
            )

        while self.match(TokenType.STAR):
            type_name += "*"

        while self.match(TokenType.LBRACKET):
            self.expect(TokenType.RBRACKET)
            type_name += "[]"

        return type_name

    def parse_block(self):
        statements = []

        self.skip_newlines()

        while (
            not self.check(TokenType.END)
            and not self.check(TokenType.ELIF)
            and not self.check(TokenType.ELSE)
        ):
            if self.check(TokenType.EOF):
                raise ParserError(
                    "Unexpected end of file; expected 'end'"
                )

            statements.append(self.parse_statement())
            self.skip_newlines()

        return statements

    def parse_statement(self):
        if self.match(TokenType.LET):
            return self.parse_variable(inferred=True)

        if self.check(TokenType.INT) \
                or self.check(TokenType.FLOAT) \
                or self.check(TokenType.BOOL) \
                or self.check(TokenType.STRING_TYPE) \
                or self.check(TokenType.CHAR) \
                or self.check(TokenType.VOID):

            return self.parse_variable(inferred=False)

        if self.match(TokenType.RETURN):
            return self.parse_return()

        if self.match(TokenType.WHILE):
            return self.parse_while()

        if self.match(TokenType.IF):
            return self.parse_if()

        if self.check(TokenType.IDENTIFIER):
            return self.parse_identifier_statement()

        raise ParserError(
            f"Unexpected token {self.current.type.name} "
            f"at line {self.current.line}"
        )

    def parse_variable(self, inferred):
        if inferred:
            type_name = None
        else:
            type_name = self.parse_type()

        name = self.expect(TokenType.IDENTIFIER)

        self.expect(TokenType.ASSIGN)

        value = self.parse_expression()

        return VariableDeclaration(
            type=type_name,
            name=name.value,
            value=value,
        )

    def parse_return(self):
        if self.check(TokenType.NEWLINE) \
                or self.check(TokenType.END):
            return Return(None)

        return Return(self.parse_expression())

    def parse_while(self):
        condition = self.parse_expression()

        self.expect(TokenType.OPEN)

        body = self.parse_block()

        self.expect(TokenType.END)

        return While(
            condition=condition,
            body=body,
        )

    def parse_if(self):
        condition = self.parse_expression()

        self.expect(TokenType.OPEN)

        body = self.parse_block()

        elif_blocks = []

        while self.match(TokenType.ELIF):
            elif_condition = self.parse_expression()

            self.expect(TokenType.OPEN)

            elif_body = self.parse_block()

            elif_blocks.append(
                Elif(
                    condition=elif_condition,
                    body=elif_body,
                )
            )

        else_body = None

        if self.match(TokenType.ELSE):
            self.expect(TokenType.OPEN)

            else_body = self.parse_block()

        self.expect(TokenType.END)

        return If(
            condition=condition,
            body=body,
            elif_blocks=elif_blocks,
            else_body=else_body,
        )

    def parse_identifier_statement(self):
        parts = [
            self.expect(TokenType.IDENTIFIER).value
        ]

        while self.match(TokenType.COLON):
            parts.append(
                self.expect(TokenType.IDENTIFIER).value
            )

        name = QualifiedName(parts)

        if self.match(TokenType.LPAREN):
            arguments = self.parse_arguments()

            self.expect(TokenType.RPAREN)

            return Call(
                function=name,
                arguments=arguments,
            )

        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()

            if len(parts) != 1:
                raise ParserError(
                    "Cannot assign to a qualified name"
                )

            return Assignment(
                name=parts[0],
                value=value,
            )

        raise ParserError(
            f"Expected ':' , '=' or '(' after identifier "
            f"at {self.current().line}:{self.current().column}"
        )

    def parse_arguments(self):
        arguments = []

        if self.check(TokenType.RPAREN):
            return arguments

        while True:
            arguments.append(self.parse_expression())

            if not self.match(TokenType.COMMA):
                break

        return arguments

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        expression = self.parse_comparison()

        while self.match(
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
        ):
            operator = self.tokens[self.pos - 1]

            right = self.parse_comparison()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
            )

        return expression

    def parse_comparison(self):
        expression = self.parse_term()

        while self.match(
            TokenType.LESS,
            TokenType.GREATER,
            TokenType.LESS_EQUAL,
            TokenType.GREATER_EQUAL,
        ):
            operator = self.tokens[self.pos - 1]

            right = self.parse_term()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
            )

        return expression

    def parse_term(self):
        expression = self.parse_factor()

        while self.match(
            TokenType.PLUS,
            TokenType.MINUS,
        ):
            operator = self.tokens[self.pos - 1]

            right = self.parse_factor()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
            )

        return expression

    def parse_factor(self):
        expression = self.parse_postfix()

        while self.match(
            TokenType.STAR,
            TokenType.SLASH,
        ):
            operator = self.tokens[self.pos - 1]

            right = self.parse_postfix()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
            )

        return expression

    def parse_primary(self):
        token = self.current()

        if self.match(TokenType.INTEGER):
            return Literal(
                int(token.value),
                "int",
            )

        if self.match(TokenType.FLOAT_LITERAL):
            return Literal(
                float(token.value),
                "float",
            )

        if self.match(TokenType.STRING):
            return Literal(
                token.value,
                "string",
            )

        if self.match(TokenType.TRUE):
            return Literal(
                True,
                "bool",
            )

        if self.match(TokenType.FALSE):
            return Literal(
                False,
                "bool",
            )

        if self.match(TokenType.LBRACKET):
            elements = []

            if not self.check(TokenType.RBRACKET):
                while True:
                    elements.append(self.parse_expression())

                    if not self.match(TokenType.COMMA):
                        break

            self.expect(TokenType.RBRACKET)

            return ArrayLiteral(elements)

        if self.check(TokenType.IDENTIFIER):
            parts = [
                self.advance().value
            ]

            while self.match(TokenType.COLON):
                parts.append(
                    self.expect(TokenType.IDENTIFIER).value
                )

            if len(parts) == 1:
                return Identifier(parts[0])

            return QualifiedName(parts)

        raise ParserError(
            f"Expected expression, got {token.type.name} "
            f"at {token.line}:{token.column}"
        )

    def parse_postfix(self):
        expression = self.parse_primary()

        while True:
            if self.match(TokenType.LPAREN):
                arguments = self.parse_arguments()
                self.expect(TokenType.RPAREN)

                expression = Call(
                    function=expression,
                    arguments=arguments,
                )

            elif self.match(TokenType.LBRACKET):
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)

                expression = IndexExpression(
                    array=expression,
                    index=index,
                )

            else:
                break

        return expression