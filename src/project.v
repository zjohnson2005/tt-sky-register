/*
 * Copyright (c) 2026 Zachary Johnson
 * SPDX-License-Identifier: Apache-2.0
 *
 * RISC-V style register file: eight 8-bit registers where x0 is hardwired
 * to zero, with write-through forwarding so a read of the register being
 * written in the same cycle returns the new value, like a CPU pipeline's
 * register file bypass. The pins are registered on the way in so
 * signals from the board are never used mid-change.
 */

`default_nettype none

module tt_um_zjohnson2005_regfile (
    input  wire [7:0] ui_in,    // write data
    output wire [7:0] uo_out,   // registered read data
    input  wire [7:0] uio_in,   // [2:0] write address, [3] write enable, [6:4] read address
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    reg [7:0] write_data;
    reg [2:0] write_address;
    reg       write_enable;
    reg [2:0] read_address;

    always @(posedge clk) begin
        if (!rst_n) begin
            write_data    <= 8'd0;
            write_address <= 3'd0;
            write_enable  <= 1'b0;
            read_address  <= 3'd0;
        end else begin
            write_data    <= ui_in;
            write_address <= uio_in[2:0];
            write_enable  <= uio_in[3];
            read_address  <= uio_in[6:4];
        end
    end

    reg [7:0] registers [1:7];
    reg [7:0] read_data;

    wire writing_real_register = write_enable && (write_address != 3'd0);
    wire forward_write         = writing_real_register && (write_address == read_address);

    integer i;

    always @(posedge clk) begin
        if (!rst_n) begin
            for (i = 1; i < 8; i = i + 1) begin
                registers[i] <= 8'd0;
            end
            read_data <= 8'd0;
        end else begin
            if (writing_real_register) begin
                registers[write_address] <= write_data;
            end

            if (read_address == 3'd0) begin
                read_data <= 8'd0;
            end else if (forward_write) begin
                read_data <= write_data;
            end else begin
                read_data <= registers[read_address];
            end
        end
    end

    assign uo_out  = read_data;
    assign uio_out = 8'd0;
    assign uio_oe  = 8'd0;

    wire _unused = &{ena, uio_in[7], 1'b0};

endmodule
