from .nodes import *


class ASTPrinter:
    def print(self, node, indent=0):
        prefix = " " * indent

        if isinstance(node, Program):
            print(prefix + "Program")

            for statement in node.statements:
                self.print(statement, indent + 2)

        elif isinstance(node, Require):
            print(prefix + f"Require: {node.module}")

        elif isinstance(node, Function):
            print(
                prefix
                + f"Function: {node.return_type} {node.name}"
            )

            if node.parameters:
                print(prefix + "  Parameters")

                for parameter in node.parameters:
                    self.print(parameter, indent + 4)

            print(prefix + "  Body")

            for statement in node.body:
                self.print(statement, indent + 4)

        elif isinstance(node, Parameter):
            print(
                prefix
                + f"Parameter: {node.type} {node.name}"
            )

        elif isinstance(node, ArrayLiteral):
            print(" " * indent + "Array")

            for element in node.elements:
                self.print(element, indent + 2)

        elif isinstance(node, VariableDeclaration):
            type_name = node.type or "auto"

            print(
                prefix
                + f"Variable: {type_name} {node.name}"
            )

            print(prefix + "  Value")

            self.print(node.value, indent + 4)

        elif isinstance(node, IndexExpression):
            print(" " * indent + "Index")

            print(" " * (indent + 2) + "Array")
            self.print(node.array, indent + 4)

            print(" " * (indent + 2) + "Index")
            self.print(node.index, indent + 4)

        elif isinstance(node, Assignment):
            print(prefix + f"Assignment: {node.name}")

            self.print(node.value, indent + 2)

        elif isinstance(node, Return):
            print(prefix + "Return")

            if node.value is not None:
                self.print(node.value, indent + 2)

        elif isinstance(node, While):
            print(prefix + "While")

            print(prefix + "  Condition")
            self.print(node.condition, indent + 4)

            print(prefix + "  Body")

            for statement in node.body:
                self.print(statement, indent + 4)

        elif isinstance(node, If):
            print(prefix + "If")

            print(prefix + "  Condition")
            self.print(node.condition, indent + 4)

            print(prefix + "  Body")

            for statement in node.body:
                self.print(statement, indent + 4)

            for elif_block in node.elif_blocks:
                print(prefix + "  Elif")
                self.print(
                    elif_block.condition,
                    indent + 4,
                )

                for statement in elif_block.body:
                    self.print(statement, indent + 4)

            if node.else_body is not None:
                print(prefix + "  Else")

                for statement in node.else_body:
                    self.print(statement, indent + 4)

        elif isinstance(node, Elif):
            print(prefix + "Elif")

        elif isinstance(node, Call):
            if node.module:
                name = f"{node.module}:{node.name}"
            else:
                name = node.name

            print(prefix + f"Call: {name}")

            for argument in node.arguments:
                self.print(argument, indent + 2)

        elif isinstance(node, Identifier):
            print(prefix + f"Identifier: {node.name}")

        elif isinstance(node, Literal):
            print(
                prefix
                + f"Literal: {node.value!r} "
                + f"({node.type})"
            )

        elif isinstance(node, BinaryExpression):
            print(
                prefix
                + f"Binary: {node.operator}"
            )

            self.print(node.left, indent + 2)
            self.print(node.right, indent + 2)

        else:
            print(prefix + f"<unknown {type(node).__name__}>")