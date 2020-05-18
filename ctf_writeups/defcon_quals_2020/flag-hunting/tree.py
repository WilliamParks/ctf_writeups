rots_done = ""

class Node:
    def __init__(self, index):
        self.left = None
        self.right = None
        self.height = 1
        self.count = 1
        self.indicies = [index]

def build_structure_string(node):
    res = ""
    if node is None:
        return "_"
    if node.left is not None:
        res += "l" + build_structure_string(node.left) + "b"
    res += "e" + "(" + ",".join(map(str, node.indicies)) + ")"
    if node.right is not None:
        res += "r" + build_structure_string(node.right) + "z"
    return res

# Trace is a character list of "rlen"s for where the new thing is. right/left/eq/new
def insert(node, trace, index):
    if node is None:
        assert trace[0] == "n"
        return Node(index)
    else:
        assert node is not None
        if trace == "e":
            update(node, index)
        else:
            assert trace[0] in "lr"
            if trace[0] == "l":
                node.left = insert(node.left, trace[1:], index)
            else:
                node.right = insert(node.right, trace[1:], index)
    t = first_rotation(node)
    return update_unicorn(t)


def update(node, index):
    node.count += 1
    node.indicies += [index]


def first_rotation(node):
    left_child = node.left
    if left_child is None:
        return node
    if left_child.height == node.height:
        global rots_done
        rots_done += 'w'
        lefts_childs_right_child = left_child.right
        node.left = lefts_childs_right_child
        left_child.right = node
        return left_child
    else:
        return node


def update_unicorn(node):
    right_child = node.right
    if right_child is None:
        return node
    if right_child.right is None:
        return node
    if right_child.right.height == node.height:
        global rots_done
        rots_done += 'u'
        a = node
        b = a.right
        c = b.right
        a.right = b.left
        b.left = node
        b.height += 1
        return b
    else:
        return node


def get_rots():
    global rots_done
    return rots_done


def reset_rots():
    global rots_done
    rots_done = ""
