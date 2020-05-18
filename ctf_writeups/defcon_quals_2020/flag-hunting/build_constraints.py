from tree import *
from recordtype import recordtype

Instruction = recordtype('Instruction',['addr','op','operand', 'call_tgt'])


NEW_ROUND_ADDR = "ca5ab312e8886c46a899368f61547e0b" # The call to beta_check in check lvl 2
LEFT_BRANCH = "9fd18c435279a11cc106c4933676a7d9" # left branch
RIGHT_BRANCH = "a2648a849526903f1553126aa4119b79" #right branch
EQUAL_BRANCH = "b39fabb14ca48dfa222944f6b24fff4b"
NEW_VAL_ADDR = "7e8d3d12f9987acc83634394bb225179" # Malloc new node

WOMBAT_ADDR = "eeef3e11294110f840d4fc0a1273c089"
UNICORN_ADDR = "57c4fb55862a54ce50f667af48b390e7"

USEFUL_ADDRS_WITH_ROT = {
    NEW_VAL_ADDR: 'n',
    LEFT_BRANCH: 'l',
    RIGHT_BRANCH: 'r',
    EQUAL_BRANCH: 'e',
    WOMBAT_ADDR: "w",
    UNICORN_ADDR: "u"
}


# Given a single line in the trace, covert to the Instruction named tuple
def parse_inst(l):
    vals = l.split()
    addr = vals[0]
    op = vals[1]
    if(len(vals) > 2):
        # I apologize for the following line of code
        operands = tuple(" ".join(vals[2:]).split(","))
    else:
        operands = tuple()
    i = Instruction(addr, op, operands, [])
    return i


# Read the file, and only load the addrs that we care about
def load_trace():
    whole_trace = []
    with open("trace.txt", "r") as f:
        file_contents = f.read()
    for l in file_contents.splitlines():
        inst = parse_inst(l)
        if inst.addr in USEFUL_ADDRS_WITH_ROT:
            whole_trace += [inst.addr]
    return whole_trace


def get_build_string(trace):
    res = []
    temp = ""
    index = 0
    getting_final_rot = False
    while index < len(trace):
        addr = trace[index]
        new_let = USEFUL_ADDRS_WITH_ROT[addr]
        if getting_final_rot:
            if new_let in "uw":
                temp += new_let
                index += 1
            else:
                res += [temp]
                temp = ""
                getting_final_rot = False
        else:
            temp += new_let
            index += 1
            if new_let in "ne":
                getting_final_rot = True
    return res


def split_out_rots(string):
    tree = ""
    rots = ""
    for l in string:
        if l in "uw":
            rots += l
        else:
            tree += l
    return tree, rots


def build_tree(build_string_list):
    tree = None
    index = 0
    for chunk in build_string_list:
        reset_rots()
        to_send, expected_rots = split_out_rots(chunk)
        tree = insert(tree, to_send, index)
        print(build_structure_string(tree))
        rots_done = get_rots()
        if rots_done != "" or expected_rots != "":
            print("rotation check", rots_done, expected_rots)
        assert rots_done == expected_rots
        index += 1
    return tree


def main():
    trace = load_trace()
    build_string_list = get_build_string(trace)
    print(build_string_list)
    tree = build_tree(build_string_list)


if __name__ == "__main__":
    main()
