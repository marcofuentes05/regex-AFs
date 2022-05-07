import os
from flask import Flask, request, send_from_directory

from .utils.cocol_reader import CocoLReader
from .utils.lexer_template import *
from .utils.lexical import *
from .utils.direct import *
from .utils.analizador_lexico import *
from .temp.LEXER import *
import logging 

ABC = [letter for letter in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#0123456789\u03B5']
IMAGES_DIRECTORY = '../tmp/'
from logging.config import dictConfig

def create_app(test_config = None):
    app = Flask(__name__)
    uploads_dir = os.path.join(app.instance_path, 'uploads')
    # os.makedirs(uploads_dir)

    logging.basicConfig(filename='error.log',level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 # Files should not be larger than 16MB
    
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    app.logger.info('App successfuly started!')

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
        may_proceed = alphabet_valid(alphabet, string)
        if not may_proceed:
            return {
                'message': 'Error! The string contains characters that are not in the alphabet.'
            }
        may_proceed = parenthesis_validator(regex)
        if not may_proceed:
            return {
                'message': 'Error! The regex is not valid'
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
            if direct_table[str(leaf.value)]["value"] in ABC and direct_table[str(leaf.value)]["value"] not in alphabet:
            # for character in ABC:
            #     if character == direct_table[str(leaf.value)]["value"]:
            #         if character not in alphabet:
                        alphabet.append(direct_table[str(leaf.value)]["value"])
        alphabet.sort()
        for j in tree.leaves:
            direct_table[str(j.value)]["is_leaf"] = True
        may_proceed = alphabet_valid(alphabet, string)
        if not may_proceed:
            return {
                'message': 'Error! The string contains characters that are not in the alphabet.'
            }
        may_proceed = parenthesis_validator(regex)
        if not may_proceed:
            return {
                'message': 'Error! The regex is not valid'
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

    def core_direct_fixed(regex, string):
        re = '({})#'.format(regex)
        cadena=string
        #Se hace el arbol
        af = Analyzer(re)
        tree = af.build_sintax_tree()
        #Diccionario con la data para cada nodo anulable, primera pos...
        data = {}
        #Tabla de transiciones
        transiciones= {}
        #operadores
        letras='*|?+'
        #Caracteres en hojas de arbol
        alfabeto=[]
        arbol = tree
        contador = 1
        #Se llena el diccionario de datos con la cantidad de nodos
        for i in arbol.postorder:
            data[str(contador)] = {
                "value": chr(i.value),
                "node_value": i.value,
                "anulable": None,
                "primera_pos": None,
                "ultima_pos": None,
                "siguiente_pos": [],
                "is_leaf": False,
            }
            i.value = contador
            contador +=1
        #Se obtienen los caracteres de las hojas
        for hoja in arbol.leaves:
            for letra in letras:
                if letra != data[str(hoja.value)]["value"]:
                    if data[str(hoja.value)]["value"] not in alfabeto:
                        alfabeto.append(data[str(hoja.value)]["value"])
        alfabeto.sort()
        for j in arbol.leaves:
            data[str(j.value)]["is_leaf"] = True

        # Se hacen las fuciones anulable, primera pos, ultimo pos y siguiente pos para llenar la data
        for node in arbol.postorder:
            af.anulable(node, data)
            af.first_pos(node, data)
            af.last_pos(node, data)
            af.next_pos(node, data)
        
        #Se llena la tabla de transiciones
        af.transiciones(transiciones, arbol, data, alfabeto)
        # Se simula el afd
        resultado = af.simulacion(transiciones, cadena, str(arbol.right.value), alfabeto)


        #Se dibuja el afd
        dot = graphviz.Digraph(comment="AFD", format='png')
        dot.attr(rankdir="LR")

        #Se hacen los nodos
        for key in transiciones.keys():
            states = key.replace("[","")
            states = states.replace("]","")
            states = states.replace(" ","")
            states = states.split(",")
            if str(arbol.right.value) in states:
                dot.node(transiciones[key]["name"], transiciones[key]["name"], shape='doublecircle')
            else:
                dot.node(transiciones[key]["name"], transiciones[key]["name"], shape='circle')
                
        #Se hacen las transiciones
        for key, v in transiciones.items():
            for c in alfabeto:
                if v["name"] != None and v[c] != None:
                    dot.edge(v["name"], v[c], c)

        dot.render(directory='tmp', filename='AFD-direct')
        return {
            'regex': regex,
            'string': string,
            'result': 'ACCEPTED' if resultado else 'REJECTED',
        }


    def file_to_string(file):
        string = ''
        for line in file:
            for character in line.decode('utf-8'):
                if character != '\n':
                    string += character
                else:
                    string += chr(219) # Esto me ayuda con los comentarios
        return string

    @app.route('/upload_cocor', methods=['POST'])
    def upload_cocor():
        file = file_to_string()
        if file == None:
            app.logger.error('No file part')
            return {'message': 'No file part'}
        app.logger.info('File uploaded')
        # Aqui tendria que ir el cocol_reader
        return {
            'message': 'Success!',
        }
        

    @app.route('/thompson')
    def thompson():
        return core_thompson(request.args.get("regex"), request.args.get("string"))

    @app.route('/direct')
    def direct():
        return core_direct_fixed(request.args.get("regex"), request.args.get("string"))

    @app.route('/get_lexer')
    def get_lexer():
        if 'file' not in request.files:
            app.logger.error('No file part')
            return None
        uploaded_file = request.files['file']
        uploaded_file.save(os.path.join(uploads_dir, uploaded_file.filename))

        app.logger.info('File uploaded')
        reader = CocoLReader(os.path.join(uploads_dir, uploaded_file.filename))
        compiler = reader.regex_compiler
        if os.path.exists(app.root_path + '/temp/LEXER.py'):
            os.remove(app.root_path + '/temp/LEXER.py')
        Lexer(compiler['NAME'], compiler['KEYWORDS'], compiler['TOKENS'])
        return send_from_directory('temp', 'LEXER.py', as_attachment=True)

    @app.route('/execute_lexer')
    def execute_lexer():
        if 'file' not in request.files:
            app.logger.error('No file part')
            return None
        uploaded_file = request.files['file']
        if os.path.exists(os.path.join(uploads_dir, uploaded_file.filename)):
            os.remove(os.path.join(uploads_dir, uploaded_file.filename))

        uploaded_file.save(os.path.join(uploads_dir, uploaded_file.filename))

        string = ''
        with open(os.path.join(uploads_dir, uploaded_file.filename), 'r') as file:
            for line in file:
                for character in line:
                    if character != '\n':
                        string += character
                    else:
                        string += NEW_LINE

        return analyze(string)
        

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
