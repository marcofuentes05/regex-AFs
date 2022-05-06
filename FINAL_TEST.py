from flaskr.utils.direct import *
from flaskr.utils.lexical import *
from functools import reduce
import re
input_stream = ''
NEW_LINE = chr(219)

CHARACTERS = [i for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ']
NUMBERS = [i for i in '0123456789']
SPECIAL_CHARACTERS = [i for i in '\(\)\;\+\=\{\}\.\<\>']
BLANK_SPACE = ' '


def everything_or(cumulative, current):
    return '{}|{}'.format(cumulative, current)

KEYWORDS = {'if': 'si', 'for': 'para', 'while': 'mientras', 'WHILE': 'MIENTRAS', 'While': 'Mientras'}
TOKENS = {'identificador': '^(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)|(0|1|2|3|4|5|6|7|8|9|0))*$', 'numero': '^(0|1|2|3|4|5|6|7|8|9|0)((0|1|2|3|4|5|6|7|8|9|0))*$', 'numeroDecimal': '^(0|1|2|3|4|5|6|7|8|9|0)((0|1|2|3|4|5|6|7|8|9|0))*(\.)(0|1|2|3|4|5|6|7|8|9|0)((0|1|2|3|4|5|6|7|8|9|0))*$', 'numeroHex': '^(0|1|2|3|4|5|6|7|8|9|0|A|B|C|D|E|F)((0|1|2|3|4|5|6|7|8|9|0|A|B|C|D|E|F))*(H)$', 'espacioEnBlanco': '^(\t| )((\t| ))*$', 'cadena': '^(")((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|0|1|2|3|4|5|6|7|8|9|0|\t| ))*(")$'}

def read_file(file_path):
    string = ''
    with open(file_path, 'r') as file:
        for line in file:
            for character in line:
                if character != '\n':
                    string += character
                else:
                    string += NEW_LINE
    return string


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
        if temporal_lex in KEYWORDS and (not reduce(lambda cummulative, current : cummulative or bool(re.match(current[1], input_stream[inicio:avance + 1])), TOKENS.items(), False)):
            token_flow += f"{KEYWORDS[temporal_lex]} "
            print('KEYWORD ')
            inicio = counter
            is_evaluating = False
        elif temporal_lex == BLANK_SPACE:
            # token_flow += 'BLANK_SPACE '
            # print('BLANK_SPACE ')
            inicio = counter
            is_evaluating = False
        elif temporal_lex == NEW_LINE:
            inicio = counter
            is_evaluating = False
        else:
            for key, value in TOKENS.items():
                if temporal_lex and re.match(value, temporal_lex) and (not reduce(lambda cummulative, current : cummulative or bool(re.match(current[1], input_stream[inicio:avance + 1])), TOKENS.items(), False)) and (not reduce(lambda cummulative, current : cummulative or bool(re.match(current[1], input_stream[inicio:avance + 2])), TOKENS.items(), False)):
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

if __name__ == '__main__':
    print(analyze(read_file('tests/ArchivoPrueba3Entrada.txt')))
        