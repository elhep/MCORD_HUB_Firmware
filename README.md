# MCORD_AFEHUB

Both builds contains DHCP and Thread supports. 

In build file ` mpconfigboard.h ` has been changed:

- #define MICROPY_PY_THREAD (1)
- #define MICROPY_PY_THREAD_GIL (1)

During build a micropython also `MICROPY_PY_LWIP=1` has been set up. 


Documentation containing descriptions of the Hub's utility functions and instructions for initialization can be found [here](https://afe-documentation.readthedocs.io/en/latest/)





