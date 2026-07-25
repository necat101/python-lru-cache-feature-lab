# python-lru-cache-feature-lab

Tiny deterministic correctness lab for `functools.lru_cache` when caching ML-adjacent feature extraction.

Inspired by the Hacker News thread on Python's functools module: https://news.ycombinator.com/item?id=27768211

See `hn_evidence.md` for the full evidence trail (linked article claims, named HN commenter claims, Python docs, local observations, and explicit non-claims).

## Cases

Four deterministic cases, each producing three rows (`inspect_inputs`, `execute_cache`, `verify_relation`) — 12 rows total.

All cases use fixed synthetic feature values: `[0.1, 0.2, 0.3]` / `(0.1, 0.2, 0.3)`, input `"sample-1"`. The relevant cache is cleared before each case.

| # | case | what it checks |
|---|------|----------------|
| 1 | `repeated_feature_cache_hit_marker` | Cached extractor with hashable string input. First call is a miss, second is a hit. Wrapped function executes once. Both calls return `[0.1, 0.2, 0.3]`. |
| 2 | `mutable_cached_return_alias_marker` | Cached function returning a `list`. Caller mutates the returned list. Second call returns the same cached object and exposes the caller's mutation. Documented aliasing behavior. |
| 3 | `immutable_cached_tuple_marker` | Cached function returning a `tuple`. Repeated calls hit the cache, return `(0.1, 0.2, 0.3)`. Item assignment raises `TypeError`. |
| 4 | `unhashable_list_argument_marker` | Cached function called with a list argument. Raises `TypeError` before the wrapped body executes. Cache counters are unchanged. |

## Running

```bash
python run_lab.py
python -m unittest test_lab -v
```

Both the lab runner and the test suite should report all checks passing.

## Files

- `run_lab.py` — the lab, 4 cases × 3 methods = 12 rows
- `test_lab.py` — `unittest` verification, independent checks against production helpers
- `observations.json` — machine-readable results (12 rows)
- `RESULTS.md` — human-readable table
- `hn_evidence.md` — HN thread claims, Python docs, local observations, non-claims
- `hn_evidence.jsonl` — raw HN thread dump
- `hn_story_27768211.json` — HN story JSON

## What this lab does NOT claim

- `lru_cache` copies return values — it does not. Mutable cached returns alias, as case 2 demonstrates.
- `lru_cache` makes mutable outputs safe — it does not.
- `lru_cache` accepts unhashable arguments — it does not, case 4 demonstrates the `TypeError`.
- This pattern is suitable for every feature pipeline — no claim is made about suitability.
- Any performance characteristics — no timing, no benchmarks.
- Immutability of the return tuple prevents every downstream mutation problem — it prevents item assignment, not every misuse.

## What this lab does NOT cover

- cache eviction / `maxsize` behavior
- concurrency / thread safety
- keyword argument ordering
- `typed=True` vs `typed=False`
- integer vs float cache key collisions
- defensive copying wrappers
- production cache invalidation strategies
- `functools.cache`, `cached_property`, `singledispatch`, `partial`, `total_ordering`, or other `functools` features

## Results

See `RESULTS.md` and `observations.json`.