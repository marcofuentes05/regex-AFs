import re as regex
from textwrap import indent
from binarytree import Node as BinaryTreeNode

class Nodo:
    def __init__(self, value, left=None, right=None):
        self.data = value
        self.left = left
        self.right = right

class Analyzer:
    def __init__(self, regex):
        self.current = None
        self.secondary_roots = []
        self.initialize(regex, None)

    def get_sub_tree(self, secondary_exp):
        i = 0
        while i < len(secondary_exp):
            if secondary_exp[i] == "(":
                contador = 1
                for j in range(i+1, len(secondary_exp)):
                    if secondary_exp[j] == "(":
                        contador += 1
                    elif secondary_exp[j] == ")":
                        contador -= 1

                    counter = 0
                    if contador == 0 and secondary_exp[j] == ")":
                        if j + 1 < len(secondary_exp):
                            if secondary_exp[j+1] == "*" or secondary_exp[j+1] == "?":
                                counter += 2

                        end_of_exp = j + counter
                        return end_of_exp
            elif regex.match(r"[a-zA-Z0-9*]", secondary_exp[i]):
                end_of_exp = i
                for j in range(i+1, len(secondary_exp)):
                    if not regex.match(r"[a-zA-Z0-9*]", secondary_exp[j]):
                        break
                    end_of_exp = j
                return end_of_exp
            i += 1

    def initialize(self, secondary_exp, secondary_root_node):
        i = 0
        while i < len(secondary_exp):
            if secondary_exp[i] == "(":
                if i == 0:
                    contador = 1
                    for j in range(i+1, len(secondary_exp)):
                        if secondary_exp[j] == "(":
                            contador += 1
                        elif secondary_exp[j] == ")":
                            contador -= 1

                        counter = 0
                        if contador == 0:
                            if secondary_exp[j] == ")" and j + 1 < len(secondary_exp):
                                if secondary_exp[j+1] == "*" or secondary_exp[j+1] == "?":
                                    counter += 2

                            end_of_exp = j + counter
                            init = i + 1
                            self.initialize(secondary_exp[init:end_of_exp], secondary_root_node)
                            i = j
                            break
                else:
                    if secondary_exp[i-1] == ")" or secondary_exp[i-1] == "*" or secondary_exp[i-1] == "?" or regex.match(r"[a-z]", secondary_exp[i-1]):
                        end_sec_exp = self.get_sub_tree(secondary_exp[i:])
                        end_of_exp = i + 1 + end_sec_exp
                        self.initialize(secondary_exp[i:end_of_exp], len(self.secondary_roots))

                        if secondary_root_node is None:
                            secondary_node = self.secondary_roots.pop()
                        else:
                            secondary_node = self.secondary_roots.pop(secondary_root_node + 1)

                        if secondary_node is not None:
                            self.add_child(secondary_root_node, ".", None, secondary_node, "l")

                        i = i + end_of_exp + 1
            elif regex.match(r"[a-zA-Z0-9#]", secondary_exp[i]):
                if ((secondary_root_node is None and self.current is None) or i == 0) and i + 1 < len(secondary_exp) and regex.match(r"[a-zA-Z#]", secondary_exp[i+1]):
                    if i + 2 < len(secondary_exp) and (secondary_exp[i+2] == "*" or secondary_exp[i+2] == "?"):
                        self.add_child(secondary_root_node, ".", Nodo(secondary_exp[i]), Nodo(secondary_exp[i+2], Nodo(secondary_exp[i+1]), None), "l")
                        i += 2
                    else:
                        self.add_child(secondary_root_node, ".", Nodo(secondary_exp[i]), Nodo(secondary_exp[i+1]), "l")
                        i += 1
                elif (secondary_root_node is None and self.current is not None) or i != 0:
                    self.add_child(secondary_root_node, ".", None, Nodo(secondary_exp[i]), "l")
                else:
                    self.add_child(secondary_root_node, secondary_exp[i], None, None, "l")
                if i + 1 < len(secondary_exp):
                    if secondary_exp[i+1] == "*" or secondary_exp[i+1] == "?":
                        self.add_child(secondary_root_node, secondary_exp[i+1], Nodo(secondary_exp[i]), None, "l")
                    elif secondary_exp[i+1] == ")":
                        if i + 2 < len(secondary_exp):
                            if secondary_exp[i+2] == "*" or secondary_exp[i+2] == "?":
                                self.add_child(secondary_root_node, secondary_exp[i+2], Nodo(secondary_exp[i]), None, "l")
            
            elif secondary_exp[i] == "|" or secondary_exp[i] == ".":
                end_sec_exp = self.get_sub_tree(secondary_exp[i+1:])
                end_of_exp = i + 1 + end_sec_exp + 1
                self.initialize(secondary_exp[i+1:end_of_exp], len(self.secondary_roots))

                if secondary_root_node is None:
                    secondary_node = self.secondary_roots.pop()
                else:
                    secondary_node = self.secondary_roots.pop(secondary_root_node + 1)

                if secondary_node is not None:
                    self.add_child(secondary_root_node, secondary_exp[i], Nodo(secondary_exp[i-1]), secondary_node, "l")

                if end_of_exp < len(secondary_exp) and secondary_exp[end_of_exp] == ")":
                    if end_of_exp + 1 < len(secondary_exp):
                        if secondary_exp[end_of_exp+1] == "*" or secondary_exp[end_of_exp+1] == "?":
                            self.add_child(secondary_root_node, secondary_exp[end_of_exp+1], Nodo(secondary_exp[end_of_exp+1]), None, "l")

                i = i + end_of_exp + 1
            else:
                pass
            i += 1

    def build_sintax_tree(self):
        return build_tree(self.current)

    def add_child(self, secondary_root_node, values, left, right, is_brother):
        if secondary_root_node is None:
            if self.current is None:
                self.current = Nodo(values, left, right)
            else:
                if is_brother == "l":
                    self.current = Nodo(values, self.current, right)
        else:
            if secondary_root_node == len(self.secondary_roots):
                self.secondary_roots.append(Nodo(values, left, right))
            elif secondary_root_node < len(self.secondary_roots):
                if self.secondary_roots[secondary_root_node] is None:
                    self.secondary_roots[secondary_root_node] = Nodo(values, left, right)
                else:
                    if is_brother == "l":
                        self.secondary_roots[secondary_root_node] = Nodo(values, self.secondary_roots[secondary_root_node], right)

    #Funcion anulable
    def anulable(self, node, data):
        # Si es or se hace un or entre el anulable de los hijos
        if data[str(node.value)]["value"] == "|":
            data[str(node.value)]["anulable"] = data[str(node.left.value)]["anulable"] or data[str(node.right.value)]["anulable"]
        # Si es cerradura de kleen es verdadero automaticamente
        elif data[str(node.value)]["value"] == "*":
            data[str(node.value)]["anulable"] = True
        # Si es epsilon es verdadero
        elif data[str(node.value)]["value"] == "E":
            data[str(node.value)]["anulable"] == True
        # Si es concatenacion se hace un and entre el anulable de los hijos
        elif data[str(node.value)]["value"] == ".":
            data[str(node.value)]["anulable"] = data[str(node.left.value)]["anulable"] and data[str(node.right.value)]["anulable"]
        # Si es operador nulo es true
        elif data[str(node.value)]["value"] == "?":
            data[str(node.value)]["anulable"] = True
        # Si es solo una letra es falso
        else:
            data[str(node.value)]["anulable"] = False

    # Funcion primera posicion
    def first_pos(self, node, data):
        # Si es or entonces se una las primeras posiciones de los hijos
        if data[str(node.value)]["value"] == "|":
            data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
        # Si es cerradura de kleen entonces son todos las primera posiciones de su hijo
        elif data[str(node.value)]["value"] == "*":
            data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"]] for item in sublist]
        # Si es cadena vacia entonces no es nada
        elif data[str(node.value)]["value"] == "E":
            data[str(node.value)]["primera_pos"] = []
        # Si es concatenacion se evalua si el hijo de la izquierda es anulable
        # Si si lo es entonces se unen los primeras posiciones de los hijos
        # Si no entonces solo es la primera posicion del hijo izquierdo
        elif data[str(node.value)]["value"] == ".":
            if data[str(node.left.value)]["anulable"]:
                data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
            else:
                data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"]] for item in sublist]
        # Si es nulo entonces es la union de las primeras posiciones de los hijos
        elif data[str(node.value)]["value"] == "?":
            data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
        # Si es letra entonces la primera posicion es la letra
        else:
            data[str(node.value)]["primera_pos"] = [node.value]
    
    def last_pos(self, node, data):
        # Si es or entonces es la union de las ulitmas posiciones de los hijos
        if data[str(node.value)]["value"] == "|":
            data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
        # Si es cerradura de kleen entonces es la ultima posicion de su hijo
        elif data[str(node.value)]["value"] == "*":
            data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"]] for item in sublist]
        # Si es cadena vacia entonces no es nada
        elif data[str(node.value)]["value"] == "E":
            data[str(node.value)]["ultima_pos"] = []
        # Si es concatenecion se ve si el hijo de la derecha es anulable
        # Si si entonces es la union de las ultimos posiciones de los hijos
        # Si no entonces solo es la ultima posicion del hijo derecho
        elif data[str(node.value)]["value"] == ".":
            if data[str(node.right.value)]["anulable"]:
                data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
            else:
                data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.right.value)]["ultima_pos"]] for item in sublist]
        # Si es operador nulo entonces es la union de las ultimas posiciones de sus hijos
        elif data[str(node.value)]["value"] == "?":
            data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
        # Si es letra entonces la ultima posicion es el valor de esta
        else:
            data[str(node.value)]["ultima_pos"] = [node.value]

    # Funcion siguiente posicion 
    def next_pos(self, node, data):
        # Si es cerradura de kleen entonces las pimeras posiciones del hijo
        # Se agregan a cada ultima posicion del hijo como siguiente posicion
        if data[str(node.value)]["value"] == "*":
            for up in data[str(node.left.value)]["ultima_pos"]:
                for pp in data[str(node.left.value)]["primera_pos"]:
                    if pp not in data[str(node.left.value)]["siguiente_pos"]:
                        data[str(up)]["siguiente_pos"].append(pp)
        # Si es concatenacion entonces las primeras posiciones del hijo de la derecha
        # Se ponen en cada una de las ultimas posiciones del hijo de la izquierda como siguiente posicion
        elif data[str(node.value)]["value"] == ".":
            for up in data[str(node.left.value)]["ultima_pos"]:
                for pp in data[str(node.right.value)]["primera_pos"]:
                    if pp not in data[str(node.left.value)]["siguiente_pos"]:
                        data[str(up)]["siguiente_pos"].append(pp)

    # Funcion para hacer la tabla de transiciones
    def transiciones(self, trans, tree, data, alfabeto):
        # Contador para estados en 0
        contador = 0
        # Se crea el estado inicial el cual esta compuesto por las primeras posiciones de la raiz
        # Se le agrega como nombre S0
        trans[str(data[str(tree.value)]["primera_pos"])] = {
            "name": "S"+str(contador),
        }
        # Se le agrega los caracteres con los que se puede hacer transicion
        for letra in alfabeto:
            trans[str(data[str(tree.value)]["primera_pos"])][letra] = None
        # Se suma al contador para el siguiente estado
        contador += 1

        # While para completar la tabla de transiciones
        cont = True
        while(cont):
            # Largo inicial de tabla de estos
            initial_size = len(trans)
            keys = list(trans.keys())
            # Se itera sobre las llaves que representa cada estado del AFD
            for key in keys:
                # Se itera entre los caracteres para iteraciones para ir llenando cada estado con sus transiciones
                for letra in alfabeto:
                    # Si no hay una transicion hecha para ese caracter 
                    if trans[key][letra] == None:
                        # Lista de los identificadores que representan al caracter
                        new_state = []
                        # Se para de str a una lista con los identificadores que hay en ese estado
                        current_state = key.replace("[","")
                        current_state = current_state.replace("]","")
                        current_state = current_state.replace(" ","")
                        current_state = current_state.split(",")
                        # Si el identificador representa al caracter para la transicion se agregan las siguientes posiciones de esta al nuevo estado
                        for i in current_state:
                            if data[str(i)]["value"] == letra:
                                new_state.append(data[str(i)]["siguiente_pos"])
                        # se vuelve una sola lista y se ordena el nuevo estado
                        new_state = [item for sublist in new_state for item in sublist]
                        new_state = list(set(new_state))
                        new_state.sort()
                        if len(new_state) > 0:
                            # Si el estado nuevo no tienen ya una representaicone en la tabla
                            # Entonces se agrega a la tabla y se le crea su estado
                            if str(new_state) not in trans:
                                trans[str(new_state)] = {
                                    "name": "S"+str(contador)
                                }
                                for letter in alfabeto:
                                    trans[str(new_state)][letter] = None
                                contador +=1
                            # Se agrega este nuevo nombre del nuevo estado al la transicion del estado que se esta recorriendo acutalmente
                                trans[key][letra] = trans[str(new_state)]["name"]
                            else:
                                trans[key][letra] = trans[str(new_state)]["name"]
            # se vuelve a ver el valor de la tabla si cambio el valor al inicial se sigue en el while
            final_size = len(trans)
            if initial_size == final_size:
                # Si no cambio el valor de la tabal se confirma que todos los valores de transiciones esten llenos y no haya ninguno con vacio
                cont = not all(trans.values())

    # Algoritmo para simular un AFD
    # Para el algoritmo de pasar de exp a AFD
    def simulacion(self, trans, cadena, final_char, alfabeto):
        # Se empieza en estado 0
        current_state = "S0"
        cadena = cadena.replace("E","")
        for char in cadena:
            if char not in alfabeto:
                return False
        # Se recorre la cadena
        if cadena != "":
            for char in cadena:
                llave = ""
                # Se recorre la tabla de transiciones para buscar el estado que tiene esta transicion
                for key, v in trans.items():
                    # Si si hay una transicion con este caracter para el estado actual se guarda el estado
                    if v["name"] == current_state and v[char] != None:
                        llave = key
                    # Si no siginifica que no acepta la cadena
                    elif v["name"] == current_state and v[char] == None:
                        return False
                # Se cambia al nuevo estado
                current_state = trans[llave][char]
        # Ya finalizado de recorrer y con un estado final se comprueba si es de aceptacion
        for key, v in trans.items():
            # Se recorre la tabla y si el # se encuentra en los valores de este estado se acepta
            if v["name"] == current_state:
                chars = key.replace("[","")
                chars = chars.replace("]","")
                chars = chars.replace(" ","")
                chars = chars.split(",")
                if final_char in chars:
                    return True
                else:
                    return False

    #Cerradura de epsilon devuelve los estados a los que puedo ir con E
    def cerraduraEpsilon(self, state, trans, states = []):
        if state not in states:
            states.append(state)
        if (len(trans[state]["E"]) > 0):
            for current_state in trans[state]["E"]:
                if current_state not in states:
                    states.append(current_state)
                self.cerraduraEpsilon(current_state, trans, states)
        return states

    #Mover devuelve los estados a los que puedo ir de un conjunto de estados con un caracter
    def mover(self, states, caracter, trans):
        moved_states = []
        for state in states:
            for k, v in trans.items():
                if k == state:
                    if len(v[caracter]) > 0:
                        for current_state in v[caracter]:
                            if current_state not in moved_states:
                                moved_states.append(current_state)
        return moved_states

    # Cerradurade epsilon S  es para estos devuelve los conjuntos con los que se puede ir con E de un conjunto de estados
    def cerraduraEpsilonS(self, all_states, trans):
        final_states = []
        for current_state in all_states:
            new_states = []
            new_states = self.cerraduraEpsilon(current_state, trans, [])
            final_states.append(new_states)

        final_states = [item for sublist in final_states for item in sublist]
        final_states = list(set(final_states))
        final_states.sort()
        return final_states     

    #Simulacion AFD
    def simulacionAFD(self, trans, cadena, final_char, alfabeto):
        #Se recorre y si hay una transicion para el estado actual se actualiza 
        current_state = "0"
        cadena = cadena.replace("E","")
        for char in cadena:
            if char not in alfabeto:
                return False
        if cadena != "":
            for char in cadena:
                llave = ""
                for key, v in trans.items():
                    if v["name"] == current_state and v[char] != None:
                        llave = key
                    elif v["name"] == current_state and v[char] == None:
                        return False
                current_state = trans[llave][char]
        #Se ve que caracteres estan en el estados final si se encuentra el # pertenece
        for key, v in trans.items():
            if v["name"] == current_state:
                states = key.replace("[","")
                states = states.replace("]","")
                states = states.replace(" ","")
                states = states.split(",")
                st = []
                for i in states:
                    i = i.replace("'",'')
                    st.append(i)
                if final_char in st:
                    return True
                else:
                    return False

# Pasa el arbol a un binary tree para poder usarlo mas facil
def build_tree(node, root=None):
        if root is None:
            root = BinaryTreeNode(ord(node.data))

        if node.left is not None and node.left.data is not None:
            root.left = BinaryTreeNode(ord(node.left.data))
            build_tree(node.left, root.left)

        if node.right is not None and node.right.data is not None:
            root.right = BinaryTreeNode(ord(node.right.data))
            build_tree(node.right, root.right)

        return root

def remove_cerr_pos(r):
    for c in range(0, len(r), 1):
        if r[c] == "+":
            subr = r[:c]
            postr = r[c+1:]
            contador = 0
            subs = ""
            i = len(subr) - 1
            while(i >= 0):
                if r[i] == ")":
                    contador += 1
                    if contador == 1:
                        i -= 1
                    else:
                        subs = r[i] +subs
                        i-=1

                elif r[i] =="(":
                    contador -= 1
                    if contador == 0 :
                        i=-1
                    else:
                        subs = r[i] + subs
                        i-=1
                else:
                    if contador != 0:
                        subs = r[i] +subs
                        i-=1
                    else:
                        subs = r[i]
                        i=-1
            if len(subs) == 1:
                return subr+"*"+subs+postr
            else:
                return subr+"*("+subs+")"+postr

def remove_nulo(r):
    for c in range(0, len(r), 1):
        if r[c] == "?":
            subr = r[:c]
            postr = r[c+1:]
            contador = 0
            subs = ""
            i = len(subr) -1
            while (i>=0):
                if r[i] == ")":
                    contador += 1
                    if contador == 1:
                        i -= 1
                    else:
                        subs = r[i] +subs
                        subr = subr[:-1]
                        i-=1

                elif r[i] =="(":
                    contador -= 1
                    if contador == 0 :
                        i=-1
                    else:
                        subs = r[i] + subs
                        subr = subr[:-1]
                        i-=1
                else:
                    if contador != 0:
                        subs = r[i] +subs
                        subr  = subr[:-1]
                        i-=1
                    else:
                        subs = r[i]
                        subr = subr[:-1]
                        i=-1
            if len(subs) == 1:
                subr = subr[:-2]
                return subr+"("+subs+"|E)"+postr
            else:
                subr = subr[:-2]
                return subr+"("+subs+"|E)"+postr

def check_parenthesis(r):
    contador = 0
    for char in r:
        if char == "(":
            contador += 1
        elif char == ")":
            contador -= 1
    
    if contador > 0:
        r = r + (")"*contador)
    return r
