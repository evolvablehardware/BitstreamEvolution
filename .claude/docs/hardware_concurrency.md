# Hardware Concurrency Model

## Overview

The `Hardware` protocol uses `async def request_measurement()` so that multiple FPGA measurements
can be dispatched concurrently via `asyncio.gather()` in `Evolution.run()`. This document explains
when that concurrency is real, the physical constraint that limits it, and how to implement the
constraint correctly.

---

## Current State (Blocking Serial)

`Microcontroller` uses `pyserial`, which is entirely blocking. The `async def` methods never
actually yield to the event loop, so `asyncio.gather()` runs them one at a time. There is no
parallelism in the current implementation.

---

## Target State (Server-Client Model)

The architecture is moving toward a server-client model:

```
Evolution (client)                    Hardware Server
──────────────────                    ──────────────────────────────
asyncio.gather(                       [worker for Icestick 0]──── Icestick 0 (USB)
  hw.request_measurement(m0),   ───►  [worker for Icestick 1]──── Icestick 1 (USB)
  hw.request_measurement(m1),         [worker for Icestick 2]──── Icestick 2 (USB)
  hw.request_measurement(m2),         ...
)
```

In this model:
- The client (`Evolution`) sends all measurement requests over the network simultaneously
- Each `await request_measurement(m)` suspends while waiting for a network response
- `asyncio.gather()` then provides **real parallelism** — all requests are in-flight at once
- The server handles the physical hardware exclusively

### serial_asyncio

On the server side, replace `pyserial` with `serial_asyncio`
(https://pypi.org/project/serial-asyncio/) so that serial reads genuinely suspend within the
server's event loop:

```python
# Current (blocking — blocks the whole event loop)
data = self.__serial.read_until()

# Target (async — yields to event loop while waiting for bytes)
reader, writer = await serial_asyncio.open_serial_connection(url=port, baudrate=baud)
data = await reader.readuntil(b'\n')
```

---

## The Icestick Exclusivity Constraint

**Each physical Icestick can only be accessed by one process at a time.**

`iceprog` (the upload tool called inside `Circuit.compile()`) holds exclusive USB access to the
device while it is programming. If two coroutines attempt to compile to the same Icestick
concurrently, the second `iceprog` call will fail or corrupt the first.

This means:
- **Across different Icesticks**: requests can run fully in parallel ✓
- **On the same Icestick**: requests must be serialized ✗ (without a guard)

---

## How to Enforce the Constraint

### Option A — `asyncio.Semaphore(1)` per Icestick (Recommended)

Each `Microcontroller` instance (one per Icestick) owns a `Semaphore(1)`. Any coroutine must
acquire it before calling `iceprog` or reading serial data:

```python
class Microcontroller:
    def __init__(self, ...):
        ...
        self.__lock = asyncio.Semaphore(1)

    async def request_measurement(self, measurement):
        async with self.__lock:
            # Only one coroutine reaches here at a time per Icestick
            ckt.compile(fpga_data)
            waveform = await self.measure_signal()
            ...
```

`asyncio.gather()` over multiple `Microcontroller` instances (different semaphores) still runs
them all concurrently. Only requests to the *same* instance are serialized.

### Option B — Per-Icestick `asyncio.Queue` with a worker coroutine

One long-lived coroutine per Icestick dequeues measurement requests and processes them one
at a time. The `request_measurement()` call enqueues the work and awaits the result via a
`Future`:

```python
async def _worker(self):
    while True:
        measurement, future = await self.__queue.get()
        try:
            result = await self._do_measurement(measurement)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)

async def request_measurement(self, measurement):
    future = asyncio.get_event_loop().create_future()
    await self.__queue.put((measurement, future))
    return await future
```

This approach also naturally supports **priority queuing** if some measurements should be
scheduled before others.

### Comparison

| | Option A (Semaphore) | Option B (Queue) |
|---|---|---|
| Complexity | Low | Medium |
| Priority support | No | Yes |
| Cancellation | Easy (`asyncio.wait_for`) | Requires extra plumbing |
| Best for | Simple serialization | Scheduling or batching |

---

## Event Loop Lifetime

`Evolution.run()` currently calls `asyncio.run(asyncio.gather(*tasks))` inside the generation
loop, creating and destroying a new event loop each generation. This is wasteful and
incompatible with some asyncio patterns (e.g. a Queue worker started in one loop can't be
awaited in a new loop).

**Preferred approach**: Make `Evolution.run()` itself `async` and run a single event loop for
the whole experiment:

```python
# Instead of:
def run(self):
    while gen_data is not None:
        results = asyncio.run(asyncio.gather(*tasks))  # new loop each generation

# Do:
async def run(self):
    while gen_data is not None:
        results = await asyncio.gather(*tasks)          # one persistent loop

# Entry point:
asyncio.run(evolution.run())
```

This also allows the Option B worker coroutines to be started once at the beginning and
reused across all generations.