from __future__ import annotations

class Lexer:
    def __init__(self, name: str, keywords: dict[str, str], tokens: dict[str, str]):
        self.name = name
        self.keywords = keywords
        self.tokens = tokens
        self.create_file("flaskr/temp/LEXER.py")

    def create_file(self, file_name: str) -> bool:
        new_file_content = ''
        new_file_content = f"""
from functools import reduce
import re
input_stream = ''
NEW_LINE = chr(219)

BLANK_SPACE = ' '


def everything_or(cumulative, current):
    return '{{}}|{{}}'.format(cumulative, current)

KEYWORDS = {self.keywords}
TOKENS = {self.tokens}

def read_file(file_path):
    string = ''
    with open(file_path, 'r') as file:
        for line in file:
            for character in line:
                if character != '\\n':
                    string += character
                else:
                    string += NEW_LINE
    return string


with open('test_file.txt', 'r') as file:
    for line in file:
        for character in line:
            if character != '\\n' and character != ' ':
                input_stream += character

compiler_defines_blank = reduce(lambda cummulative, current : cummulative or bool(re.match(current[1], BLANK_SPACE)), TOKENS.items(), False)

def analyze(input_stream):
    inicio = 0
    avance = 0
    is_evaluating = False
    token_flow = ''
    for counter in range(len(input_stream) + 1):
        if counter == inicio: is_evaluating = True
        temporal_lex = input_stream[inicio:avance]
        print(temporal_lex)
        if temporal_lex in KEYWORDS and (not reduce(lambda cummulative, current : cummulative or bool(re.match(current[1], input_stream[inicio:avance + 1])), TOKENS.items(), False)):
            token_flow += f"{{KEYWORDS[temporal_lex]}} "
            print('KEYWORD ')
            inicio = counter
            is_evaluating = False
        elif temporal_lex == BLANK_SPACE:
            if not compiler_defines_blank:
                inicio = counter
                is_evaluating = False
        elif temporal_lex == NEW_LINE:
            inicio = counter
            is_evaluating = False
        else:
            for key, value in TOKENS.items():
                if temporal_lex and re.match(value, temporal_lex) and (not reduce(lambda cummulative, value0: cummulative or re.match(value0[1], input_stream[inicio:avance + 1]), TOKENS.items(), False) or input_stream[inicio:avance + 1] == temporal_lex ) and not  reduce(lambda cummulative, value0: cummulative or re.match(value0[1], input_stream[inicio:avance + 2]), TOKENS.items(), False):
                    print(key)
                    token_flow += '{{}} '.format(key)
                    inicio = counter
                    is_evaluating = False
                    break
        avance += 1

    if is_evaluating:
        print('LEXICAL ERROR')
        print(inicio)
        print(len(input_stream))
        return {{
            'message': 'LEXICAL ERROR'
        }}
    else:
        print(token_flow, file=open('token_flow.txt', 'a'))
        return {{
            'message': token_flow
        }}

if __name__ == '__main__':
    print(analyze(read_file('tests/ArchivoPrueba3Entrada.txt')))
        """
        file = open(file_name, "x")
        file.write(new_file_content)
        file.close()

if __name__ == '__main__':
    lexer = Lexer('lexer_template', {
        'for': 'FOR',
        'int': 'INT',
        'console': 'CONSOLE',
    }, {})
