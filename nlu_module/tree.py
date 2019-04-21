class Tree:
    def __init__(self, pos_tag="ROOT", children=None, value=""):
        self.pos_tag = pos_tag
        self.children = []
        self.value = value
        if children is not None:
            for child in children:
                self.add_child(child)

    def add_child(self, child):
        self.children.append(child)
    

    def set_children(self, children):
        self.children = []
        for child in children:
            self.add_child(child)
    
    def get_children(self):
        return self.children

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def __repr__(self):
        return "\npos_tag " + self.pos_tag + "\tvalue " + self.value + "\tchildren "+str(self.children)

    def __eq__(self, other):
        if not isinstance(other, Tree):
            return NotImplemented
        
        return self.value == other.value and self.pos_tag == other.pos_tag;


    def __hash__(self):
        return hash((self.pos_tag, self.value))

