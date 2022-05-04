from binarytree import Node as BinaryTreeNode
import graphviz
import re as regex
from .direct import *
class Node:
    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right

    @staticmethod
    def convert_to_binary_tree(parent_node, binary_tree_parent=None):
        if binary_tree_parent is None:
            binary_tree_parent = BinaryTreeNode(ord(parent_node.data))

        if parent_node.left is not None and parent_node.left.data is not None:
            binary_tree_parent.left = BinaryTreeNode(ord(parent_node.left.data))
            Node.convert_to_binary_tree(parent_node.left, binary_tree_parent.left)

        if parent_node.right is not None and parent_node.right.data is not None:
            binary_tree_parent.right = BinaryTreeNode(ord(parent_node.right.data))
            Node.convert_to_binary_tree(parent_node.right, binary_tree_parent.right)

        return binary_tree_parent


class Tree:
    def __init__(self, initial_regular_expression):
        self.current_node_head = None
        self.temp_roots = []
        self.get_nodes(initial_regular_expression, None)

    def get_tree(self):
        return Node.convert_to_binary_tree(self.current_node_head)

    def add_node(self, temp_root_index, content, left, right, use_head_for):
        if temp_root_index is None:
            self.current_node_head = Node(content, left, right) if self.current_node_head is None else (Node(content, self.current_node_head, right) if use_head_for == 'l' else Node(content, left, self.current_node_head))
        else:
            if temp_root_index == len(self.temp_roots):
                self.temp_roots.append(Node(content, left, right))
            elif temp_root_index < len(self.temp_roots):
                self.temp_roots[temp_root_index] = Node(content, left, right) if self.temp_roots[temp_root_index] is None else (Node(content, self.temp_roots[temp_root_index], right) if use_head_for == 'l' else Node(content, left, self.temp_roots[temp_root_index]))

    @staticmethod
    def get_final_of_expression(partial_expression):
        i = 0
        while i < len(partial_expression):
            if partial_expression[i] == '«':
                parentheses_counter = 1
                for j in range(i+1, len(partial_expression)):
                    if partial_expression[j] in ['«', '»']: parentheses_counter = parentheses_counter + 1 if partial_expression[j] == '«' else parentheses_counter - 1

                    if parentheses_counter == 0 and partial_expression[j] == '»':
                        extra = 2 if j + 1 < len(partial_expression) and partial_expression[j+1] in ['±', '+', '?'] else 0
                        fin = j + extra
                        return fin

            elif regex.match(r'[a-zA-Z±"\'/*=.|()[\]{} ]', partial_expression[i]):
                fin = i
                for j in range(i + 1, len(partial_expression)):
                    if not regex.match(r'[a-zA-Z±"\'/*=.|()[\]{} ]', partial_expression[j]): break
                    fin = j
                return fin
            i += 1


    def get_nodes(self, partial_expression, temp_root_index):
        i = 0
        while i < len(partial_expression):
            if partial_expression[i] == '«':
                if i == 0:
                    parentheses_counter = 1
                    for j in range(i+1, len(partial_expression)):
                        if partial_expression[j] in ['«', '»']: parentheses_counter = parentheses_counter + 1 if partial_expression[j] == '«' else parentheses_counter - 1

                        if parentheses_counter == 0:
                            extra = 2 if partial_expression[j] == '»' and j + 1 < len(partial_expression) and partial_expression[j+1] in ['±', '+', '?'] else 0
                            fin = j + extra
                            self.get_nodes(partial_expression[i+1:fin], temp_root_index)
                            i = j
                            break
                else:
                    if partial_expression[i-1] in ['»', '±', '+', '?'] or regex.match(r'[a-zA-Z"\'/*=.|()[\]{} ]', partial_expression[i-1]):
                        fin_sub_re = self.get_final_of_expression(partial_expression[i:])
                        fin = i + 1 + fin_sub_re
                        self.get_nodes(partial_expression[i:fin], len(self.temp_roots))

                        sub_tree_root = self.temp_roots.pop() if temp_root_index is None else self.temp_roots.pop(temp_root_index + 1)
                        if sub_tree_root is not None: self.add_node(temp_root_index, '.', None, sub_tree_root, 'l')
                        i = i + fin + 1

            elif regex.match(r'[a-zA-Z#"\'/*=.|()[\]{} ]', partial_expression[i]):
                if ((temp_root_index is None and self.current_node_head is None) or i == 0) and i + 1 < len(partial_expression) and regex.match(r'[a-zA-Z#"\'/*=.|()[\]{} ]', partial_expression[i+1]):
                    if i + 2 < len(partial_expression) and partial_expression[i+2] in ['±', '+', '?']:
                        self.add_node(temp_root_index, '.', Node(partial_expression[i]), Node(partial_expression[i+2], Node(partial_expression[i+1]), None), 'l')
                        i += 2
                    else:
                        self.add_node(temp_root_index, '.', Node(partial_expression[i]), Node(partial_expression[i+1]), 'l')
                        i += 1
                elif (temp_root_index is None and self.current_node_head is not None) or i != 0:
                    self.add_node(temp_root_index, '.', None, Node(partial_expression[i]), 'l')
                else:
                    self.add_node(temp_root_index, partial_expression[i], None, None, 'l')

                if i + 1 < len(partial_expression):
                    if partial_expression[i+1] in ['±', '+', '?']:
                        self.add_node(temp_root_index, partial_expression[i+1], Node(partial_expression[i]), None, 'l')
                    elif partial_expression[i+1] == '»':
                        if i + 2 < len(partial_expression) and partial_expression[i+2] in ['±', '+', '?']:
                            self.add_node(temp_root_index, partial_expression[i+2], Node(partial_expression[i]), None, 'l')

            elif partial_expression[i] in ['¦']:
                fin_sub_re = self.get_final_of_expression(partial_expression[i+1:])
                fin = i + 1 + fin_sub_re + 1
                self.get_nodes(partial_expression[i+1:fin], len(self.temp_roots))

                sub_tree_root = self.temp_roots.pop() if temp_root_index is None else self.temp_roots.pop(temp_root_index + 1)
                if sub_tree_root is not None: self.add_node(temp_root_index, partial_expression[i], Node(partial_expression[i-1]), sub_tree_root, 'l')

                if fin < len(partial_expression) and partial_expression[fin] == '»':
                    if fin + 1 < len(partial_expression) and partial_expression[fin+1] in ['±', '+', '?']:
                        self.add_node(temp_root_index, partial_expression[fin+1], Node(partial_expression[fin+1]), None, 'l')

                i = i + fin + 1
            else:
                pass
                # print('-', partial_expression[i])
            i += 1



# def convert_to_binary_tree(parent_node, binary_tree_parent=None):
#     if binary_tree_parent is None:
#         binary_tree_parent = Node(ord(parent_node.value))

#     if parent_node.left is not None and parent_node.left.value is not None:
#         binary_tree_parent.left = Node(ord(parent_node.left.value))
#         convert_to_binary_tree(parent_node.left, binary_tree_parent.left)

#     if parent_node.right is not None and parent_node.right.value is not None:
#         binary_tree_parent.right = Node(ord(parent_node.right.value))
#         convert_to_binary_tree(parent_node.right, binary_tree_parent.right)
#     return binary_tree_parent

# ABC = [letter for letter in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\u03B5#']
# # Clase para representar un nodo de un arbol binario
# class TreeNode:
#     def __init__(self, value, left=None, right=None):
#         self.value = value
#         # las hojas seran de tipo TreeNode (recursivo)
#         self.left = left
#         self.right = right

# # Clase para representar el arbol de analisis sintactico
# class Tree:
#     def __init__(self, regex):
#         self.root = None # TreeNode
#         self.siblings = []
#         self.initialize(regex, None)

#     def get_tree(self):
#         return convert_to_binary_tree(self.root)

#     def initialize(self, regex, parent):
#         regex_index_pointer = 0
#         while regex_index_pointer < len(regex):
#             if regex[regex_index_pointer] == '(':
#                 if regex_index_pointer == 0:
#                     num_total_parenthesis = 1
#                     for regex_inside_pointer in range(regex_index_pointer + 1, len(regex)):
#                         if regex[regex_inside_pointer] == '(':
#                             num_total_parenthesis += 1 
#                         elif regex[regex_inside_pointer] ==")":
#                             num_total_parenthesis -= 1 
#                         offset = 0
#                         if num_total_parenthesis == 0:
#                             if regex[regex_inside_pointer] == ')' and regex_inside_pointer+1 < len(regex) and regex[regex_inside_pointer + 1] in ['*' , '+', '?']:
#                                 offset += 2
#                             pointer_limit = regex_inside_pointer + offset
#                             pointer_start = regex_index_pointer + 1
#                             self.initialize(regex[pointer_start:pointer_limit], parent)
#                             regex_index_pointer = regex_inside_pointer
#                             break
#                 else:
#                     if regex[regex_index_pointer-1] in  [")", "*", "+", "?"] or regex[regex_index_pointer-1] in ABC:
#                         regular_sub_exp_pointer_limit = self.get_final_of_expression(regex[regex_index_pointer:])
#                         end = regex_index_pointer + regular_sub_exp_pointer_limit + 1
#                         self.initialize(regex[regex_index_pointer:end], len(self.siblings))

#                         if parent is None:
#                             sub_tree_root = self.siblings.pop()
#                         else:
#                             sub_tree_root = self.siblings.pop(parent + 1)
#                         if sub_tree_root is not None:
#                             self.add_node(parent, '.', None, sub_tree_root) # Por default lo agrega a la izquierda
#                         regex_index_pointer += 1 + end
#             elif regex[regex_index_pointer] in ABC:
#                 if ((parent is None and self.root is None) or regex_index_pointer == 0) and (regex_index_pointer + 1 < len(regex) and regex[regex_index_pointer+1] in ABC ):
#                     if (regex_index_pointer + 2 < len(regex) and regex[regex_index_pointer+2] in ['*', '+', '?']):
#                         self.add_node(parent,'/', TreeNode(regex[regex_index_pointer]), TreeNode(regex[regex_index_pointer+2], TreeNode(regex[regex_index_pointer+1]), None) )
#                         regex_index_pointer += 2
#                     else: 
#                         self.add_node(parent, '.', TreeNode(regex[regex_index_pointer]), TreeNode(regex[regex_index_pointer+1]))
#                         regex_index_pointer += 1
#                 elif(parent is None and self.root is not None) or regex_index_pointer != 0:
#                     self.add_node(parent, '.', None, TreeNode(regex[regex_index_pointer]))
#                 else:
#                     self.add_node(parent, regex[regex_index_pointer], None, None)
                
#                 if regex_index_pointer + 1 < len(regex):
#                     if regex[regex_index_pointer + 1] in ['*', '+', '?']:
#                         self.add_node(parent, regex[regex_index_pointer + 1], TreeNode(regex[regex_index_pointer]), None)
#                     elif regex[regex_index_pointer + 1] == ')':
#                         if regex_index_pointer + 2 < len(regex) and regex[regex_index_pointer + 2] in ['*', '+', '?']:
#                             self.add_node(parent, regex[regex_index_pointer + 2], TreeNode(regex[regex_index_pointer]), None)
#             elif regex[regex_index_pointer] == '|':
#                 regular_sub_exp_pointer_limit = self.get_final_of_expression(regex[regex_index_pointer+1:])
#                 end = regex_index_pointer + regular_sub_exp_pointer_limit + 1 + 1
#                 self.initialize(regex[regex_index_pointer+1:end], len(self.siblings))
#                 new_temp_root = None
#                 if parent is None:
#                     new_temp_root = self.siblings.pop()
#                 else:
#                     new_temp_root = self.siblings.pop(parent + 1)
#                 if new_temp_root is not None:
#                     self.add_node(parent, regex[regex_index_pointer], TreeNode(regex[regex_index_pointer - 1]), new_temp_root)
                
#                 if end < len(regex) and regex[end] == ')':
#                     if end + 1 < len(regex) and regex[end + 1] in ['*', '+', '?']:
#                         self.add_node(parent, regex[end + 1], TreeNode(regex[end + 1]), None)
#                 regex_index_pointer += end + 1
#             else:
#                 pass
#             regex_index_pointer += 1

#     def add_node(self, parent_index, value, left, right):
#         if parent_index is None:
#             if self.root is None:
#                 self.root = TreeNode(value, left, right)
#             else:
#                 self.root = TreeNode(value, self.root, right)
#         else:
#             if parent_index == len(self.siblings):
#                 self.siblings.append(TreeNode(value, left, right))
#             elif parent_index < len(self.siblings):
#                 if self.siblings[parent_index] is None:
#                     self.siblings[parent_index] = TreeNode(value, left, right)
#                 else:
#                     self.siblings[parent_index] = TreeNode(value, self.siblings[parent_index], right)
    
#     def get_final_of_expression(self, regex):
#         pointer = 0
#         while pointer < len(regex):
#             if regex[pointer] == '(':
#                 num_total_parenthesis = 1
#                 for regex_inside_pointer in range(pointer + 1, len(regex)):
#                     if regex[regex_inside_pointer] == '(':
#                         num_total_parenthesis += 1
#                     elif regex[regex_inside_pointer] == ')':
#                         num_total_parenthesis -= 1
                    
#                     offset = 0
#                     if num_total_parenthesis == 0 and regex[regex_inside_pointer] == ')':
#                         if regex_inside_pointer+1 < len(regex) and regex[regex_inside_pointer + 1] in ['*' , '+', '?']:
#                             offset = 2
#                         return regex_inside_pointer + offset
#             elif regex[pointer] in ABC or regex[pointer] == '*':
#                 end = pointer
#                 for regex_inside_pointer in range(pointer + 1, len(regex)):
#                     if not (regex[regex_inside_pointer] in ABC or regex[regex_inside_pointer] == '*'):
#                         break
#                     end = regex_inside_pointer
#                 return end
#             pointer += 1

#     # Simula el AFD pruducido por los subconjuntos
#     def AFD_sym_subsets(self, trans, cadena, final_char):
#         actual_state = "0"
#         for character in cadena:
#             original_key = ""
#             for index, value in trans.items():
#                 if value["name"] == actual_state and value[character] != None:
#                     original_key = index
#                 elif value["name"] == actual_state and value[character] == None:
#                     return False
#             actual_state = trans[original_key][character]
#         for index, value in trans.items():
#             if value["name"] == actual_state:
#                 states = index.replace("[","")
#                 states = states.replace("]","")
#                 states = states.replace(" ","")
#                 states = states.split(",")
#                 st = []
#                 for i in states:
#                     i = i.replace("'",'')
#                     st.append(i)
#                 if final_char in st:
#                     return True
#                 else:
#                     return False

#     def thompson(self, tree, data, alfabeto, trans):
#         contador = 1 
#         for nodo in tree.postorder:
#             if data[str(nodo.value)]["value"] == "|":
#                 data[str(nodo.value)]["initial_state"] = "S{}".format(contador)
#                 contador += 1
#                 data[str(nodo.value)]["final_state"] = "S{}".format(contador)
#                 contador += 1
#             elif data[str(nodo.value)]["value"] == ".":
#                 data[str(nodo.right.value)]["initial_state"] = data[str(nodo.left.value)]["final_state"] 
#                 data[str(nodo.value)]["initial_state"] = data[str(nodo.left.value)]["initial_state"]
#                 data[str(nodo.value)]["final_state"] = data[str(nodo.right.value)]["final_state"]
#             elif data[str(nodo.value)]["value"] == "*":
#                 data[str(nodo.value)]["initial_state"] = "S{}".format(contador)
#                 contador += 1
#                 data[str(nodo.value)]["final_state"] = "S{}".format(contador)
#                 contador += 1
#             else:
#                 data[str(nodo.value)]["initial_state"] = "S{}".format(contador)
#                 contador += 1
#                 data[str(nodo.value)]["final_state"] = "S{}".format(contador)
#                 contador += 1
        
#         s0 = {
#             "initial_state": "S0",
#             "final_state": "S1"
#         }
#         dot = graphviz.Digraph(comment="AFN", format='png')
#         dot.attr(rankdir="LR")

#         for i in range(contador):
#             trans["S{}".format(i)]={}
#             for letra in alfabeto:
#                 trans["S{}".format(i)][letra] = []

#         for nodo in tree.postorder:
#             if data[str(nodo.value)]["value"] == "|":
#                 if data[str(nodo.left.value)]["initial_state"] == s0["final_state"]:
#                     s0["final_state"] = data[str(nodo.value)]["initial_state"]
#                 dot.node(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["initial_state"])
#                 dot.node(data[str(nodo.left.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"])
#                 dot.node(data[str(nodo.right.value)]["initial_state"], data[str(nodo.right.value)]["initial_state"])
#                 dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"], label="\u03B5")
#                 trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])

#                 dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.right.value)]["initial_state"], label="\u03B5")
#                 trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.right.value)]["initial_state"])

#                 if data[str(nodo.value)]["final_state"] == "S{}".format(contador-1):
#                     dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='doublecircle')
#                 else:
#                     dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"])
#                 dot.node(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["final_state"])
#                 dot.node(data[str(nodo.right.value)]["final_state"], data[str(nodo.right.value)]["final_state"])
#                 dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.value)]["final_state"], label="\u03B5")
#                 trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])

#                 dot.edge(data[str(nodo.right.value)]["final_state"], data[str(nodo.value)]["final_state"], label="\u03B5")
#                 trans[data[str(nodo.right.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])
#             elif data[str(nodo.value)]["value"] == "*":
#                 if data[str(nodo.left.value)]["initial_state"] == s0["final_state"]:
#                     s0["final_state"] = data[str(nodo.value)]["initial_state"]
#                 dot.node(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["initial_state"])
#                 dot.node(data[str(nodo.left.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"])
#                 dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.left.value)]["initial_state"], label="\u03B5")
#                 trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])

#                 if data[str(nodo.value)]["final_state"] == "S{}".format(contador-1):
#                     dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"], shape='doublecircle')
#                 else:
#                     dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"])
#                 dot.node(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["final_state"])
#                 dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.value)]["final_state"], label="\u03B5")
#                 trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.value)]["final_state"])

#                 dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["final_state"], label="\u03B5")
#                 trans[data[str(nodo.value)]["initial_state"]]["E"].append(data[str(nodo.value)]["final_state"])

#                 dot.edge(data[str(nodo.left.value)]["final_state"], data[str(nodo.left.value)]["initial_state"], label="\u03B5")
#                 trans[data[str(nodo.left.value)]["final_state"]]["E"].append(data[str(nodo.left.value)]["initial_state"])
#             elif data[str(nodo.value)]["value"] == ".":
#                 pass
#             else:
#                 dot.node(str(data[str(nodo.value)]["initial_state"]),data[str(nodo.value)]["initial_state"])
#                 if str(data[str(nodo.value)]["final_state"]) == "S{}".format(contador-1):
#                     dot.node(str(data[str(nodo.value)]["final_state"]), data[str(nodo.value)]["final_state"], shape='doublecircle')
#                 else:
#                     dot.node(data[str(nodo.value)]["final_state"], data[str(nodo.value)]["final_state"])
#                 dot.edge(data[str(nodo.value)]["initial_state"], data[str(nodo.value)]["final_state"], label=data[str(nodo.value)]["value"])
#                 trans[data[str(nodo.value)]["initial_state"]][data[str(nodo.value)]["value"]].append(data[str(nodo.value)]["final_state"])

#         dot.node(s0["initial_state"], s0["initial_state"])
#         dot.edge(s0["initial_state"], s0["final_state"], label="\u03B5")
#         trans[s0["initial_state"]]["E"].append(s0["final_state"])

#         dot.render(directory='tmp', filename='AFN-thompson')
#         self.total_number_states = contador
#         return contador

#     def e_closure(self, state, trans, states = []):
#         if state not in states:
#             states.append(state)
#         if (len(trans[state]["E"]) > 0):
#             for st in trans[state]["E"]:
#                 if st not in states:
#                     states.append(st)
#                 self.e_closure(st, trans, states)
#         return states

#     def move(self, states, caracter, trans):
#         moved_states = []
#         for state in states:
#             for k, v in trans.items():
#                 if k == state:
#                     if len(v[caracter]) > 0:
#                         for st in v[caracter]:
#                             if st not in moved_states:
#                                 moved_states.append(st)
#         return moved_states

#     def e_closure_S(self, all_states, trans):
#         final_states = []
#         for st in all_states:
#             new_states = []
#             new_states = self.e_closure(st, trans, [])
#             final_states.append(new_states)

#         final_states = [item for sublist in final_states for item in sublist]
#         final_states = list(set(final_states))
#         final_states.sort()
#         return final_states     

#     # Simular el AFN
#     def AFN_sym(self, cadena, trans, final_state):
#         states = self.e_closure("S0", trans, [])
#         contador = 1
#         cadena += "H"
#         character = cadena[0]
#         while character != "H":
#             states = self.e_closure_S(self.move(states, character, trans), trans)
#             character = cadena[contador]
#             contador += 1
#         if final_state in states:
#             return True
#         else:
#             return False

#     def subsets(self, trans, data, abc):
#         counter = 0
#         abc.remove("E")
#         closure = self.e_closure("S0", trans, [])
#         closure.sort()
#         data[str(closure)] = {
#             "name": str(counter),
#         }
#         for character in abc:
#             data[str(closure)][character] = None
#         counter += 1
#         should_continue = True
#         while(should_continue):
#             initial_size = len(data)
#             keys = list(data.keys())
#             for key in keys:
#                 for character in abc:
#                     if data[key][character] == None:
#                         new_state = []
#                         st = key.replace('[','')
#                         st = st.replace(']','')
#                         st = st.replace(' ','')
#                         st = st.split(',')
#                         state = []
#                         for i in st:
#                             i = i.replace("'",'')
#                             state.append(i)
#                         new_state = self.e_closure_S(self.move(state, character, trans), trans)
#                         if len(new_state) > 0:
#                             if str(new_state) not in data:
#                                 data[str(new_state)] = {
#                                     "name": str(counter)
#                                 }
#                                 for letter in abc:
#                                     data[str(new_state)][letter] = None
#                                 counter +=1
#                                 data[key][character] = data[str(new_state)]["name"]
#                             else:
#                                 data[key][character] = data[str(new_state)]["name"]
#             final_size = len(data)
#             if initial_size == final_size:
#                 should_continue = not all(data.values())
#         return data
