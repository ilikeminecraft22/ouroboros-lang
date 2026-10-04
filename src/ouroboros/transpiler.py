import subprocess
from pathlib import Path

from .lexer import Lexer
from .parser import Parser
from .codegen import CppCodegen


def compile_file(source_path, output_path):
    source_path = Path(source_path)
    output_path = Path(output_path)

    source = source_path.read_text()

    # Ouroboros → tokens
    tokens = Lexer(source).tokenize()

    # Tokens → AST
    program = Parser(tokens).parse()

    # AST → C++
    cpp = CppCodegen().generate(program)

    output_path.write_text(cpp)

    return output_path