from flaskr.utils.direct import *
from flaskr.utils.lexical import *
from functools import reduce
import re
input_stream = ''

CHARACTERS = [i for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ']
NUMBERS = [i for i in '0123456789']
SPECIAL_CHARACTERS = [i for i in '\(\)\;\+\=\{\}\.\<\>']
BLANK_SPACE = ' '

def everything_or(cumulative, current):
    return '{}|{}'.format(cumulative, current)

TOKENS = {}

KEYWORDS = {'for': 'FOR', 'int': 'INT', 'console': 'CONSOLE'}


with open('test_file.txt', 'r') as file:
    for line in file:
        for character in line:
            if character != '\n' and character != ' ':
                input_stream += character



def analyze(input_stream):
    inicio = 0
    avance = 0
    is_evaluating = False
    token_flow = ''
    for counter in range(len(input_stream) + 1):
        if counter == inicio: is_evaluating = True
        temporal_lex = input_stream[inicio:avance]
        print(temporal_lex)
        if temporal_lex in KEYWORDS:
            token_flow += 'KEYWORD '
            print('KEYWORD ')
            inicio = counter
            is_evaluating = False
        elif temporal_lex == BLANK_SPACE:
            token_flow += 'BLANK_SPACE '
            print('BLANK_SPACE ')
            inicio = counter
            is_evaluating = False
        # elif temporal_lex in SPECIAL_CHARACTERS:
        #     token_flow += 'SPECIAL_CHARACTER '
        #     print('SPECIAL_CHARACTER ')
        #     inicio = counter
        # elif temporal_lex in NUMBERS:
        #     token_flow += 'NUMBER  '
        #     print('NUMBER  ')
        #     inicio = counter
        # elif temporal_lex and re.match(TOKENS['identifier'], temporal_lex) and not re.match(TOKENS['identifier'], input_stream[inicio:avance + 1]):
        #     print('IDENTIFIER')
        #     token_flow += 'IDENTIFIER '
        #     inicio = counter
        # elif temporal_lex and re.match(TOKENS['string'], temporal_lex):
        #     print('STRING')
        #     token_flow += 'STRING '
        #     inicio = counter
        else:
            for key, value in TOKENS.items():
                if temporal_lex and re.match(value, temporal_lex) and (not re.match(value, input_stream[inicio:avance + 1]) or input_stream[inicio:avance + 1] == temporal_lex ):
                    print(key)
                    token_flow += '{} '.format(key)
                    inicio = counter
                    is_evaluating = False
                    break
        avance += 1

    if is_evaluating:
        print('LEXICAL ERROR')
        print(inicio)
        print(len(input_stream))
        return {
            'message': 'LEXICAL ERROR'
        }
    else:
        print(token_flow, file=open('token_flow.txt', 'a'))
        return {
            'message': token_flow
        }
        