# Coco/l reader
# COMPILER name
#  ScannerSpecifications
#  ParserSpecifications
#  END name .
#  .
import re
from unicodedata import name
from functools import reduce
import copy
from lexer_template import *


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

MY_NEW_LINE = chr(219)

LINE_COMMENT = '//'
BLANK_SPACE = ' '

LINE_COMMENT_INDICATOR = '//'
START_MULTILINE_COMMENT_INDICATOR = '/*'
END_MULTILINE_COMMENT_INDICATOR = '*/'
COCOL_END_OF_LINE = '.'

REGEX_SPECIAL_CHARACTERS = '.+*?^$()[]\{}|\\'

compiler_template = {
    'NAME': '',
    'CHARACTERS': {},
    'KEYWORDS': {},
    'TOKENS': {}
}

VOCABULARY_RE = {
    'ident': '^[a-zA-Z_][a-zA-Z0-9]+$',
    'number': '^[0-9]+',
    'string': '^(\")(.*)(\")$',
    'char': '^\'.\'',
    'comment': '^/\*.*\*/',
    'assign': '^=$',
    'kleene': '^(\{)(.+)(\})$',
    'option': '^\[(.*)\]$',
    'addition': '^(\+)$',
    'substraction': '^(\-)$',
    'group': '^(\()(.+)(\))$',
}


COCOL_KEYWORDS = [
    'ANY',
    'CHARACTERS',
    'COMMENTS',
    'COMPILER',
    'CONTEXT',
    'END',
    'FROM',
    'IF',
    'IGNORE',
    'IGNORECASE',
    'NESTED',
    'OUT',
    'PRAGMAS',
    'PRODUCTIONS',
    'SYNC',
    'TOKENS',
    'WEAK',
    'KEYWORDS',
    'EXCEPT',
    'CHR'
]

SPECIAL_CHARACTERS = {
    '=',
    '.'
    '|',
    '()',
    '[]',
    '\{\}',
    '/*',
    '*/',
}


errors = []

def everything_or(cumulative, current):
    return '{}|{}'.format(cumulative, current)

class CocoLReader:
    def __init__(self, file_path: str):
        self.input_stream = ''
        self.token_flow = ''
        self.token_flow_list = []
        self.errors = []
        self.raw_compiler = copy.deepcopy(compiler_template)
        self.regex_compiler = copy.deepcopy(compiler_template)

        with open(file_path, 'r') as file:
            for line in file:
                for character in line:
                    if character == '\n':
                        self.input_stream += MY_NEW_LINE
                    else:
                        self.input_stream += character
        self.get_cocol_tokens()
        # for token in self.token_flow_list:
        #     print(token)
        self.build_raw_compiler()
        if self.errors:
            for error in self.errors:
                print('{}{}'.format(bcolors.FAIL, error))
        self.transform_characters_regex()
        for error in self.errors:
            print(bcolors.FAIL + error)

    def get_cocol_tokens(self) -> None:
        inicio = 0 
        avance = 0
        inside_line_comment = False
        inside_block_comment = False
        is_evaluating = True
        for counter in range(len(self.input_stream) + 1):
            if counter == inicio: is_evaluating = True
            temporal_lex = self.input_stream[inicio:avance]
            # print('[{}]'.format(temporal_lex))
            if not (inside_line_comment or inside_block_comment):
                if temporal_lex in COCOL_KEYWORDS:
                    self.token_flow += temporal_lex
                    self.token_flow_list.append((temporal_lex, 'keyword'))
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == BLANK_SPACE:
                    # print('BLANK_SPACE')
                    self.token_flow += 'BLANK_SPACE '
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == MY_NEW_LINE:
                    self.token_flow += 'NEW_LINE '
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == COCOL_END_OF_LINE:
                    self.token_flow += 'END_OF_LINE '
                    self.token_flow_list.append((temporal_lex, 'END_OF_LINE'))
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == LINE_COMMENT_INDICATOR:
                    self.token_flow += 'LINE_COMMENT '
                    self.token_flow_list.append((temporal_lex, 'LINE_COMMENT'))
                    inside_line_comment = True
                elif temporal_lex == START_MULTILINE_COMMENT_INDICATOR:
                    self.token_flow += 'START_MULTILINE_COMMENT '
                    self.token_flow_list.append((temporal_lex, 'START_MULTILINE_COMMENT'))
                    inside_block_comment = True
                else:
                    for key, value in VOCABULARY_RE.items():
                        if temporal_lex and re.match(value, temporal_lex) and (not re.match(value, self.input_stream[inicio:avance + 1]) or self.input_stream[inicio:avance + 1] == temporal_lex ):
                            self.token_flow += '{} '.format(key)
                            self.token_flow_list.append((temporal_lex, key))
                            # print(key)
                            inicio = counter
                            is_evaluating = False
                            break
            else:
                if inside_line_comment:
                    if temporal_lex[-1] == MY_NEW_LINE:
                        inside_line_comment = False
                        inicio = counter
                        is_evaluating = False
                elif inside_block_comment:
                    if temporal_lex[-2:] == END_MULTILINE_COMMENT_INDICATOR:
                        inside_block_comment = False
                        inicio = counter
                        is_evaluating = False
            avance += 1

        if is_evaluating:
            self.token_flow += 'ERROR '
            self.token_flow_list.append((temporal_lex, 'LEXICAL ERROR'))
            self.errors.append('LEXICAL ERROR @ {} - {}'.format(avance, temporal_lex))

    def build_raw_compiler(self):
        # Evaluamos nombre al principio y al final
        mode = ''
        for index, token in enumerate(self.token_flow_list):
            if token[0] in ['CHARACTERS', 'KEYWORDS', 'TOKENS'] and index > 0 and self.token_flow_list[index - 1][0] != 'EXCEPT':
                mode = token[0]
            if token[0] == 'COMPILER':
                if self.token_flow_list[index + 1][1] == 'ident':
                    name_start = self.token_flow_list[index + 1][0]
            if token[0] == 'END':
                if self.token_flow_list[index + 1][1] == 'ident':
                    name_end = self.token_flow_list[index + 1][0]
                break
            if token[1] == 'ident':
                if self.token_flow_list[index + 1][1] == 'assign': #si el siguiente es asignacion
                    lista_temporal = self.token_flow_list[index + 2:]
                    temporal_array = []
                    for token_temporal in lista_temporal:
                        if token_temporal[1] != 'END_OF_LINE':
                            temporal_array.append(token_temporal)
                        else:
                            break
                    self.raw_compiler[mode][token[0]] = temporal_array
        if not (name_start and name_end) or (name_start != name_end):
            print('No se encontró nombre del compilador')
            self.errors.append('COMPILER NAME')
        self.raw_compiler['NAME'] = name_start
        for key, value in self.raw_compiler.items() :
            if key == 'NAME':
                print('{}{}: {}{}'.format(bcolors.OKBLUE, key, bcolors.OKCYAN, value))
            else:
                print('{}{}'.format(bcolors.OKBLUE, key))
                for internal_key, internal_value in value.items():
                    print ('{}{}:{}'.format(bcolors.OKCYAN, internal_key, internal_value)) 
        
    def evaluate_kleene(self, kleene_token):
        kleene_token = kleene_token[1: -1]
        ids = kleene_token.split('|')
        return_string = []
        for index, id in  enumerate(ids):
            if id in self.raw_compiler['CHARACTERS'].keys():
                return_string.append(f"({reduce(everything_or, self.regex_compiler['CHARACTERS'][id])})")
        return f"({'|'.join(return_string)})*"

    def evaluate_option(self, option_token):
        option_token = option_token[1: -1]
        ids = option_token.split('|')
        return_string = []
        for index, id in  enumerate(ids):
            if id in self.raw_compiler['CHARACTERS'].keys():
                return_string.append(f"({reduce(everything_or, self.regex_compiler['CHARACTERS'][id])})")
        return f"({'|'.join(return_string)})?"

    def transform_characters_regex(self):
        self.regex_compiler['NAME'] = self.raw_compiler['NAME']
        print(f"{bcolors.OKGREEN}TOKENS{bcolors.ENDC}")
        for identifier, value in self.raw_compiler['CHARACTERS'].items():
            # value es el array de (valor, token)
            temporal_string = []
            mode = None
            isChr = False
            for (value_token, token) in value:
                if token == 'string':
                    if mode != None:
                        if mode == 'addition':
                            temporal_string.extend([i if i not in REGEX_SPECIAL_CHARACTERS else f"\{i}" for i in value_token[1:-1]])
                        else:
                            temporal_string = [i if i not in REGEX_SPECIAL_CHARACTERS else f"\{i}" for i in temporal_string if i not in value_token[1:-1]]
                        mode = None
                    else:
                        temporal_string.extend([i if i not in REGEX_SPECIAL_CHARACTERS else f"\{i}" for i in value_token[1:-1]])
                elif token == 'ident':
                    if mode != None:
                        if mode == 'addition':
                            temporal_string.extend(self.regex_compiler['CHARACTERS'][value_token])
                        else:
                            temporal_string = [i for i in temporal_string if i not in self.regex_compiler['CHARACTERS'][value_token]]
                        mode = None
                    else:
                        temporal_string.extend(self.regex_compiler['CHARACTERS'][value_token])
                elif token == 'addition':
                    mode = 'addition'
                elif token == 'substraction':
                    mode = 'substraction'
                elif token == 'keyword' and value_token == 'CHR':
                    isChr = True
                elif isChr:
                    temporal = chr(int(value_token[1: -1]))
                    temporal_string.append(temporal if temporal not in REGEX_SPECIAL_CHARACTERS else f"\{temporal}")
            self.regex_compiler['CHARACTERS'][identifier] = temporal_string

        for identifier, value in self.raw_compiler['KEYWORDS'].items():
            value_token, token = value[0]
            if token == 'string':
                self.regex_compiler['KEYWORDS'][value_token[1: -1]] = identifier # self.regex_compiler['KEYWORDS'][value]
            else:
                errors.append('KEYWORD ERROR - {}'.format(value[0]))

        for identifier, value in self.raw_compiler['TOKENS'].items():
            temporal_regex = ''
            for (value_token, token) in value:
                if token == 'ident':
                    temporal_regex += f"({ reduce(everything_or,  self.regex_compiler['CHARACTERS'][value_token])})"
                elif token == 'string':
                    new_value = value_token[1:-1]
                    modified_new_value = f"\\{new_value}"
                    temporal_regex += f"({ new_value if new_value not in REGEX_SPECIAL_CHARACTERS else modified_new_value})"
                elif token == 'kleene':
                    temporal_regex += self.evaluate_kleene(value_token)
                elif token == 'option':
                    temporal_regex += self.evaluate_option(value_token)
            self.regex_compiler['TOKENS'][identifier] = f"^{temporal_regex}$"
        for key, value in self.regex_compiler.items() :
            if key == 'NAME':
                print('{}{}: {}{}'.format(bcolors.OKBLUE, key, bcolors.OKCYAN, value))
            else:
                print('{}{}'.format(bcolors.OKBLUE, key))
                for internal_key, internal_value in value.items():
                    print ('{}{}:{}'.format(bcolors.OKCYAN, internal_key, internal_value)) 


# reader = CocoLReader('tests/ArchivoPrueba3.atg')
# compiler = reader.regex_compiler
# lexer = Lexer(compiler['NAME'], compiler['KEYWORDS'], compiler['TOKENS'])
# lexer.create_file('FINAL_TEST.py')