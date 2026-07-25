# HN Evidence — python-lru-cache-feature-lab

Source thread: https://news.ycombinator.com/item?id=27768211  
Story: "Functools – The Power of Higher-Order Functions in Python"  
HN item JSON: `hn_story_27768211.json`  
Full thread dump: `hn_evidence.jsonl`

## Linked article claims

From https://martinheinz.dev/blog/52 (mirrored at https://towardsdatascience.com/functools-the-power-of-higher-order-functions-in-python-8e6e61c6e4e4):

- `functools.lru_cache` provides least-recently-used cache / memoization of function results
- `@lru_cache(maxsize=32)` caches up to 32 results
- `cache_info()` shows hits and misses
- `cache_parameters()` inspects `maxsize` / `typed`
- optional `typed=True` caches arguments of different types separately
- `functools.cache` is a thin wrapper over `lru_cache` without `maxsize` eviction
- `cached_property` caches a class attribute, runs only on lookups, can be cleared by deleting the attribute
- Article warning: "do not use them if your function has any side effects or if it creates mutable objects with each call, as those are not the types of functions that you want to have cached"

## Named Hacker News commenter claims

- `pyuser583` (HN 27780704): "Don't use lru_cache. It stores pointers to the values, so if a mutable value is changed downstream it gets changed in the cache. That's not proper caching."
- `SV_BubbleTime` (HN 27780737), replying to pyuser583: "This seems like it would have been an easy fix on their end. Was the issue memory and storage?"
- `jakear` (HN 27780820), replying to SV_BubbleTime: "It'd be annoying for every type used in a cache to need to properly implement `__deepcopy__()`, and it'd pose significant performance impact, especially if the cached objects are large (which there's a good chance they are, given you've felt the need to cache them rather than build them from scratch). Much better off using the same assignment semantics used throughout Python and let people choose to deepcopy() all the objects they read from the cache if they really really want to modify them later; it would even work as a simple decorator to stack onto the existing one for such cases."
- `goodside` (HN 27781014), replying to pyuser583: "This is how I would expect it to work. Caching mutable collections is a legitimate use case, distinct from caching the immutable values those collections contain. `lru_cache` does not wrap your cached values in container types on its own, so if you're getting bit by mutable values it's probably because what you cached was a mutable container (like `list`, `dict`, or `set`). If you use primitive values in the cache, or immutable containers (like `tuple`, `namedtuple`, or `frozenset`), you won't hit this problem. If you were to manually cache values yourself using a `dict`, you'd see similar issues with mutability when storing `list` objects as values. It's not a problem specific to `lru_cache`."
- `Xavdidtheshadow` (HN 27781134), replying to pyuser583: "I disagree — it works wonders for expensive functions that return strings and ints. Maybe 'don't use lru_cache with mutable values' would be more accurate."
- `zo1` (HN 27781504), replying to pyuser583: "Not to be mean but you can't expect caching to fix a fundamental design issue in your code."
- `gorgoiler` (HN 27780354): "`functools` and `itertools` are amazing … Using `@cached_property` feels like a bad code smell and it's a controversial design decision."

## Current Python documentation

Python 3.11+ `functools.lru_cache` docs (https://docs.python.org/3/library/functools.html#functools.lru_cache):

- Decorator to wrap a function with a memoizing callable that saves up to `maxsize` most recent calls
- "Since a dictionary is used to cache results, the positional and keyword arguments to the function must be hashable."
- "If `typed` is set to true, function arguments of different types will be cached separately. If `typed` is false, the implementation will usually regard them as equivalent calls and only a single result will be cached."
- Wrapped function is instrumented with a `cache_info()` function returning a named tuple showing hits, misses, maxsize and currsize
- `cache_clear()` clears the cache
- "A cache can implement an LRU … eviction algorithm"
- No automatic copying of return values is documented; cache stores the function result directly

`functools.cache` (Python 3.9+): "Simple lightweight unbounded function cache. Sometimes called 'memoize'… Same as `lru_cache(maxsize=None)`."

## Local observations

From `observations.json` (12 rows, all passed, Python 3.12.3):

1. `repeated_feature_cache_hit_marker` — hashable string input `"sample-1"`, feature vector `[0.1, 0.2, 0.3]`
   - First call: `misses=1`, `hits=0`, wrapped function executed 1 time
   - Second call: `misses=1`, `hits=1`, wrapped function still at 1 execution
   - Both calls return `[0.1, 0.2, 0.3]`

2. `mutable_cached_return_alias_marker`
   - Cached function returns `list [0.1, 0.2, 0.3]`
   - Caller mutates `r1[0] = 9.9`
   - Second call returns the same object (`r2 is r1 == True`)
   - Mutation is visible: `r2[0] == 9.9`
   - Recorded as documented aliasing behavior

3. `immutable_cached_tuple_marker`
   - Cached function returns tuple `(0.1, 0.2, 0.3)`
   - Repeated calls hit cache, return expected tuple
   - Item assignment `r1[0] = 9.9` raises `TypeError`
   - Extractor executed once across two identical calls

4. `unhashable_list_argument_marker`
   - Cached function called with list argument `["a", "b"]`
   - `TypeError` raised before wrapped function body executes (`exec_count == 0`)
   - Cache `hits` and `misses` unchanged (both 0)

## Non-claims / Limitations

This lab does NOT claim that:

- `lru_cache` copies return values
- `lru_cache` makes mutable outputs safe
- `lru_cache` accepts unhashable arguments
- The tested pattern is suitable for every feature pipeline
- Any performance characteristics have been measured or proven
- Immutability of the return tuple prevents every kind of downstream mutation problem

This lab does NOT cover:

- cache eviction / `maxsize` behavior
- concurrency / thread safety
- keyword argument ordering
- `typed=True` vs `typed=False`
- integer vs float cache key collisions
- defensive copying wrappers
- production cache invalidation strategies
- `functools.cache`, `cached_property`, `singledispatch`, `partial`, `total_ordering`, or other `functools` features
