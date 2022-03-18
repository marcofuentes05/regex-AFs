import graphviz
import json

def anulable(node, data):
    if data[str(node.value)]["value"] == "|":
        data[str(node.value)]["anulable"] = data[str(node.left.value)]["anulable"] or data[str(node.right.value)]["anulable"]
    elif data[str(node.value)]["value"] == ".":
        data[str(node.value)]["anulable"] = data[str(node.left.value)]["anulable"] and data[str(node.right.value)]["anulable"]
    elif data[str(node.value)]["value"] == "*":
        data[str(node.value)]["anulable"] = True
    elif data[str(node.value)]["value"] == "?":
        data[str(node.value)]["anulable"] = True
    elif data[str(node.value)]["value"] == "+":
        data[str(node.value)]["anulable"] == False
    elif data[str(node.value)]["value"] == "E":
        data[str(node.value)]["anulable"] == True
    else:
        data[str(node.value)]["anulable"] = False

def first_position(node, data):
    if data[str(node.value)]["value"] == "|":
        data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == ".":
        if data[str(node.left.value)]["anulable"]:
            data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
        else:
            data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == "*":
        data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == "?":
        data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"], data[str(node.right.value)]["primera_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == "+":
        data[str(node.value)]["primera_pos"] = [item for sublist in [data[str(node.left.value)]["primera_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == "E":
        data[str(node.value)]["primera_pos"] = []
    else:
        data[str(node.value)]["primera_pos"] = [node.value]

def last_position(node, data):
    if data[str(node.value)]["value"] == "|":
        data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == ".":
        if data[str(node.right.value)]["anulable"]:
            data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
        else:
            data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.right.value)]["ultima_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == "*":
        data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == "?":
        data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"], data[str(node.right.value)]["ultima_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == "+":
        data[str(node.value)]["ultima_pos"] = [item for sublist in [data[str(node.left.value)]["ultima_pos"]] for item in sublist]
    elif data[str(node.value)]["value"] == "E":
        data[str(node.value)]["ultima_pos"] = []
    else:
        data[str(node.value)]["ultima_pos"] = [node.value]

def next_position(node, data):
    if data[str(node.value)]["value"] == ".":
        for up in data[str(node.left.value)]["ultima_pos"]:
            for pp in data[str(node.right.value)]["primera_pos"]:
                if pp not in data[str(node.left.value)]["siguiente_pos"]:
                    data[str(up)]["siguiente_pos"].append(pp)
    elif data[str(node.value)]["value"] == "*":
        for up in data[str(node.left.value)]["ultima_pos"]:
            for pp in data[str(node.left.value)]["primera_pos"]:
                if pp not in data[str(node.left.value)]["siguiente_pos"]:
                    data[str(up)]["siguiente_pos"].append(pp)

def get_transitions(trans, tree, data, alfabeto):
    contador = 0
    trans[str(data[str(tree.value)]["primera_pos"])] = {
        "name": "S"+str(contador),
    }
    for letra in alfabeto:
        trans[str(data[str(tree.value)]["primera_pos"])][letra] = None
    contador += 1
    cont = True
    while(cont):
        initial_size = len(trans)
        keys = list(trans.keys())
        for key in keys:
            for letra in alfabeto:
                if trans[key][letra] == None:
                    new_state = []
                    state = key.replace("[","")
                    state = state.replace("]","")
                    state = state.replace(" ","")
                    state = state.split(",")
                    for i in state:
                        if data[str(i)]["value"] == letra:
                            new_state.append(data[str(i)]["siguiente_pos"])
                    new_state = [item for sublist in new_state for item in sublist]
                    new_state = list(set(new_state))
                    new_state.sort()
                    if len(new_state) > 0:
                        if str(new_state) not in trans:
                            trans[str(new_state)] = {
                                "name": "S"+str(contador)
                            }
                            for letter in alfabeto:
                                trans[str(new_state)][letter] = None
                            contador +=1
                            trans[key][letra] = trans[str(new_state)]["name"]
                        else:
                            trans[key][letra] = trans[str(new_state)]["name"]
        final_size = len(trans)
        if initial_size == final_size:
            cont = not all(trans.values())

# Simula AFD para metodo directo
def AFD_sym_direct(transitions, cadena, final_char, alphabet, tree):
    dot = graphviz.Digraph(comment="AFD", format='png')
    dot.attr(rankdir="LR")

    for key in transitions.keys():
        states = key.replace("[","")
        states = states.replace("]","")
        states = states.replace(" ","")
        states = states.split(",")
        if str(tree.right.value) in states:
            dot.node(transitions[key]["name"], transitions[key]["name"], shape='doublecircle')
        else:
            dot.node(transitions[key]["name"], transitions[key]["name"])
    for key, v in transitions.items():
        for c in alphabet:
            if v["name"] != None and v[c] != None:
                dot.edge(v["name"], v[c], c)
    dot.render(directory='tmp', filename='AFD-direct')
    current_state = "S0"
    for char in cadena:
        llave = ""
        for key, v in transitions.items():
            if v["name"] == current_state and v[char] != None:
                print(char,current_state, v[char])
                llave = key
            elif v["name"] == current_state and v[char] == None:
                return False
        current_state = transitions[llave][char]
    for key, v in transitions.items():
        if v["name"] == current_state:
            states = key.replace("[","")
            states = states.replace("]","")
            states = states.replace(" ","")
            states = states.split(",")
            if final_char in states:
                return True
            else:
                return False

# Simular el AFD producido por subconjuntos
def AFD_sym_subsets(trans, string, final_char):
    current_state = "0"
    for char in string:
        llave = ""
        for key, value in trans.items():
            if value["name"] == current_state and value[char] != None:
                llave = key
            elif value["name"] == current_state and value[char] == None:
                return False
        current_state = trans[llave][char]
    for key, value in trans.items():
        if value["name"] == current_state:
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

def thompson(tree, data, alfabeto, trans):
    contador = 1 
    for nodo in tree.postorder:
        if data[str(nodo.value)]["value"] == "|":
            data[str(nodo.value)]["initial_state"] = "S"+str(contador)
            contador += 1
            data[str(nodo.value)]["final_state"] = "S"+str(contador)
            contador += 1
        elif data[str(nodo.value)]["value"] == ".":
            data[str(nodo.right.value)]["initial_state"] = data[str(nodo.left.value)]["final_state"] 
            data[str(nodo.value)]["initial_state"] = data[str(nodo.left.value)]["initial_state"]
            data[str(nodo.value)]["final_state"] = data[str(nodo.right.value)]["final_state"]
        elif data[str(nodo.value)]["value"] == "*":
            data[str(nodo.value)]["initial_state"] = "S"+str(contador)
            contador += 1
            data[str(nodo.value)]["final_state"] = "S"+str(contador)
            contador += 1
        else:
            data[str(nodo.value)]["initial_state"] = "S"+str(contador)
            contador += 1
            data[str(nodo.value)]["final_state"] = "S"+str(contador)
            contador += 1
    
    s0 = {
        "initial_state": "S0",
        "final_state": "S1"
    }
    dot = graphviz.Digraph(comment="AFN", format='png')
    dot.attr(rankdir="LR")

    for i in range(contador):
        trans["S"+str(i)]={}
        for letra in alfabeto:
            trans["S"+str(i)][letra] = []

    for nodo in tree.postorder:
        if data[str(nodo.value)]["value"] == "|":
            if data[str(nodo.left.value)]["initial_state"] == s0["final_state"]:
                s0["final_state"] = data[str(nodo.value)]["initial_state"]
            dot.node(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["initial_state"])
            dot.node(data[str(nodo.left.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"])
            dot.node(data[str(nodo.right.value)]["initial_state"], data[str(nodo.right.value)]["initial_state"])
            dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"], label="\u03B5")
            trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])

            dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.right.value)]["initial_state"], label="\u03B5")
            trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.right.value)]["initial_state"])

            if data[str(nodo.value)]["final_state"] == "S"+str(contador-1):
                dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='doublecircle')
            else:
                dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"])
            dot.node(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["final_state"])
            dot.node(data[str(nodo.right.value)]["final_state"], data[str(nodo.right.value)]["final_state"])
            dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.value)]["final_state"], label="\u03B5")
            trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])

            dot.edge(data[str(nodo.right.value)]["final_state"], data[str(nodo.value)]["final_state"], label="\u03B5")
            trans[data[str(nodo.right.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])
        elif data[str(nodo.value)]["value"] == "*":
            if data[str(nodo.left.value)]["initial_state"] == s0["final_state"]:
                s0["final_state"] = data[str(nodo.value)]["initial_state"]
            dot.node(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["initial_state"])
            dot.node(data[str(nodo.left.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"])
            dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"], label="\u03B5")
            trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])

            if data[str(nodo.value)]["final_state"] == "S"+str(contador-1):
                dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='doublecircle')
            else:
                dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"])
            dot.node(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["final_state"])
            dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.value)]["final_state"], label="\u03B5")
            trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])

            dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["final_state"], label="\u03B5")
            trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.value)]["final_state"])

            dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["initial_state"], label="\u03B5")
            trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])
        elif data[str(nodo.value)]["value"] == ".":
            print()
        else:
            dot.node(str(data[str(nodo.value)]["initial_state"]),data[str(nodo.value)]["initial_state"])
            if str(data[str(nodo.value)]["final_state"]) == "S"+str(contador-1):
                dot.node(str(data[str(nodo.value)]["final_state"]), data[str(nodo.value)]["final_state"], shape='doublecircle')
            else:
                dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"])
            dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["final_state"], label=data[str(nodo.value)]["value"])
            trans[data[str(nodo.value)]["initial_state"]][data[str(nodo.value)]["value"]].append(data[str(nodo.value)]["final_state"])

    dot.node(s0["initial_state"], s0["initial_state"])
    dot.edge(s0["initial_state"], s0["final_state"], label="\u03B5")
    trans[s0["initial_state"]]["E"].append(s0["final_state"])

    dot.render(directory='tmp', filename='AFN-thompson')
    tree.total_number_states = contador
    return contador

def e_closure(tree, state, trans, states = []):
    if state not in states:
        states.append(state)
    if (len(trans[state]["E"]) > 0):
        for st in trans[state]["E"]:
            if st not in states:
                states.append(st)
            e_closure(tree, st, trans, states)
    return states

def move(states, caracter, trans):
    moved_states = []
    for state in states:
        for k, v in trans.items():
            if k == state:
                if len(v[caracter]) > 0:
                    for st in v[caracter]:
                        if st not in moved_states:
                            moved_states.append(st)
    return moved_states

def e_closure_S(tree, all_states, trans):
    final_states = []
    for st in all_states:
        new_states = []
        new_states = e_closure(tree, st, trans, [])
        final_states.append(new_states)

    final_states = [item for sublist in final_states for item in sublist]
    final_states = list(set(final_states))
    final_states.sort()
    return final_states     

# Simular el AFN producido por el metodo de Thompson
def AFN_sym(tree, cadena, trans):
    states = e_closure(tree, "S0", trans, [])
    contador = 1
    cadena += "H"
    c = cadena[0]
    while c != "H":
        states = e_closure_S(tree, move(states, c, trans), trans)
        c = cadena[contador]
        contador += 1
    if tree.total_number_states in states:
        return True
    else:
        return False

def subsets(tree, transitions, data, abc):
    counter = 0
    abc.remove("E")
    closure = e_closure(tree, "S0", transitions, [])
    closure.sort()
    data[str(closure)] = {
        "name": str(counter),
    }
    for character in abc:
        data[str(closure)][character] = None
    counter += 1
    should_continue = True
    while(should_continue):
        initial_size = len(data)
        keys = list(data.keys())
        for key in keys:
            for character in abc:
                if data[key][character] == None:
                    new_state = []
                    st = key.replace('[','')
                    st = st.replace(']','')
                    st = st.replace(' ','')
                    st = st.split(',')
                    state = []
                    for i in st:
                        i = i.replace("'",'')
                        state.append(i)
                    new_state = e_closure_S(tree, move(state, character, transitions), transitions)
                    if len(new_state) > 0:
                        if str(new_state) not in data:
                            data[str(new_state)] = {
                                "name": str(counter)
                            }
                            for letter in abc:
                                data[str(new_state)][letter] = None
                            counter +=1
                            data[key][character] = data[str(new_state)]["name"]
                        else:
                            data[key][character] = data[str(new_state)]["name"]
        final_size = len(data)
        if initial_size == final_size:
            should_continue = not all(data.values())
    dot = graphviz.Digraph(comment="AFD", format='png')
    dot.attr(rankdir="LR")

    for key in data.keys():
        states = key.replace("[","")
        states = states.replace("]","")
        states = states.replace(" ","")
        states = states.split(",")
        st = []
        for i in states:
            i = i.replace("'",'')
            st.append(i)
        if ("S"+str(tree.total_number_states-1)) in st:
            dot.node(data[key]["name"], data[key]["name"], shape='doublecircle')
        else:
            dot.node(data[key]["name"], data[key]["name"])
            

    for key, v in data.items():
        for c in abc:
            if v["name"] != None and v[c] != None:
                states = key.replace("[","")
                states = states.replace("]","")
                states = states.replace(" ","")
                states = states.split(",")
                print('estados: ',states)
                if ("S"+str(tree.total_number_states-1)) in states:
                    dot.node(v["name"], v["name"],  shape='doublecircle')
                else:
                    dot.node(v["name"], v["name"])
                dot.node(v[c], v[c])
                dot.edge(v["name"], v[c], c)
    dot.render(directory='tmp', filename='AFD-subsets')
    return data