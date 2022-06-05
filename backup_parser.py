from http.client import RemoteDisconnected
import numpy as np

# token_flow = ['numeroToken', 'anonimous_token_+', 'numeroToken',
#               'anonimous_token_*', 'numeroToken', 'anonimous_token_;']
token_flow = 'numeroToken anonimous_token_+ numeroToken anonimous_token_* numeroToken anonimous_token_; numeroToken anonimous_token_+ numeroToken anonimous_token_; numeroToken anonimous_token_;'.split(
    ' ')
terminals = ['numeroToken', 'IGNORE', 'anonimous_token_+',
             'anonimous_token_;', 'anonimous_token_*']
productions = {
    'EstadoInicial': {'elements': [[('EstadoInicialPrime', 'ident')]], 'type': 'kleene', 'action': None},
    'EstadoInicialPrime': {'elements': [[('Instruccion', 'ident'), ('anonimous_token_;', 'ident'), ('EstadoInicialPrime', 'ident')], [('epsilon', 'epsilon')]]},
    'Instruccion': {'elements': [[('Expresion', 'ident', {'body': ' print("Resultado: " + resultado); ', 'parameters': '<ref resultado>'})]], 'type': 'NON_TERMINAL', 'action': {'body': ' int resultado; ', 'parameters': False}},
    'Expresion': {'elements': [[('Termino', 'ident'), ('ExpresionPrime', 'ident')]], 'type': 'kleene', 'action': {'body': ' int resultado1, resultado2; ', 'parameters': '<ref int resultado>'}},
    'ExpresionPrime': {'elements': [[('anonimous_token_+', 'ident'), ('Termino', 'ident'), ('ExpresionPrime', 'ident')], [('epsilon', 'epsilon')]], 'action': {'body': '(. resultado = resultado1;Û\t\t\t\t\t\t\t\t\t\t\t\t   print("Término: " + resultado); .)', 'parameters': 'production_parameter'}},
    'Termino': {'elements': [[('Factor', 'ident'), ('TerminoPrime', 'ident')]], 'type': 'kleene', 'action': {'body': ' int resultado1, resultado2; ', 'parameters': '<ref int resultado>'}},
    'TerminoPrime': {'elements': [[('anonimous_token_*', 'ident'), ('Factor', 'ident'), ('TerminoPrime', 'ident')], [('epsilon', 'epsilon')]], 'action': {'body': '(. resultado = resultado1;Û\t\t\t\t\t\t\t\t\t\t\t\t   print("Factor: " + resultado); .)', 'parameters': 'production_parameter'}},
    'Factor': {'elements': [[('Numero', 'ident', {'body': ' resultado = resultado1;Û\t\t\t\t\t\t\t\t\t\t\t\t   print("Número: " + resultado); ', 'parameters': '<ref resultado1>'})]], 'type': 'NON_TERMINAL', 'action': {'body': ' int resultado1; ', 'parameters': '<ref int resultado>'}},
    'Numero': {'elements': [[('numeroToken', 'ident', {'body': ' resultado = ultimoToken.obtenerValor();Û\t\t\t\t\t\t\t\t\t\t\t\t   print("Token: " + resultado); ', 'parameters': False})]], 'type': 'NON_TERMINAL', 'action': None}
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
            element, *_) in production] for production in productions[value]['elements']] if value not in [*terminals, 'epsilon'] else []
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


input_validated = True
for index, element in enumerate(retreived_tokens):
    if element == token_flow[index]:
        input_validated = input_validated and True

parentElement = GramaticElementNode('EstadoInicial')
print(parentElement.productions_values)
parentElement.analyze()

if input_validated:
    print(bcolors.OKGREEN+'INPUT VALIDATED')
else:
    print(bcolors.FAIL+'INPUT NOT VALIDATED')
