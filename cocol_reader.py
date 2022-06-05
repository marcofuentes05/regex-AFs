# Coco/l reader
# COMPILER name
#  ScannerSpecifications
#  ParserSpecifications
#  END name .
#  .
import regex as re
from unicodedata import name
from functools import reduce
import copy
from lexer_template import *
from LEXER import *


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
COCOL_START_PRODUCTION_ACTION = '(.'
COCOL_END_PRODUCTION_ACTION = '.)'
STRING_DELIMITATOR = '"'

REGEX_SPECIAL_CHARACTERS = '.+*?^$()[]\{}|\\'

compiler_template = {
    'NAME': '',
    'CHARACTERS': {},
    'KEYWORDS': {},
    'TOKENS': {},
    'PRODUCTIONS': {},
}

VOCABULARY_RE = {
    'production_action': '^(\(\.)(.*)(\.\))$',
    'ident': '^[a-zA-Z_][a-zA-Z0-9]*$',
    'number': '^[0-9]+',
    'string': '^(\")(.*)(\")$',
    'char': '^\'.\'',
    'comment': '^/\*.*\*/',
    'assign': '^=$',
    'kleene': '^(\{)(.+)(\})$',
    'option': '^\[(.*)\]$',
    'addition': '^(\+)$',
    'substraction': '^(\-)$',
    'production_parameter': '^<(.*)>$',
    # 'group': '^(\()(.+)(\))$',
    'group': '^(\()(.*)(?R)*(\))$'
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


def get_last_children(node, terminals):
    children = []
    for child in node.children:
        if child.type in terminals:
            children.append(child.value)
        else:
            children = [*children, get_last_children(child, terminals)]
    return children


class RecursiveDescentNode:
    def __init__(self, value):
        # este va a ser de tipo [node]
        self.children: list[RecursiveDescentNode] = []
        self.value: str = value
        self.parent = None

    def add_child(self, child):
        self.children.append(RecursiveDescentNode(child))

    def get_children(self, terminals, non_terminals):
        children = []
        for child in self.children:
            if child.value in terminals:
                children.append(child)
            elif child.value in non_terminals:
                children = [*children, *
                            child.get_children(terminals, non_terminals)]
        return children

    def __str__(self):
        return self.value


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
        self.build_raw_compiler()
        if self.errors:
            for error in self.errors:
                print('{}{}'.format(bcolors.FAIL, error))
        self.transform_characters_regex()
        self.input_string_prods = '3 + 4 * 5; '
        initial_state = RecursiveDescentNode(
            self.regex_compiler['PRODUCTIONS']['EstadoInicial']['elements'][0][0])
        initial_state.add_child('EstadoInicialPrime')
        # self.recursive_descent(initial_state)
        for error in self.errors:
            print(bcolors.FAIL + error)

    def print_compiler(self, compiler):
        for key, value in compiler.items():
            if key == 'NAME':
                print('{}{}: {}{}'.format(
                    bcolors.OKBLUE, key, bcolors.OKCYAN, value))
            else:
                print('{}{}'.format(bcolors.OKBLUE, key))
                for internal_key, internal_value in value.items():
                    print('{}{}:{}'.format(bcolors.OKCYAN,
                          internal_key, internal_value))

    def get_cocol_tokens(self) -> None:
        inicio = 0
        avance = 0
        inside_line_comment = False
        inside_block_comment = False
        inside_action = False
        is_evaluating = True
        is_productions = False
        is_in_string = False
        for counter in range(len(self.input_stream) + 1):
            if counter == inicio:
                is_evaluating = True
            temporal_lex = self.input_stream[inicio:avance]
            if not (inside_line_comment or inside_block_comment or inside_action):
                if temporal_lex in COCOL_KEYWORDS:
                    self.token_flow += temporal_lex
                    self.token_flow_list.append((temporal_lex, 'keyword'))
                    is_productions = True
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == BLANK_SPACE or temporal_lex == chr(9):
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
                    self.token_flow_list.append(
                        (temporal_lex, 'START_MULTILINE_COMMENT'))
                    inside_block_comment = True
                elif temporal_lex == COCOL_START_PRODUCTION_ACTION:
                    # self.token_flow += 'START_PRODUCTION_ACTION '
                    # self.token_flow_list.append((temporal_lex, 'START_PRODUCTION_ACTION'))
                    inside_action = True
                else:
                    for key, value in VOCABULARY_RE.items():
                        if temporal_lex and re.match(value, temporal_lex) and (not re.match(value, self.input_stream[inicio:avance + 1]) or self.input_stream[inicio:avance + 1] == temporal_lex):
                            if key == 'group' and temporal_lex[-2] == '"':
                                break
                            self.token_flow += '{} '.format(key)
                            self.token_flow_list.append((temporal_lex, key))
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
                elif inside_action:
                    if temporal_lex[-2:] == COCOL_END_PRODUCTION_ACTION:
                        inside_action = False
                        inicio = counter
                        self.token_flow_list.append(
                            (temporal_lex, 'production_action'))
                        is_evaluating = False
            avance += 1

        if is_evaluating:
            self.token_flow += 'ERROR '
            self.token_flow_list.append((temporal_lex, 'LEXICAL ERROR'))
            self.errors.append(
                'LEXICAL ERROR @ {} - {}'.format(avance, temporal_lex))

    def build_raw_compiler(self):
        # Evaluamos nombre al principio y al final
        # [print(token) for token in self.token_flow_list]
        mode = ''
        for index, token in enumerate(self.token_flow_list):
            if token[0] in ['CHARACTERS', 'KEYWORDS', 'TOKENS', 'PRODUCTIONS'] and index > 0 and self.token_flow_list[index - 1][0] != 'EXCEPT':
                mode = token[0]
            if token[0] == 'COMPILER':
                if self.token_flow_list[index + 1][1] == 'ident':
                    name_start = self.token_flow_list[index + 1][0]
            if token[0] == 'END':
                if self.token_flow_list[index + 1][1] == 'ident':
                    name_end = self.token_flow_list[index + 1][0]
                break
            if token[1] == 'ident':
                # si el siguiente es asignacion
                if self.token_flow_list[index + 1][1] == 'assign':
                    lista_temporal = self.token_flow_list[index + 2:]
                    temporal_array = []
                    for token_temporal in lista_temporal:
                        if token_temporal[1] != 'END_OF_LINE':
                            temporal_array.append(token_temporal)
                        else:
                            break
                    self.raw_compiler[mode][token[0]] = temporal_array
                # Por si es una prod con parametros
                elif self.token_flow_list[index+1][1] == 'production_parameter' and self.token_flow_list[index + 2][1] == 'assign':
                    lista_temporal = [
                        self.token_flow_list[index + 1], *self.token_flow_list[index + 3:]]
                    temporal_array = []
                    for token_temporal in lista_temporal:
                        if token_temporal[1] != 'END_OF_LINE':
                            temporal_array.append(token_temporal)
                        else:
                            break
                    self.raw_compiler[mode][token[0]] = temporal_array
        if (name_start != name_end):
            print('No se encontró nombre del compilador')
            self.errors.append('COMPILER NAME')
        self.raw_compiler['NAME'] = name_start
        self.print_compiler(self.raw_compiler)

    def evaluate_kleene(self, kleene_token):
        kleene_token = kleene_token[1: -1]
        ids = kleene_token.split('|')
        return_string = []
        for index, id in enumerate(ids):
            if id in self.raw_compiler['CHARACTERS'].keys():
                return_string.append(
                    f"({reduce(everything_or, self.regex_compiler['CHARACTERS'][id])})")
        return f"({'|'.join(return_string)})*"

    def evaluate_production_kleene(self, kleene_token):
        # kleene_token = kleene_token[1: -1]
        inicio = 0
        avance = 0
        return_token_flow = []
        inside_line_comment = False
        inside_block_comment = False
        inside_action = False
        is_evaluating = True
        is_productions = False
        is_in_string = False
        # print(kleene_token)
        for counter in range(len(kleene_token) + 1):
            if counter == inicio:
                is_evaluating = True
            temporal_lex = kleene_token[inicio:avance]
            # print(temporal_lex)
            if not (inside_line_comment or inside_block_comment or inside_action):
                if temporal_lex in COCOL_KEYWORDS:
                    # self.token_flow += temporal_lex
                    return_token_flow.append((temporal_lex, 'keyword'))
                    is_productions = True
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == BLANK_SPACE or temporal_lex == chr(9):
                    # print('BLANK_SPACE')
                    # self.token_flow += 'BLANK_SPACE '
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == MY_NEW_LINE:
                    # self.token_flow += 'NEW_LINE '
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == COCOL_END_OF_LINE:
                    # self.token_flow += 'END_OF_LINE '
                    return_token_flow.append((temporal_lex, 'END_OF_LINE'))
                    inicio = counter
                    is_evaluating = False
                elif temporal_lex == LINE_COMMENT_INDICATOR:
                    # self.token_flow += 'LINE_COMMENT '
                    return_token_flow.append((temporal_lex, 'LINE_COMMENT'))
                    inside_line_comment = True
                elif temporal_lex == START_MULTILINE_COMMENT_INDICATOR:
                    # self.token_flow += 'START_MULTILINE_COMMENT '
                    return_token_flow.append(
                        (temporal_lex, 'START_MULTILINE_COMMENT'))
                    inside_block_comment = True
                elif temporal_lex == COCOL_START_PRODUCTION_ACTION:
                    self.token_flow += 'START_PRODUCTION_ACTION '
                    # return_token_flow.append((temporal_lex, 'START_PRODUCTION_ACTION'))
                    inside_action = True
                else:
                    for key, value in VOCABULARY_RE.items():
                        if temporal_lex and re.match(value, temporal_lex) and (not re.match(value, kleene_token[inicio:avance + 1]) or kleene_token[inicio:avance + 1] == temporal_lex):
                            if key == 'group' and temporal_lex[-2] == '"':
                                break
                            # self.token_flow += '{} '.format(key)
                            return_token_flow.append((temporal_lex, key))
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
                elif inside_action:
                    if temporal_lex[-2:] == COCOL_END_PRODUCTION_ACTION:
                        inside_action = False
                        inicio = counter
                        return_token_flow.append(
                            (temporal_lex, 'production_action'))
                        is_evaluating = False
            avance += 1

        # if is_evaluating:
        #     # self.token_flow += 'ERROR '
        #     return_token_flow.append((temporal_lex, 'LEXICAL ERROR'))
        #     self.errors.append('LEXICAL ERROR @ {} - {}'.format(avance, temporal_lex))
        return return_token_flow

    def evaluate_option(self, option_token):
        option_token = option_token[1: -1]
        ids = option_token.split('|')
        return_string = []
        for index, id in enumerate(ids):
            if id in self.raw_compiler['CHARACTERS'].keys():
                return_string.append(
                    f"({reduce(everything_or, self.regex_compiler['CHARACTERS'][id])})")
        return f"({'|'.join(return_string)})?"

    def transform_characters_regex(self):
        self.regex_compiler['NAME'] = self.raw_compiler['NAME']
        # print(f"{bcolors.OKGREEN}TOKENS{bcolors.ENDC}")
        for identifier, value in self.raw_compiler['CHARACTERS'].items():
            # value es el array de (valor, token)
            temporal_string = []
            mode = None
            isChr = False
            for (value_token, token) in value:
                if token == 'string':
                    if mode != None:
                        if mode == 'addition':
                            temporal_string.extend(
                                [i if i not in REGEX_SPECIAL_CHARACTERS else f"\{i}" for i in value_token[1:-1]])
                        else:
                            temporal_string = [
                                i if i not in REGEX_SPECIAL_CHARACTERS else f"\{i}" for i in temporal_string if i not in value_token[1:-1]]
                        mode = None
                    else:
                        temporal_string.extend(
                            [i if i not in REGEX_SPECIAL_CHARACTERS else f"\{i}" for i in value_token[1:-1]])
                elif token == 'ident':
                    if mode != None:
                        if mode == 'addition':
                            temporal_string.extend(
                                self.regex_compiler['CHARACTERS'][value_token])
                        else:
                            temporal_string = [
                                i for i in temporal_string if i not in self.regex_compiler['CHARACTERS'][value_token]]
                        mode = None
                    else:
                        temporal_string.extend(
                            self.regex_compiler['CHARACTERS'][value_token])
                elif token == 'addition':
                    mode = 'addition'
                elif token == 'substraction':
                    mode = 'substraction'
                elif token == 'keyword' and value_token == 'CHR':
                    isChr = True
                elif isChr:
                    temporal = chr(int(value_token[1: -1]))
                    temporal_string.append(
                        temporal if temporal not in REGEX_SPECIAL_CHARACTERS else f"\{temporal}")
            self.regex_compiler['CHARACTERS'][identifier] = temporal_string

        for identifier, value in self.raw_compiler['KEYWORDS'].items():
            value_token, token = value[0]
            if token == 'string':
                # self.regex_compiler['KEYWORDS'][value]
                self.regex_compiler['KEYWORDS'][value_token[1: -1]
                                                ] = identifier
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

        # Ahora vemos las prods
        for identifier, value in self.raw_compiler['PRODUCTIONS'].items():
            # print(value)
            new_term = {
                'elements': [[]],
                'type': '',
                'action': None
            }
            # Termino: {
            #    right_side: [
            #       {
            #          element,
            #          type: 'TERMINAL'|'NON_TERMINAL'|'KLEENE',
            #          actions: ''
            #       }
            #   ],
            # }

            # Primero hay que identificar anonimous tokens DONE
            # Primero deberia hacer un tipo flatten de los elementos y luego concretar mi estructura de datos
            for index, (value_token, token) in enumerate(value):
                # Ignoramos params y/o acciones
                # print('value: ', value)/
                if token == 'production_action':
                    action_has_params = value[index -
                                              1][1] == 'production_parameter'
                    is_this_element_action = (index == 0) or (
                        action_has_params and index == 1)
                    if is_this_element_action:
                        if identifier in self.regex_compiler['PRODUCTIONS'].keys():
                            self.regex_compiler['PRODUCTIONS'][identifier]['action'] = {
                                'body': value_token[2:-2],
                                'parameters': value[index-1][0] if action_has_params else False
                            }
                        else:
                            self.regex_compiler['PRODUCTIONS'][identifier] = {
                                **new_term,
                                'action': {
                                    'body': value_token[2:-2],
                                    'parameters': value[index-1][0] if action_has_params else False
                                }
                            }

                # if token in ('production_parameter', 'production_action'):
                #     if identifier in self.regex_compiler['ACTIONS'].keys():
                #         self.regex_compiler['ACTIONS'][identifier].append(
                #             value_token)
                #     else:
                #         self.regex_compiler['ACTIONS'][identifier] = [
                #             value_token]
                #     pass
                # Deshacemos cerraduras de kleene
                elif token == 'kleene':
                    # print(value_token)
                    print(index)
                    print(value[index])
                    print(value[index-1][1])
                    prev_index = index - 1
                    next_index = index + 1
                    new_value = value_token[1: -1]
                    inside_kleene = self.evaluate_production_kleene(new_value)
                    identifier_prime = identifier+'Prime'
                    # print('INSIDE KLEENE\n',inside_kleene)
                    for index, (value_element, token_element) in enumerate(inside_kleene):
                        if token_element == 'string':
                            anonimous_token_value = value_element[1: -1]
                            safe_anonimous_token_value = f'\\{anonimous_token_value}'
                            new_token_name = f'anonimous_token_{value_element[1:-1]}'
                            new_token_regex = f'^{safe_anonimous_token_value if anonimous_token_value in REGEX_SPECIAL_CHARACTERS else anonimous_token_value}$'
                            self.regex_compiler['TOKENS'][new_token_name] = new_token_regex
                            inside_kleene[index] = (new_token_name, 'ident')
                        elif token in ('production_parameter', 'production_action'):
                            if identifier in self.regex_compiler['ACTIONS'].keys():
                                self.regex_compiler['ACTIONS'][identifier].append(
                                    value_token)
                            else:
                                self.regex_compiler['ACTIONS'][identifier] = [
                                    value_token]
                    new_term['type'] = 'kleene'
                    new_term['elements'][0] += [(identifier_prime, 'ident')]
                    self.regex_compiler['PRODUCTIONS'][identifier] = new_term
                    self.regex_compiler['PRODUCTIONS'][identifier_prime] = {
                        'elements': [[*filter(lambda element: element[1] not in (
                            'production_action', 'production_parameter'), inside_kleene), (identifier_prime, 'ident')], [('epsilon', 'epsilon')]],
                    }
                    if value[prev_index][1] in ('production_parameter', 'production_action'):
                        self.regex_compiler['PRODUCTIONS'][identifier_prime]['action'] = {
                            'body': value[next_index][0][2: -2],
                            'parameters': value[prev_index][1]
                        }
                elif token == 'ident':
                    new_term_element = (value_token, token)
                    if value[index+1][1] in ('production_action', 'production_parameter') and value[index + (2 if index+2 < len(value) else 1)][1] != 'kleene':
                        has_parameters = value[index +
                                               1][1] == 'production_parameter'
                        new_term_element = (*new_term_element, {
                            'body': value[index+2][0][2:-2] if has_parameters else value[index+1][0][2:-2],
                            'parameters': value[index+1][0] if has_parameters else False
                        })
                    if identifier in self.regex_compiler['PRODUCTIONS'].keys():
                        new_term['action'] = self.regex_compiler['PRODUCTIONS'][identifier]['action']
                    new_term['type'] = 'NON_TERMINAL'
                    new_term['elements'][0] += [new_term_element]
                    self.regex_compiler['PRODUCTIONS'][identifier] = new_term
                elif token == 'string':
                    # Agregar token anonimo a lista de tokens conocidos
                    anonimous_token_value = value_element[1: -1]
                    safe_anonimous_token_value = f'\\{anonimous_token_value}'
                    new_token_name = f'anonimous_token_{value_element[1:-1]}'
                    new_token_regex = f'^{safe_anonimous_token_value if anonimous_token_value in REGEX_SPECIAL_CHARACTERS else anonimous_token_value}$'
                    self.regex_compiler['TOKENS'][new_token_name] = new_token_regex
                    new_term += [(value_element[1:-1], new_token_name)]
                    self.regex_compiler['PRODUCTIONS'][identifier] = new_term
        self.print_compiler(self.regex_compiler)
        print()
        print()
        print()
        print(self.regex_compiler['PRODUCTIONS'])
        # print(self.regex_compiler['PRODUCTIONS']['Instruccion']['actions'])


reader = CocoLReader('tests/ArchivoPrueba0_prods.atg')
compiler = reader.regex_compiler
# lexer = Lexer(compiler['NAME'], compiler['KEYWORDS'], compiler['TOKENS'])
# lexer.create_file('FINAL_TEST.py')
