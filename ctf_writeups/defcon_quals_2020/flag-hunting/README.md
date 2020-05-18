Solves: 40

Points: 131

Solution: We're provided a file containing the execution trace of a what seems to be the execution of a normal CTF
reversing problem. It contains each instruction executed, but not the memory address of the instruction nor register
values. We thankfully get a hash of the location of each instruction, so we can tell when an single instruction shows 
up multiple times.

Example: 3cda655ffeabac454f0ddeffbd60f3f3  mov    r9,rdx

First, we pulled out functions and basic blocks. Functions can be identified in a trace by the "indentation" of the 
trace (thanks to teammate bigrick), which conceptually matches stack frames. Calling a new function increases the indent,
and ret reduces it. We keep track of the instructions hit each indent layer, and use that to capture the trace of a 
single execution of the function.

From there, we can mostly rebuild a graph view (like in IDA/Ghidra/etc) by pulling out the basic blocks in each
function, based on the edges created by each jump. We also make sure to log the history of which jumps are taken. This
was aided by teammate bigrick figuring out which functions were libc calls, based on instructions matching going through
got/plt.

This is done by this python [script](./process.py), and results in the dumps here [folder](./Functions). A very rough
translation into psuedo-C is [here](./cfuncs.c), obtained by manually reversing the assembly

Summary of interesting functions:
- Main - d4b63f79787617aa772212ce97b88a4b: Opens and reads file, calls check functions
- first_checks - 1b64d9cc243c25e429b5cca3c5e66c8b: Checks for OOO as the start of the flag. Also gives us the length and
accepted character range
- second_checks - bb9cc4afceb13f7385ca1ada5a386eb2: Iterates over each character in the flag, calling per_character, and
keeps track of the head of the tree. Once done, calls print_tree
- per_character - d670e25f0b1e4b298321e687f777ec14: Adds each character to the tree, and calls malloc_node,
first_tree_rotate and second_tree_rotate as appropriate
- malloc_node - b58310a1d83b616fca1491b8ddaa4051
- first_tree_rotate - 83be5e65d5010b6ce1fd4da060e07888
- second_tree_rotate - 1f7aa429199eac8a7c6017e9e57df7fc
- print_tree - 05ac00e1e7aae89912d1ee1d234e3f19: Walks the tree and does an infix order print of the nodes

From there, [build_contraints.py](build_contraints.py) and [tree.py](tree.py) recreate the tree structure, keeping track
of which indices in the flag input correspond to each node in the tree. Additionally, it validates that the correct 
rotates are performed, by comparing the rotations the python script does to the ones tha show up in the trace. As output,
it prints the tree in in-fix order. These constraints are used by [win.py](win.py) to write all flag strings that satisfy
those constraints (around ~480k worth). Most are gibberish, but I manually searched for the most commonly used 2 letter
words in the file, and manually get the rest of the way to the flag.