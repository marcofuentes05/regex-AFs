from binarytree import Node
import graphviz

def anulable(state, data):
    if data[str(state.value)]["value"] == "|":
        data[str(state.value)]["anulable"] = data[str(state.left.value)]["anulable"] or data[str(state.right.value)]["anulable"]
    elif data[str(state.value)]["value"] == ".":
        data[str(state.value)]["anulable"] = data[str(state.left.value)]["anulable"] and data[str(state.right.value)]["anulable"]
    elif data[str(state.value)]["value"] == "*":
        data[str(state.value)]["anulable"] = True
    elif data[str(state.value)]["value"] == "?":
        data[str(state.value)]["anulable"] = True
    elif data[str(state.value)]["value"] == "+":
        data[str(state.value)]["anulable"] == False
    elif data[str(state.value)]["value"] == "E":
        data[str(state.value)]["anulable"] == True
    else:
        data[str(state.value)]["anulable"] = False

def first_position(state, data):
    if data[str(state.value)]["value"] == "|":
        data[str(state.value)]["first_position"] = [item for sublist in [data[str(state.left.value)]["first_position"], data[str(state.right.value)]["first_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == ".":
        if data[str(state.left.value)]["anulable"]:
            data[str(state.value)]["first_position"] = [item for sublist in [data[str(state.left.value)]["first_position"], data[str(state.right.value)]["first_position"]] for item in sublist]
        else:
            data[str(state.value)]["first_position"] = [item for sublist in [data[str(state.left.value)]["first_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == "*":
        data[str(state.value)]["first_position"] = [item for sublist in [data[str(state.left.value)]["first_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == "?":
        data[str(state.value)]["first_position"] = [item for sublist in [data[str(state.left.value)]["first_position"], data[str(state.right.value)]["first_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == "+":
        data[str(state.value)]["first_position"] = [item for sublist in [data[str(state.left.value)]["first_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == "E":
        data[str(state.value)]["first_position"] = []
    else:
        data[str(state.value)]["first_position"] = [state.value]

def last_position(state, data):
    if data[str(state.value)]["value"] == "|":
        data[str(state.value)]["last_position"] = [item for sublist in [data[str(state.left.value)]["last_position"], data[str(state.right.value)]["last_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == ".":
        if data[str(state.right.value)]["anulable"]:
            data[str(state.value)]["last_position"] = [item for sublist in [data[str(state.left.value)]["last_position"], data[str(state.right.value)]["last_position"]] for item in sublist]
        else:
            data[str(state.value)]["last_position"] = [item for sublist in [data[str(state.right.value)]["last_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == "*":
        data[str(state.value)]["last_position"] = [item for sublist in [data[str(state.left.value)]["last_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == "?":
        data[str(state.value)]["last_position"] = [item for sublist in [data[str(state.left.value)]["last_position"], data[str(state.right.value)]["last_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == "+":
        data[str(state.value)]["last_position"] = [item for sublist in [data[str(state.left.value)]["last_position"]] for item in sublist]
    elif data[str(state.value)]["value"] == "E":
        data[str(state.value)]["last_position"] = []
    else:
        data[str(state.value)]["last_position"] = [state.value]

def next_position(state, data):
    if data[str(state.value)]["value"] == ".":
        for left_last in data[str(state.left.value)]["last_position"]:
            for right_first in data[str(state.right.value)]["first_position"]:
                if right_first not in data[str(state.left.value)]["next_position"]:
                    data[str(left_last)]["next_position"].append(right_first)
    elif data[str(state.value)]["value"] == "*":
        for left_last in data[str(state.left.value)]["last_position"]:
            for right_first in data[str(state.left.value)]["first_position"]:
                if right_first not in data[str(state.left.value)]["next_position"]:
                    data[str(left_last)]["next_position"].append(right_first)

def transitions(transitions, tree, data, alphabet):
    counter = 0
    transitions[str(data[str(tree.value)]["first_position"])] = {
        "name": "S{}".format(counter),
    }
    for character in alphabet:
        transitions[str(data[str(tree.value)]["first_position"])][character] = None
    counter += 1
    should_continue = True
    while(should_continue):
        initial_size = len(transitions)
        keys = list(transitions.keys())
        for key in keys:
            for character in alphabet:
                if transitions[key][character] == None:
                    new_state = []
                    state = key.replace("[","")
                    state = state.replace("]","")
                    state = state.replace(" ","")
                    state = state.split(",")
                    for item in state:
                        if data[str(item)]["value"] == character:
                            new_state.append(data[str(item)]["next_position"])
                    new_state = [item for sublist in new_state for item in sublist]
                    new_state = list(set(new_state))
                    new_state.sort()
                    if len(new_state) > 0:
                        if str(new_state) not in transitions:
                            transitions[str(new_state)] = {
                                "name": "S{}".format(counter)
                            }
                            for letter in alphabet:
                                transitions[str(new_state)][letter] = None
                            counter +=1
                            transitions[key][character] = transitions[str(new_state)]["name"]
                        else:
                            transitions[key][character] = transitions[str(new_state)]["name"]
        final_size = len(transitions)
        if initial_size == final_size:
            should_continue = not all(transitions.values())

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
