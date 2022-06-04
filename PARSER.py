# from cocol_reader import RecursiveDescentNode
from http.client import RemoteDisconnected
import numpy as np

token_flow = ['numeroToken', 'anonimous_token_+', 'numeroToken',
              'anonimous_token_*', 'numeroToken', 'anonimous_token_;']

terminals = ['numeroToken', 'IGNORE', 'anonimous_token_+',
             'anonimous_token_;', 'anonimous_token_*']
productions = {
    'EstadoInicial': {'elements': [[('EstadoInicialPrime', 'ident')]], 'type': 'kleene', 'actions': []},
    'EstadoInicialPrime': {'elements': [[('Instruccion', 'ident'), ('anonimous_token_;', 'ident'), ('EstadoInicialPrime', 'ident')], [('epsilon', 'epsilon')]]},
    'Instruccion': {'elements': [[('Expresion', 'ident')]], 'type': 'NON_TERMINAL', 'actions': []},
    'Expresion': {'elements': [[('Termino', 'ident'), ('ExpresionPrime', 'ident')]], 'type': 'kleene', 'actions': []},
    'ExpresionPrime': {'elements': [[(
        'anonimous_token_+', 'ident'), ('Termino', 'ident'), ('ExpresionPrime', 'ident')], [('epsilon', 'epsilon')]]},
    'Termino': {'elements': [[('Factor', 'ident'), ('TerminoPrime', 'ident')]], 'type': 'kleene', 'actions': []},
    'TerminoPrime': {'elements': [[('anonimous_token_*', 'ident'), ('Factor', 'ident'), ('TerminoPrime', 'ident')], [('epsilon', 'epsilon')]]},
    'Factor': {'elements': [[('Numero', 'ident')]], 'type': 'NON_TERMINAL', 'actions': []},
    'Numero': {'elements': [[('numeroToken', 'ident')]], 'type': 'NON_TERMINAL', 'actions': []}
}


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


non_terminals = [*productions.keys()]

index = 0

retreived_tokens = []


class GramaticElementNode:
    def __init__(self, value, parent=None):
        self.value = value
        self.is_terminal = value in [*terminals, 'epsilon']
        self.productions_values = [[element for (
            element, _) in production] for production in productions[value]['elements']] if value not in [*terminals, 'epsilon'] else []
        self.children = []
        self.parent = parent
        self.input_index = 0

    def initialize_children(self):
        if len(self.children) == 0:
            for production in self.productions_values:
                temporal = []
                for element in production:
                    temporal.append(GramaticElementNode(element, self))
                self.children.append(temporal)

    def analyze(self, current_index=0):
        self.initialize_children()
        inside_index = current_index
        for production in self.children:
            # Production is a list of GramaticElementNode
            num_evaluated_elements = 0
            for node in production:
                if inside_index < len(token_flow):
                    if node.value == token_flow[inside_index]:
                        inside_index += 1
                        retreived_tokens.append(node.value)
                        print(bcolors.OKBLUE+'FOUND TOKEN ',
                              node.value, inside_index)
                    elif not node.is_terminal:
                        print(bcolors.WARNING+'FOUND NON TERMINAL ', node.value)
                        inside_index = node.analyze(inside_index)
                    else:
                        if node.value == 'epsilon':
                            print(bcolors.OKBLUE+'FOUND EPSILON')
                            retreived_tokens.append('epsilon')
                        else:
                            print(bcolors.FAIL+f'INSIDE_INDEX {inside_index}')
                            print(bcolors.FAIL +
                                  f'CURRENT_INDEX {current_index}')
                            for _ in range(inside_index - current_index):
                                print(bcolors.FAIL+'REMOVED TOKEN ',
                                      retreived_tokens[-1])
                                retreived_tokens.pop()
                            inside_index = current_index
                            print(
                                bcolors.FAIL+f'FOUND TOKEN {node.value} but did not match with {token_flow[current_index]}')
                            break
                    num_evaluated_elements += 1
            if num_evaluated_elements == len(production):
                print(bcolors.OKCYAN+'PRODUCTION MATCHED')
                break
        print(bcolors.ENDC + 'RETREIVED TOKENS ',
              retreived_tokens, 'IN ', self.value)
        return inside_index


# class Parser:
#     def __init__(self):
#         self.index = 0
#         self.retrieved_tokens = []

#     def parse(self, element, index):
#         if element in non_terminals:
#             print('NON TERMINAL', element)
#             possible_expansions = productions[element]['elements']
#             for expansion in possible_expansions:
#                 expansion_worked = True
#                 for (value, _) in expansion:
#                     returned_index = self.parse(value, index)
#                     if returned_index < 0:
#                         expansion_worked = False
#                         break
#                 if expansion_worked:
#                     break
#             return self.parse(value, index + 1)
#         elif element == token_flow[self.index]:
#             print('TERMINAL: ', element)
#             self.retrieved_tokens.append(element)
#             return index + 1
#         elif element == 'epsilon':
#             print('EPSILON')
#             return index
#         else:
#             return -1

#     def parse_v2(self, start_node, input_index):
#         # start_node debe ser un NO TERMINAL de la gramatica
#         # input_index
#         inside_index = input_index
#         for produccion in productions[start_node]['elements']:
#             current_production_worked = False
#             for (element, _) in produccion:
#                 if element == token_flow[inside_index]:
#                     inside_index += 1
#                     self.retrieved_tokens.append(element)
#                     print(element, inside_index)
#                 elif element in non_terminals:
#                     result = self.parse_v2(element, inside_index)
#                     print(element, inside_index)
#                     pass
#                 else:
#                     # self.parse_v2(element, inside_index-1)
#                     break
#                     pass
#         return inside_index


parentElement = GramaticElementNode('EstadoInicial')
print(parentElement.productions_values)
parentElement.analyze()

# print(bcolors.WARNING + 'DEBUGGING')
# print([*filter(lambda token: token != 'epsilon', retreived_tokens)])
if np.array_equal([*filter(lambda token: token != 'epsilon', retreived_tokens)], token_flow):
    print(bcolors.OKGREEN+'INPUT VALIDATED')
else:
    print(bcolors.FAIL+'INPUT NOT VALIDATED')
"""parser = Parser()
print('TOKEN FLOW: ', token_flow)
result = parser.parse_v2('EstadoInicial', 0)
print('RESULT: ', result)
arint(parser.retrieved_tokens)"""
