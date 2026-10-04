import sys

from .transpiler import compile_file


def main():
    if len(sys.argv) != 3:
        print("usage: python3 build.py <source.ouro> <output>")
        raise SystemExit(1)

    source = sys.argv[1]
    output = sys.argv[2]

    compile_file(source, output)
    print(f"transpiled {source} -> {output}")