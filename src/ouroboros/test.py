from .lexer import Lexer
from .parser import Parser
from .ast_printer import ASTPrinter
from .codegen import CppCodegen


source = """
require io

func int main(int argc, char **argv) open
    int[] numbers = [10, 20, 30]
    io:println(numbers[0])
end
"""


tokens = Lexer(source).tokenize()

program = Parser(tokens).parse()

print("=== AST ===")
ASTPrinter().print(program)

print()
# print("=== C++ ===")

# cpp = CppCodegen().generate(program)

# print(cpp)