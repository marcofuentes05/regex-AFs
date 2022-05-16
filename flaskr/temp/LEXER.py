
from functools import reduce
from itertools import accumulate
import re
input_stream = ''
NEW_LINE = chr(219)

BLANK_SPACE = ' '


def everything_or(cumulative, current):
    return '{}|{}'.format(cumulative, current)

KEYWORDS = {'if': 'si', 'for': 'para', 'while': 'mientras', 'WHILE': 'MIENTRAS', 'While': 'Mientras'}
TOKENS = {'identificador': '^(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)|(0|1|2|3|4|5|6|7|8|9|0))*$', 'numero': '^(0|1|2|3|4|5|6|7|8|9|0)((0|1|2|3|4|5|6|7|8|9|0))*(num)$', 'numeroDecimal': '^(0|1|2|3|4|5|6|7|8|9|0)((0|1|2|3|4|5|6|7|8|9|0))*(\\.)(0|1|2|3|4|5|6|7|8|9|0)((0|1|2|3|4|5|6|7|8|9|0))*$', 'numeroHex': '^(0|1|2|3|4|5|6|7|8|9|0|A|B|C|D|E|F)((0|1|2|3|4|5|6|7|8|9|0|A|B|C|D|E|F))*(H)$', 'espacioEnBlanco': '^(\t| )((\t| ))*$', 'cadena': '^(\\.|\\+)((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z|0|1|2|3|4|5|6|7|8|9|0|\t| ))*(\\.|\\+)$'}

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


def analyze(input_stream):
    compiler_defines_blank = reduce(lambda cummulative, current : cummulative or bool(re.match(current[1], BLANK_SPACE)), TOKENS.items(), False)
    inicio = 0
    avance = 0
    is_evaluating = False
    token_flow = ''
    for counter in range(len(input_stream) + 1):
        if counter == inicio: is_evaluating = True
        temporal_lex = input_stream[inicio:avance]
        print(temporal_lex)
        if temporal_lex in KEYWORDS and (not reduce(lambda cummulative, current : cummulative or bool(re.match(current[1], input_stream[inicio:avance + 1])), [*TOKENS.items(), *KEYWORDS.keys()], False)):
            token_flow += f"{KEYWORDS[temporal_lex]} "
            print('KEYWORD ')
            inicio = counter
            is_evaluating = False
        elif not compiler_defines_blank and temporal_lex == BLANK_SPACE:
            inicio = counter
            is_evaluating = False
        elif temporal_lex == NEW_LINE:
            inicio = counter
            is_evaluating = False
        else:
            for key, value in TOKENS.items():
                if temporal_lex and re.match(value, temporal_lex): # and (not reduce(lambda cummulative, value0: cummulative or re.match(value0[1], input_stream[inicio:avance + 1]), [*TOKENS.items(), *KEYWORDS.keys()], False) or input_stream[inicio:avance + 1] == temporal_lex ) and not  reduce(lambda cummulative, value0: cummulative or re.match(value0[1], input_stream[inicio:avance + 2]), TOKENS.items(), False):
                    temp = [character for character in input_stream[avance:]]
                    res = list(accumulate(temp, lambda x, y: "".join([x, y])))
                    remainder_stream = [f"{temporal_lex}{element}" for element in res]
                    string_has_match = lambda string : reduce(lambda accumulator, current: accumulator or re.fullmatch(current[1], string), [*TOKENS.items(), *KEYWORDS.keys()], False)
                    char_flow_has_furhter_match = reduce(lambda accumulator, current: accumulator or string_has_match(current), remainder_stream, False)
                    
                    if not char_flow_has_furhter_match:
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
            'token_flow': 'LEXICAL ERROR'
        }
    else:
        print(token_flow, file=open('token_flow.txt', 'a'))
        return {
            'token_flow': token_flow,
            'residue': temporal_lex
        }

if __name__ == '__main__':
    print(analyze(read_file('tests/ArchivoPrueba3Entrada.txt')))
        