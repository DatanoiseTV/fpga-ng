| design | binary | runs ok | router time (s) | CPU time (s) | Fmax per clock, median / best (MHz) |
|---|---|---|---|---|---|
| litex_i9_vexriscv | baseline | 5/5 | 8.7 | 19.5 | eth_clocks0_rx 95.8 / 109.7; sys_clk 61.3 / 66.3 |
| litex_i9_vexriscv | candidate | 5/5 | 8.9 | 17.2 | eth_clocks0_rx 95.8 / 109.7; sys_clk 61.3 / 66.3 |
| picorv32_x6 | baseline | 5/5 | 17.5 | 65.6 | clk 65.5 / 65.8 |
| picorv32_x6 | candidate | 5/5 | 19.8 | 56.9 | clk 65.5 / 65.8 |
| picorv32_x8 | baseline | 5/5 | 26.1 | 90.1 | clk 65.8 / 66.7 |
| picorv32_x8 | candidate | 5/5 | 26.6 | 71.1 | clk 65.8 / 66.7 |
