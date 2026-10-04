from .nodes import *


class CodegenError(Exception):
    pass


class CppCodegen:
    def __init__(self):
        self.output = []
        self.indent_level = 0

    def emit(self, text=""):
        indentation = "    " * self.indent_level
        self.output.append(indentation + text)

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        if self.indent_level == 0:
            raise CodegenError("Cannot dedent below zero")

        self.indent_level -= 1

    def generate(self, program):
        self.output = []
        self.indent_level = 0

        for statement in program.statements:
            if isinstance(statement, Require):
                self.generate_require(statement)

        self.emit()

        for statement in program.statements:
            if not isinstance(statement, Require):
                self.generate_statement(statement)

        return "\n".join(self.output)

    def generate_qualified_name(self, node):
        return "::".join(node.parts)

    def generate_statement(self, node):
        if isinstance(node, Require):
            self.generate_require(node)

        elif isinstance(node, Function):
            self.generate_function(node)

        else:
            raise CodegenError(
                f"Unsupported top-level node: "
                f"{type(node).__name__}"
            )

    def generate_require(self, node):
        self.emit(f'#include <ouroboros/{node.module}.hpp>')

    def generate_function(self, node):
        return_type = self.cpp_type(node.return_type)

        parameters = ", ".join(
            self.generate_parameter(parameter)
            for parameter in node.parameters
        )

        self.emit(
            f"{return_type} {node.name}({parameters}) {{"
        )

        self.indent()

        for statement in node.body:
            self.generate_body_statement(statement)

        self.dedent()

        self.emit("}")
        self.emit()

    def generate_parameter(self, node):
        return (
            f"{self.cpp_type(node.type)} "
            f"{node.name}"
        )

    def generate_body_statement(self, node):
        if isinstance(node, Call):
            self.emit(
                self.generate_call(node) + ";"
            )

        elif isinstance(node, VariableDeclaration):
            self.generate_variable(node)

        elif isinstance(node, Assignment):
            self.emit(
                f"{node.name} = "
                f"{self.generate_expression(node.value)};"
            )

        elif isinstance(node, Return):
            self.generate_return(node)

        elif isinstance(node, While):
            self.generate_while(node)

        elif isinstance(node, If):
            self.generate_if(node)

        else:
            raise CodegenError(
                f"Unsupported statement: "
                f"{type(node).__name__}"
            )

    def generate_variable(self, node):
        if node.type is None:
            type_name = "auto"
        else:
            type_name = self.cpp_type(node.type)

        value = self.generate_expression(node.value)

        self.emit(
            f"{type_name} {node.name} = {value};"
        )

    def generate_return(self, node):
        if node.value is None:
            self.emit("return;")
            return

        value = self.generate_expression(node.value)

        self.emit(f"return {value};")

    def generate_while(self, node):
        condition = self.generate_expression(node.condition)

        self.emit(f"while ({condition}) {{")

        self.indent()

        for statement in node.body:
            self.generate_body_statement(statement)

        self.dedent()

        self.emit("}")

    def generate_if(self, node):
        condition = self.generate_expression(node.condition)

        self.emit(f"if ({condition}) {{")

        self.indent()

        for statement in node.body:
            self.generate_body_statement(statement)

        self.dedent()

        self.emit("}")

        for elif_block in node.elif_blocks:
            condition = self.generate_expression(
                elif_block.condition
            )

            self.emit(f"else if ({condition}) {{")

            self.indent()

            for statement in elif_block.body:
                self.generate_body_statement(statement)

            self.dedent()

            self.emit("}")

        if node.else_body is not None:
            self.emit("else {")

            self.indent()

            for statement in node.else_body:
                self.generate_body_statement(statement)

            self.dedent()

            self.emit("}")

    def generate_call(self, node):
        function = self.generate_expression(node.function)

        arguments = ", ".join(
            self.generate_expression(argument)
            for argument in node.arguments
        )

        return f"{function}({arguments})"

    def generate_expression(self, node):
        if isinstance(node, Literal):
            return self.generate_literal(node)

        if isinstance(node, ArrayLiteral):
            elements = ", ".join(
                self.generate_expression(element)
                for element in node.elements
            )

            if not node.elements:
                raise CodegenError(
                    "Cannot infer the type of an empty array"
                )

            element_type = self.cpp_type(
                node.elements[0].type
            )

            return f"std::vector<{element_type}>{{{elements}}}"

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, IndexExpression):
            array = self.generate_expression(node.array)
            index = self.generate_expression(node.index)

            return f"{array}[{index}]"

        if isinstance(node, QualifiedName):
            return "::".join(node.parts)

        elif isinstance(node, CppBlock):
            for line in node.code.splitlines():
                self.emit(line)

        if isinstance(node, BinaryExpression):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)

            return (
                f"({left} {node.operator} {right})"
            )

        if isinstance(node, Call):
            function = self.generate_expression(node.function)

            arguments = ", ".join(
                self.generate_expression(argument)
                for argument in node.arguments
            )

            return f"{function}({arguments})"

        raise CodegenError(
            f"Unsupported expression: "
            f"{type(node).__name__}"
        )

    def generate_literal(self, node):
        if node.type == "string":
            escaped = (
                node.value
                .replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("\t", "\\t")
                .replace("\r", "\\r")
            )

            return f'"{escaped}"'

        if node.type == "bool":
            return "true" if node.value else "false"

        return str(node.value)

    def cpp_type(self, type_name):
        type_map = {
            "int": "int",
            "float": "double",
            "bool": "bool",
            "string": "std::string",
            "char": "char",
            "void": "void",
        }

        # Array types.
        if type_name.endswith("[]"):
            base = type_name[:-2]

            return (
                "std::vector<"
                + self.cpp_type(base)
                + ">"
            )

        # Pointer types.
        if type_name.endswith("*"):
            base = type_name.rstrip("*")
            stars = "*" * (len(type_name) - len(base))

            return (
                self.cpp_type(base)
                + stars
            )

        if type_name not in type_map:
            raise CodegenError(
                f"Unknown type: {type_name}"
            )

        return type_map[type_name]