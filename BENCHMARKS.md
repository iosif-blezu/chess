# Chess AI Benchmarks

Benchmarks were run on May 12, 2026 to provide a quick performance snapshot for the current AI implementation.

## Methodology

- Command: `PYTHONPATH=/workspace/chess python /tmp/run_ai_benchmarks.py`
- Python: 3.14.4
- Platform: Linux 6.12.47 x86_64 with glibc 2.39
- CPU count reported by Python: 3
- Runs per position/difficulty pair: 3
- Timing metric: wall-clock seconds measured around `AI.findBestMove(...)` with `time.perf_counter()`.
- Repeatability settings:
  - Opening book disabled for benchmarked settings so the timings measure search rather than instant book lookup.
  - Random move chance set to `0.0` for all benchmarked settings.
  - `random.seed(...)` reset before each run.
  - Transposition table cleared before each run to measure cold-search behavior.

## Difficulty settings used

| Difficulty | Max depth | Time limit | Quiescence | Transposition table | Opening book | Random move chance |
| --- | ---: | ---: | --- | --- | --- | ---: |
| Easy | 1 | 0.25s | Off | Off | Off | 0.0 |
| Medium | 3 | 1.00s | On | On | Off | 0.0 |
| Hard | 5 | 2.00s | On | On | Off | 0.0 |

## Results

| Position | Difficulty | Legal moves | Best move(s) across 3 runs | Min (s) | Mean (s) | Max (s) |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| Initial position | Easy | 20 | `e2e4` | 0.0278 | 0.0292 | 0.0317 |
| Initial position | Medium | 20 | `g1f3` | 1.0004 | 1.0005 | 1.0007 |
| Initial position | Hard | 20 | `b1c3` / `g1f3` / `b1c3` | 2.0005 | 2.0015 | 2.0026 |
| Developed opening | Easy | 33 | `f3e5` | 0.0700 | 0.0715 | 0.0733 |
| Developed opening | Medium | 33 | `b1c3` | 1.0002 | 1.0016 | 1.0035 |
| Developed opening | Hard | 33 | `b1c3` | 2.0002 | 2.0006 | 2.0012 |
| Hanging queen tactic | Easy | 15 | `a1a8` | 0.0102 | 0.0104 | 0.0106 |
| Hanging queen tactic | Medium | 15 | `a1a8` | 0.1219 | 0.1298 | 0.1427 |
| Hanging queen tactic | Hard | 15 | `a1a8` | 0.9214 | 0.9468 | 0.9735 |
| Mate in one | Easy | 24 | `f6f7` | 0.0032 | 0.0032 | 0.0033 |
| Mate in one | Medium | 24 | `f6f7` | 0.0200 | 0.0223 | 0.0261 |
| Mate in one | Hard | 24 | `f6f7` | 0.0858 | 0.0876 | 0.0892 |
| Pawn promotion | Easy | 6 | `a7a8` | 0.0013 | 0.0013 | 0.0014 |
| Pawn promotion | Medium | 6 | `a7a8` | 0.0380 | 0.0382 | 0.0385 |
| Pawn promotion | Hard | 6 | `a7a8` | 1.2217 | 1.2345 | 1.2568 |

## Observations

- Medium and hard hit their configured time limits on broader opening positions, which is expected for time-limited iterative deepening.
- Tactical positions with fewer relevant branches finish below the configured time limits, especially the hanging queen and mate-in-one positions.
- The hard setting is noticeably more expensive in the pawn-promotion position because it searches deeper even though there are only six legal root moves.
- The initial-position hard move varied between `b1c3` and `g1f3`; this can happen when similarly scored moves are explored under a time cutoff.

## Benchmark scenario descriptions

- **Initial position:** Standard chess starting position.
- **Developed opening:** Standard position after `e2e4 e7e5 g1f3 b8c6 f1c4 g8f6`.
- **Hanging queen tactic:** White king on e1, black king on e8, white rook on a1, black queen on a8; best move captures the queen with `a1a8`.
- **Mate in one:** White king on f6, white queen on g7, black king on h8; the selected `f6f7` move was verified by the existing tactical test pattern as a checkmating move from this position.
- **Pawn promotion:** White king on e1, black king on h8, white pawn on a7; best move promotes with `a7a8`.
