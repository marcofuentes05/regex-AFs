from flaskr.utils.direct import *
from flaskr.utils.lexical import *
from functools import reduce
import re
input_stream = ''


CHARACTERS = [i for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ']
NUMBERS = [i for i in '0123456789']
SPECIAL_CHARACTERS = [i for i in '\(\)\;\+\=\{\}\.\<\>']
BLANK_SPACE = ' '

def alphabet_valid(alphabet, string):
    for letter in string:
        if letter not in alphabet:
            return False
    return True

def parenthesis_validator(string):
    parenthesis_counter = 0
    for character in string:
        if character == '(':
            parenthesis_counter += 1
        elif character == ')':
            parenthesis_counter -= 1
    return parenthesis_counter == 0

def string_middleware(string):
    for c in range(0, len(string), 1):
        if string[c] == "+":
            sub_string = string[:c] # [0 ... c]
            postr = string[c+1:]    # [c+1 ... len(string)]
            contador = 0
            subs = ""
            sub_string_pointer = len(sub_string) - 1
            while(sub_string_pointer >= 0):
                if string[sub_string_pointer] == ")":
                    contador += 1
                    if contador != 1:
                        subs = string[sub_string_pointer] + subs
                    sub_string_pointer-=1

                elif string[sub_string_pointer] =="(":
                    contador -= 1
                    if contador == 0 :
                        sub_string_pointer = -1 
                    else:
                        subs = string[sub_string_pointer] + subs
                        sub_string_pointer -= 1
                else:
                    if contador != 0:
                        subs = string[sub_string_pointer] +subs
                        sub_string_pointer-=1
                    else:
                        subs = string[sub_string_pointer]
                        sub_string_pointer=-1

            if len(subs) != 1:
                return "{}*({}){}".format(sub_string, subs, postr)
            else:
                return "{}*{}".format(sub_string, subs + postr)
        else:
            return string

def core_direct(regex, string): 
    string = string_middleware(string) # Fix '+' character
    augmented_regex = '({})#'.format(regex)
    test_string = string
    lexical_tree = Tree(augmented_regex)
    tree = lexical_tree.get_tree()
    direct_table = {}
    alphabet=[]
    AFD_transitions= {}
    counter = 1
    for i in tree.postorder:
        direct_table[str(counter)] = {
            "value": chr(i.value),
            "node_value": i.value,
            "anulable": None,
            "first_position": None,
            "last_position": None,
            "next_position": [],
            "is_leaf": False,
        }
        i.value = counter
        counter +=1
    for leaf in tree.leaves:
        for character in [*CHARACTERS, *NUMBERS, *SPECIAL_CHARACTERS]:
            if character == direct_table[str(leaf.value)]["value"]:
                if character not in alphabet:
                    alphabet.append(character)
    # exit()
    alphabet.sort()
    for j in tree.leaves:
        direct_table[str(j.value)]["is_leaf"] = True
    may_proceed = alphabet_valid(alphabet, string)
    if not may_proceed:
        return {
            'message': 'Error!'
        }
    may_proceed = parenthesis_validator(regex)
    if not may_proceed:
        return {
            'message': 'Error!'
        }
    for node in tree.postorder:
        anulable(node, direct_table)
        first_position(node, direct_table)
        last_position(node, direct_table)
        next_position(node, direct_table)
    transitions(AFD_transitions, tree, direct_table, alphabet)
    resultado = AFD_sym_direct(AFD_transitions, test_string, str(tree.right.value), alphabet, tree)
    return {
        'regex': regex,
        'string': test_string,
        'result': 'ACCEPTED' if resultado else 'REJECTED',
    }

def everything_or(cumulative, current):
    return '{}|{}'.format(cumulative, current)

TOKENS = {
    'ID': '^({})({})*$'.format(reduce(everything_or, CHARACTERS), reduce(everything_or, [*CHARACTERS, *NUMBERS])),
    'NUMBER': '^({})({})*$'.format(reduce(everything_or, NUMBERS), reduce(everything_or, NUMBERS)),
    'HEXNUMBER': '^({})+$'.format(reduce(everything_or, [*NUMBERS, 'A', 'B', 'C', 'D', 'E', 'F'])),
    'STRING': '^(\")(.*)(\")$',
    'SPECIAL_CHARACTER': '^({})$'.format(reduce(everything_or, SPECIAL_CHARACTERS)),
    'SPECIAL_CHARACTER': '^(\(|\)|\;|\+|\=|\{|\}|\.|\<|\>)$'
}

KEYWORDS = {
    'for' : 'for' ,
    'int' : 'int' ,
    'console' : 'console' ,
    'log' : 'log' ,
    'out' : 'out' 
}


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