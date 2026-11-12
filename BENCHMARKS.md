# Benchmark Methodology

py-cheema-api's positioning is **lightweight, stdlib-only, zero build step**. These
benchmarks are designed to prove that claim honestly, not to chase raw
throughput numbers against compiled-extension frameworks. Every category below
answers a real deployment question, not just "requests per second."

## Why these categories

Most framework benchmarks only measure throughput under load. That is one
axis. For a stdlib-only framework, the more interesting axes are **startup
cost**, **memory footprint**, and **dependency surface** — because those are
where "lightweight" actually pays off in production (cold starts, container
density, security surface).

| Category | What it measures | Why it matters for py-cheema-api |
|---|---|---|
| Cold start time | Time from `python app.py` to first successful response | Serverless/Lambda-style deploys, CI test suites, dev reload loops |
| Memory footprint (RSS) | Resident memory at idle and under load | Container density — how many instances per host/node |
| Install footprint | `pip install` size, transitive dependency count | Attack surface, Docker layer size, `pip install` time |
| HTTP throughput (uncached) | req/s on GET/POST routes, no response caching | Apples-to-apples with FastAPI+uvicorn and turboapi's own uncached tables |
| p50/p99 latency | Tail latency under concurrent load | User-facing responsiveness, not just aggregate throughput |
| Dependency-free validation | Overhead of `Model`+`field()` vs Pydantic v2 | Cost of the "no required dependencies" path specifically |

## Comparison targets

- **FastAPI + uvicorn** (industry baseline, same ergonomics class)
- **turboapi** (Zig-core competitor, same "Turbo" naming space, opposite
  tradeoff — compiled speed vs. zero-dependency portability)
- **py-cheema-api** with Pydantic extra installed, and without (to isolate the
  stdlib-only path)

## Test conditions (must be disclosed per run)

- Python version and whether free-threaded (`3.14t`) or standard build
- OS / kernel, CPU model, whether run in Docker or bare metal
- Number of workers/threads for each framework (match worker count, don't let
  one framework use more parallelism than another)
- Whether response caching / DB caching is enabled or disabled (disable for
  fairness, note explicitly if left on)
- Load generator (e.g. `wrk`, `hey`, `oha`) with exact command line
  reproduced in the report
- 3 clean runs minimum, report median with min/max range — a single run is
  not a benchmark

## Routes to test (mirror common real-world shapes)

1. `GET /health` — zero-arg handler, no params
2. `GET /items/{id}` — path param with type coercion
3. `GET /items?limit=&offset=` — query params
4. `POST /items` — JSON body with model validation
5. `GET /items/{id}` with a dependency (`Depends()`) — exercises DI overhead,
   not just the fast path

Testing only the zero-arg route (as some frameworks headline) overstates real
throughput, since most production routes have params, validation, or DI.

## Startup time test

```bash
# cold start, average of 20 runs
for i in $(seq 1 20); do
  START=$(date +%s.%N)
  python app.py &
  PID=$!
  until curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; do sleep 0.01; done
  END=$(date +%s.%N)
  echo "$END - $START" | bc
  kill $PID
done
```

## Memory footprint test

```bash
# idle RSS, then RSS after sustained load
python -c "import psutil, subprocess, time; ..."  # measure at t=0 and t=60s under load
```

Report both **idle RSS** (import + framework init only) and **loaded RSS**
(after 60s of sustained traffic) — idle RSS shows the "stdlib-only" cost
directly; loaded RSS shows whether that gap holds up under GC pressure.

## Install footprint test

```bash
pip install --no-cache-dir py-cheema-api
pip install --no-cache-dir fastapi uvicorn
pip install --no-cache-dir turboapi
du -sh $(python -c "import site; print(site.getsitepackages()[0])")
pip list | wc -l   # transitive dependency count
```

## What "winning" looks like

py-cheema-api is not trying to top the throughput table. A credible result
set looks like:

- Uncached HTTP throughput within a reasonable band of turboapi's Python
  fallback path (not its native FFI path) and clearly ahead of FastAPI+uvicorn
  on routes with validation, since stdlib validation avoids Pydantic overhead
- Meaningfully lower cold-start time and idle RSS than both competitors
- Meaningfully smaller install footprint (no Zig toolchain, no free-threaded
  Python requirement, no Pydantic-by-default)

Publish the raw numbers, the losses included. A benchmark page that only
shows wins reads as marketing, not evidence — and undermines the credibility
you're trying to build against a competitor whose own README already invites
scrutiny of its numbers.

## Published results: py-cheema-api vs FastAPI

Sandbox run, py-cheema-api and FastAPI both served by uvicorn on the same
machine, one at a time, sync handlers. Higher req/s is better; lower p99 is
better.

| Scenario | Cheema req/s | FastAPI req/s | Ratio | p99 ms (Cheema / FastAPI) |
|---|---:|---:|---:|---:|
| `GET /hello` | 9,951 | 6,920 | 1.44x | 14 / 15 |
| Path-param GET | 9,613 | 6,308 | 1.52x | 13 / 16 |
| Query-param GET | 8,689 | 5,652 | 1.54x | 15 / 17 |
| Small POST (2 fields) | 8,935 | 5,609 | 1.59x | 16 / 18 |
| Large POST (about 2 KB, nested) | 5,701 | 3,641 | 1.57x | 22 / 36 |
| 100-row JSON list | 2,545 | 1,290 | 1.97x | 50 / 80 |

Reading the table:

- Cheema is about 1.4x to 2.0x faster than FastAPI on every scenario above,
  with equal or lower p99 latency.
- **Only the ratios are meaningful.** The load generator ran on the same CPU as
  the server, so absolute req/s is lower than a dedicated rig would give.
- Not measured: real endpoints, database latency, multiple workers, HTTP/2 or
  TLS, long soak runs, memory, cold start, install footprint.

### Large request bodies: a regression that was found and fixed

An earlier run of the same harness showed Cheema at **0.56x** of FastAPI on the
2 KB POST (about 1,485 vs 2,644 req/s). Cause: the stdlib `Model` validator
re-inspected the type of every value (about 190 values in that body), costing
about 746 µs per request against about 17 µs for pydantic's compiled core.

The validator now compiles each `Model`'s field types once into specialised
closures and falls back to the original path to build error details, so error
messages and `loc` values are unchanged. Validation of the same body measured
about 33 µs in a micro-benchmark (down from about 600 µs), which is what moved
the large-POST row above from 0.56x to 1.57x.

Models that use `field_validator` / `model_validator` hooks, unions, `Decimal`,
dataclasses, TypedDicts or pydantic fields still use the general path and do
not get this speedup. Declaring a very large body as a pydantic `BaseModel` is
still an option, and cheema accepts it.

## Reproducibility

Ship `benchmarks/bench_runtime.py` results as JSON alongside a `baseline.json`
(you already have the CI gate for this — reuse it for the public-facing
report). Publish the exact commit hash, environment, and command line used to
produce every number in the README table. Anyone should be able to clone the
repo and reproduce your numbers within noise.
