class Parser:
    def __init__(self, token_flow, token_value, terminals, productions, name):
        self.token_flow = token_flow
        self.token_value = token_value
        self.terminals = terminals
        self.productions = productions
        self.create_file("flaskr/temp/LEXER.py")

    def create_file(self, file_name: str) -> bool:
        new_file_content = f"""from flaskr.utils.direct import *
from http.client import RemoteDisconnected
import numpy as np


token_flow = {self.token_flow}
token_value = {self.token_value}
terminals = {self.terminals}
productions = {self.productions}


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

def initialize_actions():
    file_content = ''
    for element in productions.keys():
        if 'action' in productions[element].keys() and productions[element]['action'] is not None:
            parameters = ''.join([character for character in productions[element]['action']['parameters'].split(
                ' ') if character not in ('<ref, int, >')])[0:-1] if productions[element]['action']['parameters'] else ''
            file_content += f'def production_{{element}}({{parameters}}):\\n\\t'
            file_content += productions[element]['action']['body']
            file_content += '\\n\\n'

    file = open('functions.py', 'w')
    file.write(file_content)
    file.close()



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
        check_epsilon = False
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
                        if inside_index == -1:
                            return -1
                    else:
                        if node.value == 'epsilon':
                            print(bcolors.OKBLUE+'FOUND EPSILON')
                            retreived_tokens.append('epsilon')
                            check_epsilon = True
                        else:
                            print(bcolors.FAIL+f'INSIDE_INDEX {{inside_index}}')
                            print(bcolors.FAIL +
                                  f'CURRENT_INDEX {{current_index}}')
                            for _ in range(inside_index - current_index):
                                print(bcolors.FAIL+'REMOVED TOKEN ',
                                      retreived_tokens[-1])
                                retreived_tokens.pop()
                            inside_index = current_index
                            print(
                                bcolors.FAIL+f'FOUND TOKEN {{node.value}} but did not match with {{token_flow[current_index]}}')
                            break
                    num_evaluated_elements += 1
            if num_evaluated_elements == len(production):
                print(bcolors.OKCYAN+'PRODUCTION FILLED')
                break
        if inside_index == current_index and not check_epsilon:
            return -1
        print(bcolors.ENDC + 'RETREIVED TOKENS ',
              retreived_tokens, 'IN ', self.value)
        return inside_index


if __name__ == '__main__':
    parentElement = GramaticElementNode('EstadoInicial')
    print(parentElement.productions_values)
    parentElement.analyze()

    filtered_retreived_values = [
        *filter(lambda element: element != 'epsilon', retreived_tokens)]

    print(filtered_retreived_values)
    print(token_flow)
    input_validated = True
    if len(filtered_retreived_values) == len(token_flow):
        for index, element in enumerate(filtered_retreived_values):
            input_validated = input_validated and element == token_flow[index]
    else:
        input_validated = False

    if input_validated:
        print(bcolors.OKGREEN+'INPUT VALIDATED')
    else:
        print(bcolors.FAIL+'INPUT NOT VALIDATED')

    initialize_actions()

"""

        file = open(file_name, "x")
        file.write(new_file_content)
        file.close()
