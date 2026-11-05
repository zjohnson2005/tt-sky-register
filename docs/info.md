<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This is a small register file in the style of a RISC-V CPU. It has eight 8-bit registers, x0 through x7, with one write port and one read port.

Like RISC-V, register x0 is hardwired to zero. Writes to it are ignored and it always reads as 0.

The read port has write-through forwarding. If you read the same register you are writing in the same clock cycle, the output returns the new value being written instead of the old one. This is the same bypass a pipelined CPU uses so an instruction can read a result the instruction before it just produced.

The input pins are captured into registers on every clock edge before they are used, and the read data is registered too, so a value appears on `uo_out` two clocks after you set the read address, and a write takes effect one clock after you present it. All registers reset to 0.

| Pin | Function |
|---|---|
| `ui_in[7:0]` | write data |
| `uio_in[2:0]` | write address |
| `uio_in[3]` | write enable |
| `uio_in[6:4]` | read address |
| `uo_out[7:0]` | read data |

## How to test

1. Hold `rst_n` low for a few clocks, then release it.
2. To write: put the value on `ui_in`, the register number on `uio[2:0]`, and set `uio[3] = 1` for one clock.
3. To read: put the register number on `uio[6:4]`. Two clock edges later the value appears on `uo_out`.
4. To see forwarding: write a new value to a register while its number is also on the read address. The output shows the new value at the same time the write lands, without waiting an extra clock.
5. Writing to x0 and reading it back always gives 0.

## External hardware

No extra parts are needed beyond the Tiny Tapeout demo board, but the board's DIP switches only reach `ui_in`. The control signals on the `uio` pins have to be driven another way:

- **Recommended:** drive and read every pin from the demo board's RP2040 using the Tiny Tapeout MicroPython SDK. A short script makes timing exact and repeatable.
- **By hand:** wire the `uio` pins to switches through the PMOD headers.

Read results from the RP2040 rather than the 7-segment display, since `uo_out` also drives the display segments and binary values light up as odd segment patterns.

Set up the data and address first, wait one clock, and only then assert the command or write enable. The board's signals are not synchronized to the chip's clock, so changing everything at once can let a clock edge capture a mix of old and new values.
