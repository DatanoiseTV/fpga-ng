| design | binary | runs ok | router time (s) | CPU time (s) | Fmax per clock, median / best (MHz) |
|---|---|---|---|---|---|
| litex_i9_vexriscv | baseline | 5/5 | 9.7 | 21.5 | eth_clocks0_rx 95.8 / 109.7; sys_clk 61.3 / 66.3 |
| litex_i9_vexriscv | candidate | 5/5 | 7.9 | 19.0 | eth_clocks0_rx 100.5 / 109.0; sys_clk 61.4 / 65.9 |
| picorv32_x6 | baseline | 5/5 | 17.4 | 65.9 | clk 65.5 / 65.8 |
| picorv32_x6 | candidate | 5/5 | 16.7 | 65.4 | clk 64.8 / 65.4 |
| picorv32_x8 | baseline | 5/5 | 25.8 | 88.5 | clk 65.8 / 66.7 |
| picorv32_x8 | candidate | 5/5 | 24.9 | 88.4 | clk 66.4 / 67.2 |
