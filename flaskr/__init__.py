import os
from flask import Flask, request, send_from_directory
from .utils.lexical import *
from .utils.direct import *

ABC = [letter for letter in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#0123456789\u03B5']
IMAGES_DIRECTORY = '../tmp/'

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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

    def core_thompson(regex, string):
        string = string_middleware(string) # Fix '+' character
        lexical_tree = Tree(regex)
        tree = lexical_tree.get_tree()
        AFD_transitions = {}
        alphabet=[]
        AFN_transitions={}
        arbolito = tree
        counter = 1
        for element in tree.postorder:
            AFD_transitions[str(counter)] = {
                "value": chr(element.value),
                "initial_state": None,
                "final_state": None,
            }
            element.value = counter
            counter +=1
        for hoja in arbolito.leaves:
            for letra in ABC:
                if letra == AFD_transitions[str(hoja.value)]["value"]:
                    if letra not in alphabet:
                        alphabet.append(letra)
        alphabet.sort()
        alphabet.append("E")
        may_proceed = alphabet_valid(alphabet, string) and parenthesis_validator(string) and parenthesis_validator(regex)
        if not may_proceed:
            return {
                'message': 'Error! The string is not in the language described by the regex'
            }
        final_state = lexical_tree.thompson(arbolito, AFD_transitions, alphabet, AFN_transitions)
        result = lexical_tree.AFN_sym(string, AFN_transitions, 'S{}'.format(final_state-1))

        AFD_transitions = {}
        lexical_tree.subsets(AFN_transitions, AFD_transitions, alphabet)

        result = lexical_tree.AFD_sym_subsets(AFD_transitions, string, 'S{}'.format(final_state-1))

        return {
            'regex': regex,
            'string': string,
            'result': 'ACCEPTED' if result else 'REJECTED',
        }

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
            for character in ABC:
                if character == direct_table[str(leaf.value)]["value"]:
                    if character not in alphabet:
                        alphabet.append(character)
        alphabet.sort()
        for j in tree.leaves:
            direct_table[str(j.value)]["is_leaf"] = True
        may_proceed = alphabet_valid(alphabet, string) and parenthesis_validator(string) and parenthesis_validator(regex)
        if not may_proceed:
            return {
                'message': 'Error! The string is not in the language described by the regex'
            }
        for node in tree.postorder:
            anulable(node, direct_table)
            first_position(node, direct_table)
            last_position(node, direct_table)
            next_position(node, direct_table)
        transitions(AFD_transitions, tree, direct_table, alphabet)
        resultado = AFD_sym_direct(AFD_transitions, test_string, str(tree.right.value), alphabet, tree)
        return {
            'regex': augmented_regex,
            'string': test_string,
            'result': 'ACCEPTED' if resultado else 'REJECTED',
        }

    @app.route('/thompson')
    def thompson():
        return core_thompson(request.args.get("regex"), request.args.get("string"))

    @app.route('/direct')
    def direct():
        return core_direct(request.args.get("regex"), request.args.get("string"))

    @app.route('/get_AF')
    def get_AF():
        algorithm = request.args.get("algorithm")
        is_deterministic = request.args.get("is_deterministic") == 'True'
        if not is_deterministic and algorithm == "direct":
            return {
                'message': 'Direct method does not prouce a non deterministic graph'
            }
        if algorithm == "thompson":
            if is_deterministic:
                return send_from_directory(IMAGES_DIRECTORY, 'AFD-subsets.png', as_attachment=True)
            else:
              return send_from_directory(IMAGES_DIRECTORY, 'AFN-thompson.png', as_attachment=True)
        else:
            return send_from_directory(IMAGES_DIRECTORY, 'AFD-direct.png', as_attachment=True)
    return app