## For documenting current state of the "evolvatron" implementation

NOTE: Currently only implemented for simple variance maximization and pulse count experiments

Does not work for tone discrimination at this time

Only D2 and D3 can be used for interrupts

TODOs:
* Remove the fpga and fpga2 parameters and replace all usages
  - Allow usage w/ multiple pins with old transferability system
* Test new Arduino code without providing pins
* Test non transferability ones
* Fully test transferability experiments
* Handle FPGA collection for sim modes
* Upload to the correct FPGA
