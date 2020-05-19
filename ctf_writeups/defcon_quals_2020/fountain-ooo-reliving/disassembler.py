test = """0000000000000001000000000000000000010011111111111111110001
0000000000000000000000000000000000110011111111111111110001
0000000000000000110000000000000000100100000000000000110010
0000000000000000010100000000000000110011111111111111110001
0000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000011110100000000000000100000
0000000000000000100100000000000000110100000000000001000011
0000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000110100000000000001010001
0000000000000000000000000000000000000000000000000000000001
0000000000000000000000000000000001010100000000000000100001
0000000000000000100100000000000001010000000000000000000011
0000000000000001010100000000000001000100000000000001010011
0000000000000001010100000000000000110011111111111111110001
0000000000000001000000000000000000100100000000000001000010
0000000000000001000000000000000000010011111111111111110001
0000000000000000010000000000000000100011111111111111110001
0000000000000001100000000000000001110011111111111111110001
0000000000000000110000000000000000110011111111111111110001"""

opcodes = {'MNZ': '0000',
           'MLZ': '0001',
           'ADD': '0010',
           'SUB': '0011',
           'AND': '0100',
           'OR' : '0101',
           'XOR': '0110',
           'ANT': '0111',
           'SL' : '1000',
           'SRL': '1001',
           'SRA': '1010'}

rev_opcodes = {v: k for k, v in opcodes.items()}

modes = { '': '00',
         'A': '01',
         'B': '10',
         'C': '11'}

rev_modes = {v: k for k, v in modes.items()}


#Should result in
#0. MLZ -1 3 3;
#1. MLZ -1 7 6; preloadCallStack
#2. MLZ -1 2 1; beginDoWhile0_infinite_loop
#3. MLZ -1 1 4; beginDoWhile1_trials
#4. ADD A4 2 4;
#5. MLZ -1 A3 5; beginDoWhile2_repeated_subtraction
#6. SUB A5 A4 5;
#7. SUB 0 A5 2;
#8. MLZ A2 5 0;
#9. MLZ 0 0 0; endDoWhile2_repeated_subtraction
#10. MLZ A5 3 0;
#11. MNZ 0 0 0; endDoWhile1_trials
#12. SUB A4 A3 2;
#13. MNZ A2 15 0; beginIf3_prime_found
#14. MNZ 0 0 0;
#15. MLZ -1 A3 1; endIf3_prime_found
#16. ADD A3 2 3;
#17. MLZ -1 3 0;
#18. MLZ -1 1 4; endDoWhile0_infinite_loop

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is


def disassemble_operand(operand):
    dis_mode = operand[:2]
    mode = rev_modes[dis_mode]
    val = twos_comp(int(operand[2:], 2), len(operand[2:]))
    return str(mode) + str(val)

def disassemble_line(l):
    opcode = rev_opcodes[l[-4:]]
    arg1 = disassemble_operand(l[18*2:18*3])
    arg2 = disassemble_operand(l[18:18*2])
    arg3 = disassemble_operand(l[:18])
    return " ".join([opcode, arg1, arg2, arg3])

def process(prog):
    program = prog.splitlines()[::-1]
    res = list(map(disassemble_line, program))
    fin = ""
    for i, l in enumerate(res):
        fin += str(i+1) + " " + l + "\n"
    return fin.strip()

print(process(test))
def win():
    with open("good_rom.txt", "r") as f:
        content = f.read()
    prog = process(content)
    with open("dissambled_prog.txt", "w") as f:
        f.write(prog)