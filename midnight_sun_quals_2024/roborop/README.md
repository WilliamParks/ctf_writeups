The challenge provides you a large amount of executable memory, filled in by rand().

We're provided the seed used to do so, and it runs our ROP chain.

After playing around with it for a bit, we're able to consistently find any op + ret, where the op is no longer than 2 bytes long.

To win, we mprotect the large memory region from above to be writable, read in some shellcode, and jump to it.
