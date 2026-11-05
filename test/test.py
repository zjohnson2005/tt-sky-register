# SPDX-FileCopyrightText: © 2026 Zachary Johnson
# SPDX-License-Identifier: Apache-2.0

import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge


def control(write_address=0, write_enable=0, read_address=0):
    return (read_address << 4) | (write_enable << 3) | write_address


async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await FallingEdge(dut.clk)


async def step(dut, write_data=0, write_address=0, write_enable=0, read_address=0):
    dut.ui_in.value = write_data
    dut.uio_in.value = control(write_address, write_enable, read_address)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    return int(dut.uo_out.value)


@cocotb.test()
async def test_reset_and_x0(dut):
    await reset(dut)
    assert int(dut.uio_oe.value) == 0
    for address in range(8):
        await step(dut, read_address=address)
        assert await step(dut, read_address=address) == 0, f"x{address} not zero after reset"

    await step(dut, write_data=0xAB, write_address=0, write_enable=1)
    await step(dut, read_address=0)
    assert await step(dut, read_address=0) == 0, "x0 must ignore writes"


@cocotb.test()
async def test_write_then_read(dut):
    await reset(dut)
    values = {a: (0x11 * a) ^ 0x5A for a in range(1, 8)}
    for address, value in values.items():
        await step(dut, write_data=value, write_address=address, write_enable=1)
    for address, value in values.items():
        await step(dut, read_address=address)
        got = await step(dut, read_address=address)
        assert got == value, f"x{address}: got {got:#x}, want {value:#x}"


@cocotb.test()
async def test_forwarding(dut):
    await reset(dut)
    await step(dut, write_data=0x10, write_address=3, write_enable=1)
    got = await step(dut, write_data=0x99, write_address=3, write_enable=1, read_address=3)
    assert got == 0x99, f"same-cycle read of x3 should forward 0x99, got {got:#x}"
    got = await step(dut, write_data=0x77, write_address=0, write_enable=1, read_address=0)
    assert got == 0, "writing x0 must not forward"


@cocotb.test()
async def test_random(dut):
    await reset(dut)
    rng = random.Random(2026)
    model = [0] * 8
    for _ in range(500):
        data = rng.randrange(256)
        waddr = rng.randrange(8)
        we = rng.randrange(2)
        raddr = rng.randrange(8)
        if raddr == 0:
            want = 0
        elif we and waddr == raddr:
            want = data
        else:
            want = model[raddr]
        got = await step(dut, data, waddr, we, raddr)
        assert got == want, f"read x{raddr}: got {got:#x}, want {want:#x}"
        if we and waddr != 0:
            model[waddr] = data
