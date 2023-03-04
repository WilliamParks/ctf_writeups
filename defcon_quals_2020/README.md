# DEFCON CTF Qualifiers 2020: 15 - 17 May

I competed with the great [Shell Collecting Club](https://ctftime.org/team/45676), placing 45th. This is our best finish
to date, but still a ways away from qualifying for finals.

During this CTF, I solved two challenges, each with the help of multiple teammates:

## fountain-ooo-reliving

Solves: 72

Points: 115

Summary: We're provided a file containing the save state of a computer implemented in Conway's Game of Life (GoL). It's
a modified version of [Quest for Tetris](https://github.com/QuestForTetris/QFT). The CTF problem is 
the same CPU implementation, but with different ROM values. Solving the problem required dumping the ROM from the GoL
file, writing a disassembler for instructions in ROM, running those instructions in an interpreter, and figuring out the
initial starting value in RAM slot 1 to get the program to write the flag.

## flag-hunting

Solves: 40

Points: 131

Summary: We're given a file containing the execution trace of a standard CTF RE problem. It contains the instructions 
executed with a hash of the memory address of the instruction, but not the actual data. With that start point, we were
able to extract the functions and the basic blocks of the program, along with the path that was executed. I reversed the
assembly, and determined the original program build a self-balancing binary tree based on the input. Based on the
execution path taken, I could find out which nodes in the tree were accessed when each character in the flag was added.
With the rebuilt tree structure and knowing which tree nodes corresponded to each index of the flag, I was able to built
a list of constraints for the flag. For example, the farthest left value leaf of the tree was accessed by flag indices
8,11,17,22,26,30,34,39,44,51. We thus know that all of those characters in the flag have the same value (space in this
 case), and all other nodes in the tree must have higher ascii values. I dumped all possible strings that fit
 these constraints (~480k in total), and found the one that was the most human readable, which was the flag.