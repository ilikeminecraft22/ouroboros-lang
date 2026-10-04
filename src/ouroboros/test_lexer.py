from lexer import Lexer


source = '''
require io

func int main(int argc, char **argv) open
    let numbers = [10, 20, 30]
end
'''


lexer = Lexer(source)
tokens = lexer.tokenize()

for token in tokens:
    print(token)