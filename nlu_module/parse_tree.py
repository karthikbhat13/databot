from pycorenlp import StanfordCoreNLP
from tree import Tree
import re
from collections import defaultdict

def get_parse_tree(text):
	stanford_nlp = StanfordCoreNLP("http://localhost:9001")

	output = stanford_nlp.annotate(text, properties={
	'annotators': 'parse',
	'outputFormat': 'json'
	})


	str_parse_tree = output['sentences'][0]['parse']

	print(str_parse_tree)
	return str_parse_tree

def temp(text, ind):
	json = {}
	# print("function in")
	word = ''
	key = ''
	while(ind < len(text)):
		if(text[ind] == '('):
			# print("par"+ text[:ind+1])
			ind += 1
			word = ''
			while(text[ind] != ' '):
				word += text[ind]
				ind += 1
			# print(word)
			if(text[ind+1] == '('):
				if word not in json:
					json[word] = []
				# print(json)
				try:
					while(text[ind] == " "):
						temp_dic, ind = temp(text, ind+1)
						json[word].append(temp_dic)
				except(Exception):
					return json ,ind+1
				# print("return "+str(json))
				if(text[ind] == ")"):
					# print("if")
					return json, ind+2
			else:
				ind += 1
				key = ""
				# print("else" + str(json))
				while(text[ind] != ")"):
					key += text[ind]				
					ind += 1
				ind += 1
				json[word] = key
				return json, ind


def convert_str_json(text):
	text = text.replace("\n", "")
	text = re.sub(" +", " ", text)
	print(text)
	ind = text.index("(")+6
	print(len(text))
	print(ind)
	return temp(text, ind)

def convert_json_tree(json):
	for key, val in json.items():
		node = Tree(pos_tag=key)

		if(type(val) == type("")):
			node.value = val
			node.children = None
		elif(type(val) == type([])):
			for child in val:
				node.add_child(convert_json_tree(child))
		else:
			continue
	return node

def get_root_node(str_parse_tree):
	str_json = convert_str_json(str_parse_tree)[0]
	print(str_json)
	root = Tree()
	for key, value in str_json.items():
		temp_dic = {}
		temp_dic[key] = value
		root.add_child(convert_json_tree(temp_dic))
	return root


def get_child_name(node, name):
	node_children = node.get_children()
	
	if node_children is not None:
		for child in node_children:
			if(child.value == name):
				return node, name
			else:
				if get_child_name(child, name) != (False, False):
					return node, get_child_name(child, name)[1]
				else:
					continue
	return False, False

def get_child_pos(node, pos):
	node_children = node.get_children()
	
	if node_children is not None:
		for child in node_children:
			if(child.pos_tag == pos):
				return node, child.value
			else:
				if get_child_pos(child, pos) != (False, False):
					return get_child_pos(child, pos)
				else:
					continue
	return False, False

def get_parent_node(root, node):
	children = root.get_children()
	if(children is None):
		return False
	for child in children:
		if child == node:
			return root
		else:
			if(get_parent_node(child, node) != False):
				return child
	return False

def get_relation(str_parse_tree, column_name, pos):
	
	json = convert_str_json(str_parse_tree)[0]

	root = get_root_node(str_parse_tree)
	print(json)

	get_chunks(root)
	print(root)
	dec_children = root.get_children()

	for child in dec_children:
		node, val = get_child_name(child, column_name)
		if(node != False):
			
			rel_node, rel_val = get_child_pos(node, pos)
			if(rel_node != False):
				
				print(rel_node, rel_val)
				return rel_node, rel_val
			else:
				par_node = get_parent_node(root, node) if get_parent_node(root, node) == False else root 
				sib_node, sib_val = False, False
				for ch in par_node.get_children():
					if(get_child_pos(ch, pos) != (False, False)):
						sib_node, sib_val = get_child_pos(ch, pos)
						break
				if(sib_node != False):
					return sib_node, sib_val
				else:
					return False, False
	for child in dec_children:
		node, val = get_child_pos(child, pos)
		print(pos)
		if(node != False):
			return node, val
	return False, False

def check_exists(word, arr):
	for w in arr:
		if word == w or word.startswith(w):
			return True
	return False

def get_continuous_chunks_parse_tree(root):
	children = root.get_children()
	new_children = []
	
	if children is None:
		return root
	
	for ind in range(0, len(children)):
		child = children[ind]

		if child.get_children() is not None:
			new_children.append(child)
			# children.remove(child)
	if(len(children) == len(new_children)):
		root.set_children(new_children)
		return root
	for child in new_children:
		children.remove(child)
	cont_chunk = children[0]
	pre_chunk = cont_chunk.pos_tag

	for ind in range(1, len(children)):
		child = children[ind]
		
		cur_chunk = child.pos_tag
		print(cont_chunk)
		if(cur_chunk == pre_chunk):
			cont_chunk.value = cont_chunk.value +' '+ child.value
			ind += 1
		else:
			new_children.append(cont_chunk)
			pre_chunk = child.pos_tag
			cont_chunk = child
	if cont_chunk not in new_children:
		new_children.append(cont_chunk)

	root.set_children(new_children)
	
	return root

def get_chunks(root):
	root = get_continuous_chunks_parse_tree(root)
	root_children = root.get_children()
	new_children = []
	if root_children is None:
		return root
	for child in root_children:
		if child is not None:
			new_children.append(get_chunks(child))
	root.set_children(new_children)
	return root

if __name__ == "__main__":
	node, val = get_relation(get_parse_tree("Tom Hanks has acted"), 'acted', 'NNP')

	print(node, val)