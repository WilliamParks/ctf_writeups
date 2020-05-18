from recordtype import recordtype
from collections import OrderedDict

BLOCK_TYPES = ['jmp', 'ret', 'call', 'fin']

Instruction = recordtype('Instruction',['addr','op','operand', 'call_tgt'])
Basic_Block = recordtype('Basic_Block',['start_addr', 'children', 'parents', 'insts'])
Function = recordtype('Function', ['start_addr', 'xrefs_to', 'xrefs_from', 'insts'])
Func_With_Blocks = recordtype('Func_With_Blocks', ['start_addr', 'xrefs_to', 'xrefs_from', 'blocks'])


# Not 100% sure this is an exhaustive list
jmps = ['jns','jne','jae','jle','jge','js','jl','je','jg','ja','jb','jmp','jbe']
rets = ['ret', 'repz']
control_flow_change_insts = jmps + rets + ['call']

better_control_flow = jmps + rets

START_BLOCK_ADDR = "3cda655ffeabac454f0ddeffbd60f3f3"
END_BLOCK_ADDR = "6e177de8ac3e8da90e748e89466893cf"
FIRST_READ_ADDR = "29baf18c7ca50fee9bf3739553e1a68f"
LAST_ADDR = "a362bd3ec3fc3bd642d53573f6c99e85"

func_table = {"0x5555555546d0":"printf",
"0x5555555546b0":"fread",
"0x555555554700":"exit",
"0x5555555546f0":"fopen64",
"0x5555555546e0":"malloc",
}

def is_rip_rel_jmp(inst):
    if inst.op == "jmp":
        for w in inst.operand:
            if "rip" in w:
                return True

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


# Gets called functions as determined by Evan
def fix_calls(trace):
    for inst in trace:
        if inst.op == "call" and inst.operand[0] in func_table:
            inst.operand = [func_table[inst.operand[0]]]


# Read the file, and load it into a list of Instruction named tuples
def load_trace():
    whole_trace = []
    with open("trace.txt", "r") as f:
        file_contents = f.read()
    for l in file_contents.splitlines():
        whole_trace += [parse_inst(l)]
    return whole_trace


# Checks if the provided string represents an integer in the ascii range
def is_ascii_int(val):
    if val[:2] != "0x":
        return False
    i = int(val, 16)
    return i >= 0x20 and i <= 0x7f


# True if the provided instruction is a cmp against some sort of byte value
def is_byte_compare(inst):
    return inst.op == "cmp" and is_ascii_int(inst.operand[1])


def is_rip_modifying(inst):
    # Leave in libc calls
    if inst.op == "call" and inst.operand[0] in func_table.values():
        return False
    return inst.op in control_flow_change_insts


# Returns only unique instructions
def remove_duplicate_instructions(l):
    res = dict()
    for i in l:
        addr = i.addr
        res[addr] = i
    return res.values()


# Gets all comparisions against individual bytes
def get_all_byte_compares(trace):
    res = list()
    for i in trace:
        if is_byte_compare(i):
            res += [i]
    return remove_duplicate_instructions(res)


# Gets all ops in a list of instructions
def get_all_ops(trace):
    res = dict()
    for i in trace:
        res[i.op] = 1
    return list(res.keys())




# Removes everything up to the first read
def evans_read_heuristic(trace):
    first_read_addr = FIRST_READ_ADDR
    index = -1
    for i in range(len(trace)):
        if trace[i].addr == first_read_addr:
            index = i
            break
    assert index != -1
    return trace[index:]

# Function = recordtype('Function', ['start_addr', 'xrefs_to', 'xrefs_from', 'insts'])
# Builds a list of functions with start_addr, xrefs_to, xrefs_from and blocks set. Not deduplicated
def build_functions(trace, index):
    assert trace[len(trace) - 1].op in rets + ['syscall']
    start_inst = trace[index]
    start_addr = start_inst.addr
    max_length = len(trace)
    xrefs_from = []
    ret_funcs = []
    insts = []
    while index < max_length:
        insts += [trace[index]]
        curr_inst = trace[index]
        # Drop into new function if call
        if curr_inst.op == "call":
            new_funcs, new_index = build_functions(trace, index + 1)
            if curr_inst.operand[0] not in func_table.values():
                ret_funcs += new_funcs
                xrefs_from += [trace[index + 1].addr]
                curr_inst.call_tgt += [trace[index + 1].addr]
            index = new_index
        elif curr_inst.op in rets or curr_inst.addr == LAST_ADDR:
            assert insts[len(insts) - 1].op in rets or curr_inst.addr == LAST_ADDR
            new_func = Function(start_addr, set(), set(xrefs_from), [tuple(insts)])
            return ret_funcs + [new_func], index + 1
        else:
            index += 1
    return ret_funcs, index


# Combines multiple function calls in the trace into one instance
def dedup_funcs(funcs):
    res = dict()
    for f in funcs:
        if f.start_addr not in res:
            res[f.start_addr] = f
        else:
            res[f.start_addr].xrefs_from.update(f.xrefs_from)
            assert len(f.insts) == 1 and isinstance(f.insts, list) and isinstance(f.insts[0], tuple)
            res[f.start_addr].insts += f.insts
    return res


def build_xrefs_to(funcs):
    for func in funcs.values():
        xrefs_from = func.xrefs_from
        for xref in xrefs_from:
            called_func = funcs[xref]
            called_func.xrefs_to.update([func.start_addr])


# Wrapper around all of the function building functions
def build_all_funcs(lin_trace):
    funcs, _ = build_functions(lin_trace, 0)
    proced_funcs = dedup_funcs(funcs)
    build_xrefs_to(proced_funcs)
    return proced_funcs


# Takes in a list of instructions, returns a group of blocks
def build_blocks(inst_group, jmp_targets):
    blocks = []
    curr_block = []
    start_addr = inst_group[0].addr
    assert inst_group[len(inst_group)-1].op in rets or inst_group[len(inst_group)-1].addr == LAST_ADDR
    for i, inst in enumerate(inst_group):

        curr_addr = inst.addr
        if curr_addr in jmp_targets: # Hit end point
            last_inst = inst_group[i - 1]
            if last_inst.op in rets:
                child_addr = None
                child_list = []
            else:
                child_addr = curr_addr
                child_list = [child_addr]
            new_block = Basic_Block(start_addr, child_list, [], curr_block)
            start_addr = curr_addr
            blocks += [new_block]
            curr_block = []
        curr_block += [inst]
    inst = inst_group[-1]
    if len(curr_block) != 0:
        if inst.op in rets or inst.addr == LAST_ADDR:
            child_set = []
        else:
            assert True == False
            child_set = [child_addr]
        new_block = Basic_Block(start_addr, child_set, [], curr_block)
        blocks += [new_block]
    return blocks


def combine_blocks(blocks):
    res = OrderedDict()
    for block in blocks:
        addr = block.start_addr
        if addr not in res:
            res[addr] = block
        else:
            res[addr].children = res[addr].children + block.children
    return res


def is_rip_modifying_version_foo(inst):
    # Leave in libc calls
    return inst.op in better_control_flow


def extract_jump_targets(group):
    res = []
    for i, inst in enumerate(group):
        if is_rip_modifying_version_foo(inst) and i < len(group) - 1:
            print(i, group[i])
            res += [group[i+1].addr] # Add the next instruction hit
    return res


def process_func_blocks(funcs):
    new_funcs = OrderedDict()
    for func in funcs.values():

        # Need to build a list of all jmp targets
        jmp_targets = []
        for group in func.insts:
            jmp_targets += extract_jump_targets(group)
        jmp_targets = set(jmp_targets)

        target_chains = []
        for inst_group in func.insts:
            blocks = build_blocks(inst_group, jmp_targets)
            target_chains += blocks
        combined_targets = combine_blocks(target_chains)
        new_funcs[func.start_addr] = Func_With_Blocks(func.start_addr, func.xrefs_to, func.xrefs_from, combined_targets)
    return new_funcs


def stringify_inst(i):
    if len(i.call_tgt) != 0:
        assert len(i.call_tgt) == 1
        return "{} {} {} - at {}".format(i.addr, i.op, ", ".join(i.operand), i.call_tgt[0])
    else:
        return "{} {} {}".format(i.addr, i.op, ", ".join(i.operand))


def stringify_children(l, end = None):
    res = ""
    current = ""
    dump = ""
    count = 0
    for entry in l:
        dump += "'{}', ".format(entry)
        if entry == current:
            count += 1
        else:
            if current == "":
                count = 1
                current = entry
            else:
                res += " {} * {}, ".format(current, count)
                count = 1
                current = entry
    if count != 0:
        res += " {} * {}, ".format(current, count)

    #print("'{}' : [{}],".format(end, dump))
    return res


def stringify_block(block):
    end_addr = block.insts[len(block.insts) - 1].addr
    #print(end_addr)
    res = "Addr {}\n".format(block.start_addr)
    res += "Calls to {}\n".format(stringify_children(block.children, end=end_addr))
    res += ""
    for inst in block.insts:
        res += stringify_inst(inst) + "\n"
    res += "\n"
    return res


def print_funcs_blocks(funcs):
    for func in funcs.values():
        res = "Start addr {}\n".format(func.start_addr)
        res += "Called by {}\n".format(func.xrefs_to)
        res += "Calls to {}\n\n".format(func.xrefs_from)
        for block in func.blocks.values():
            res += stringify_block(block)

        with open("./clean/" + func.start_addr, "w") as f:
            f.write(res)


if __name__ == "__main__":
    linear_trace = load_trace()
    fix_calls(linear_trace)
    function_thingy = build_all_funcs(linear_trace)
    funcs_with_blocks = process_func_blocks(function_thingy)
    print_funcs_blocks(funcs_with_blocks)