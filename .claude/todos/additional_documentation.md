# Additional Documentation TODO

Tracks documentation suggestions to be added to `.claude/docs/` or elsewhere.

**Last Updated**: 2026-02-27

---

## Pending

### ICE40 Hardware Model Guide
Document the ICE40hx1k-specific constants and bitstream format used in [FileBasedCircuit.py](../../src/Circuit/FileBasedCircuit.py).
- Magic tile coordinates: X=(4,9), Y=(1,16) for ICE40hx1k
- MOORE vs NEWSE routing type differences and when each is used
- What ASC files are and how the bitstream is encoded (ASCII 48/49 = bit 0/1)
- What "accessible columns" means and how `__run_at_each_modifiable()` iterates the bitstream
- Reference the comment at FileBasedCircuit.py:98: "Go over this with someone who can clarify what all of the data types are"

### Microcontroller Serial Protocol Specification
Document the MCU communication protocol used in [Microcontroller.py](../../src/Hardware/Microcontroller.py).
- Packet format: what "START"/"FINISH" sentinel bytes mean
- WAVEFORM request flow: what bytes are exchanged, how 500 samples arrive
- OSCILLATIONS request flow: pulse count format and multi-sample logic
- Why the fallback value is -1000 (currently undocumented magic number)
- Retry logic: why max_attempts=5 and what triggers a retry
- TODO at line 72: serial reads/writes need optimization
- TODO at line 123: serial parsing uses poor regex, should be improved

---

## Completed

<!-- Move items here once the documentation has been written -->