#!/usr/bin/env python3
"""python-lru-cache-feature-lab

Four deterministic functools.lru_cache correctness cases for ML-adjacent
cached feature extraction.

Cases:
  - repeated_feature_cache_hit_marker
  - mutable_cached_return_alias_marker
  - immutable_cached_tuple_marker
  - unhashable_list_argument_marker

Each case produces three rows:
  - inspect_inputs
  - execute_cache
  - verify_relation
"""

from __future__ import annotations
import json
import sys
from functools import lru_cache
from typing import Any, Dict, List

# Fixed synthetic values
SAMPLE_INPUT = "sample-1"
FEATURE_LIST = [0.1, 0.2, 0.3]
FEATURE_TUPLE = (0.1, 0.2, 0.3)

# ----------------------------------------------------------------------
# Repeated feature / cache hit
# ----------------------------------------------------------------------


_repeated_exec_count = 0


@lru_cache(maxsize=32)
def _repeated_extractor(x: str) -> List[float]:
    global _repeated_exec_count
    _repeated_exec_count += 1
    return [0.1, 0.2, 0.3]


def repeated_feature_cache_hit_marker_inspect_inputs() -> Dict[str, Any]:
    _repeated_extractor.cache_clear()
    global _repeated_exec_count
    _repeated_exec_count = 0

    info = _repeated_extractor.cache_info()
    input_is_str = isinstance(SAMPLE_INPUT, str)
    try:
        hash(SAMPLE_INPUT)
        input_hashable = True
    except TypeError:
        input_hashable = False

    passed = (
        input_is_str
        and input_hashable
        and info.hits == 0
        and info.misses == 0
        and info.currsize == 0
        and _repeated_exec_count == 0
    )
    return {
        "case": "repeated_feature_cache_hit_marker",
        "method": "inspect_inputs",
        "passed": passed,
        "details": {
            "input": SAMPLE_INPUT,
            "input_is_str": input_is_str,
            "input_hashable": input_hashable,
            "cache_hits": info.hits,
            "cache_misses": info.misses,
            "cache_currsize": info.currsize,
            "exec_count": _repeated_exec_count,
        },
    }


def repeated_feature_cache_hit_marker_execute_cache() -> Dict[str, Any]:
    _repeated_extractor.cache_clear()
    global _repeated_exec_count
    _repeated_exec_count = 0

    info_before = _repeated_extractor.cache_info()
    try:
        r1 = _repeated_extractor(SAMPLE_INPUT)
        info_after_1 = _repeated_extractor.cache_info()
        exec_after_1 = _repeated_exec_count

        r2 = _repeated_extractor(SAMPLE_INPUT)
        info_after_2 = _repeated_extractor.cache_info()
        exec_after_2 = _repeated_exec_count

        values_match = (r1 == FEATURE_LIST and r2 == FEATURE_LIST)
        first_was_miss = (
            info_after_1.misses == info_before.misses + 1
            and info_after_1.hits == info_before.hits
        )
        second_was_hit = (
            info_after_2.hits == info_after_1.hits + 1
            and info_after_2.misses == info_after_1.misses
        )
        exec_ok = exec_after_1 == 1 and exec_after_2 == 1

        passed = values_match and first_was_miss and second_was_hit and exec_ok

        return {
            "case": "repeated_feature_cache_hit_marker",
            "method": "execute_cache",
            "passed": passed,
            "details": {
                "info_before": info_before._asdict(),
                "info_after_1": info_after_1._asdict(),
                "info_after_2": info_after_2._asdict(),
                "exec_after_1": exec_after_1,
                "exec_after_2": exec_after_2,
                "r1": r1,
                "r2": r2,
                "values_match": values_match,
                "first_was_miss": first_was_miss,
                "second_was_hit": second_was_hit,
                "exec_ok": exec_ok,
            },
        }
    except Exception as e:
        return {
            "case": "repeated_feature_cache_hit_marker",
            "method": "execute_cache",
            "passed": False,
            "details": {"exception": f"{type(e).__name__}: {e}"},
        }


def repeated_feature_cache_hit_marker_verify_relation() -> Dict[str, Any]:
    _repeated_extractor.cache_clear()
    global _repeated_exec_count
    _repeated_exec_count = 0

    try:
        r1 = _repeated_extractor(SAMPLE_INPUT)
        info_1 = _repeated_extractor.cache_info()
        r2 = _repeated_extractor(SAMPLE_INPUT)
        info_2 = _repeated_extractor.cache_info()

        first_miss = info_1.misses == 1 and info_1.hits == 0
        second_hit = info_2.hits == 1 and info_2.misses == 1
        exec_once = _repeated_exec_count == 1
        returns_ok = r1 == FEATURE_LIST and r2 == FEATURE_LIST

        passed = first_miss and second_hit and exec_once and returns_ok

        return {
            "case": "repeated_feature_cache_hit_marker",
            "method": "verify_relation",
            "passed": passed,
            "details": {
                "first_miss": first_miss,
                "second_hit": second_hit,
                "exec_once": exec_once,
                "returns_ok": returns_ok,
                "exec_count": _repeated_exec_count,
                "info_1": info_1._asdict(),
                "info_2": info_2._asdict(),
            },
        }
    except Exception as e:
        return {
            "case": "repeated_feature_cache_hit_marker",
            "method": "verify_relation",
            "passed": False,
            "details": {"exception": f"{type(e).__name__}: {e}"},
        }


# ----------------------------------------------------------------------
# Mutable cached return / aliasing
# ----------------------------------------------------------------------

_mutable_exec_count = 0


@lru_cache(maxsize=32)
def _mutable_extractor(x: str) -> List[float]:
    global _mutable_exec_count
    _mutable_exec_count += 1
    return [0.1, 0.2, 0.3]


def mutable_cached_return_alias_marker_inspect_inputs() -> Dict[str, Any]:
    _mutable_extractor.cache_clear()
    global _mutable_exec_count
    _mutable_exec_count = 0

    # inspect the extractor without polluting the real cache
    test_vals = [0.1, 0.2, 0.3]
    initial_ok = test_vals == FEATURE_LIST
    mutation_target_valid = len(test_vals) > 0 and isinstance(test_vals, list)

    info = _mutable_extractor.cache_info()
    passed = (
        initial_ok
        and mutation_target_valid
        and info.hits == 0
        and info.misses == 0
        and info.currsize == 0
    )
    return {
        "case": "mutable_cached_return_alias_marker",
        "method": "inspect_inputs",
        "passed": passed,
        "details": {
            "expected_initial": FEATURE_LIST,
            "initial_ok": initial_ok,
            "mutation_target_valid": mutation_target_valid,
            "cache_hits": info.hits,
            "cache_misses": info.misses,
            "cache_currsize": info.currsize,
        },
    }


def mutable_cached_return_alias_marker_execute_cache() -> Dict[str, Any]:
    _mutable_extractor.cache_clear()
    global _mutable_exec_count
    _mutable_exec_count = 0

    try:
        r1 = _mutable_extractor(SAMPLE_INPUT)
        exec_after_1 = _mutable_exec_count
        info_after_1 = _mutable_extractor.cache_info()

        # caller mutates
        r1[0] = 9.9
        mutation_applied = r1[0] == 9.9

        r2 = _mutable_extractor(SAMPLE_INPUT)
        exec_after_2 = _mutable_exec_count
        info_after_2 = _mutable_extractor.cache_info()

        same_object = r2 is r1
        mutation_visible = len(r2) > 0 and r2[0] == 9.9

        # execution happened as a cache interaction (miss then hit)
        interaction_ok = (
            info_after_1.misses == 1
            and info_after_2.hits >= 1
            and exec_after_1 == 1
        )

        passed = interaction_ok and same_object and mutation_visible and mutation_applied

        return {
            "case": "mutable_cached_return_alias_marker",
            "method": "execute_cache",
            "passed": passed,
            "details": {
                "exec_after_1": exec_after_1,
                "exec_after_2": exec_after_2,
                "info_after_1": info_after_1._asdict(),
                "info_after_2": info_after_2._asdict(),
                "same_object": same_object,
                "mutation_applied": mutation_applied,
                "mutation_visible": mutation_visible,
                "r2_first_element": r2[0] if r2 else None,
                "interaction_ok": interaction_ok,
            },
        }
    except Exception as e:
        return {
            "case": "mutable_cached_return_alias_marker",
            "method": "execute_cache",
            "passed": False,
            "details": {"exception": f"{type(e).__name__}: {e}"},
        }


def mutable_cached_return_alias_marker_verify_relation() -> Dict[str, Any]:
    _mutable_extractor.cache_clear()
    global _mutable_exec_count
    _mutable_exec_count = 0

    try:
        r1 = _mutable_extractor(SAMPLE_INPUT)
        original_first = r1[0]
        r1[0] = 9.9
        r2 = _mutable_extractor(SAMPLE_INPUT)

        same_object = r2 is r1
        mutation_visible = r2[0] == 9.9

        passed = same_object and mutation_visible and original_first == 0.1

        return {
            "case": "mutable_cached_return_alias_marker",
            "method": "verify_relation",
            "passed": passed,
            "details": {
                "same_object": same_object,
                "mutation_visible": mutation_visible,
                "original_first": original_first,
                "mutated_first": r2[0] if r2 else None,
            },
        }
    except Exception as e:
        return {
            "case": "mutable_cached_return_alias_marker",
            "method": "verify_relation",
            "passed": False,
            "details": {"exception": f"{type(e).__name__}: {e}"},
        }


# ----------------------------------------------------------------------
# Immutable cached tuple
# ----------------------------------------------------------------------

_immutable_exec_count = 0


@lru_cache(maxsize=32)
def _immutable_extractor(x: str):
    global _immutable_exec_count
    _immutable_exec_count += 1
    return (0.1, 0.2, 0.3)


def immutable_cached_tuple_marker_inspect_inputs() -> Dict[str, Any]:
    _immutable_extractor.cache_clear()
    global _immutable_exec_count
    _immutable_exec_count = 0

    info = _immutable_extractor.cache_info()

    # check extractor returns expected tuple
    # do a dry call then clear so inspect doesn't pollute case state
    # actually: we want to inspect without side effects, so check constants
    returns_tuple = isinstance(FEATURE_TUPLE, tuple)
    values_ok = FEATURE_TUPLE == (0.1, 0.2, 0.3)

    passed = (
        returns_tuple
        and values_ok
        and info.hits == 0
        and info.misses == 0
        and info.currsize == 0
        and _immutable_exec_count == 0
    )
    return {
        "case": "immutable_cached_tuple_marker",
        "method": "inspect_inputs",
        "passed": passed,
        "details": {
            "returns_tuple": returns_tuple,
            "values_ok": values_ok,
            "expected": list(FEATURE_TUPLE),
            "cache_hits": info.hits,
            "cache_misses": info.misses,
            "cache_currsize": info.currsize,
            "exec_count": _immutable_exec_count,
        },
    }


def immutable_cached_tuple_marker_execute_cache() -> Dict[str, Any]:
    _immutable_extractor.cache_clear()
    global _immutable_exec_count
    _immutable_exec_count = 0

    try:
        info_before = _immutable_extractor.cache_info()
        r1 = _immutable_extractor(SAMPLE_INPUT)
        info_after_1 = _immutable_extractor.cache_info()
        exec_after_1 = _immutable_exec_count

        r2 = _immutable_extractor(SAMPLE_INPUT)
        info_after_2 = _immutable_extractor.cache_info()
        exec_after_2 = _immutable_exec_count

        values_ok = r1 == FEATURE_TUPLE and r2 == FEATURE_TUPLE
        first_miss = info_after_1.misses == info_before.misses + 1
        second_hit = info_after_2.hits == info_after_1.hits + 1

        # check immutability: item assignment raises TypeError
        try:
            r1[0] = 9.9  # type: ignore[index]
            immutability_rejected = False
        except TypeError:
            immutability_rejected = True

        passed = values_ok and first_miss and second_hit and immutability_rejected

        return {
            "case": "immutable_cached_tuple_marker",
            "method": "execute_cache",
            "passed": passed,
            "details": {
                "info_before": info_before._asdict(),
                "info_after_1": info_after_1._asdict(),
                "info_after_2": info_after_2._asdict(),
                "exec_after_1": exec_after_1,
                "exec_after_2": exec_after_2,
                "r1": list(r1),
                "r2": list(r2),
                "values_ok": values_ok,
                "first_miss": first_miss,
                "second_hit": second_hit,
                "immutability_rejected": immutability_rejected,
            },
        }
    except Exception as e:
        return {
            "case": "immutable_cached_tuple_marker",
            "method": "execute_cache",
            "passed": False,
            "details": {"exception": f"{type(e).__name__}: {e}"},
        }


def immutable_cached_tuple_marker_verify_relation() -> Dict[str, Any]:
    _immutable_extractor.cache_clear()
    global _immutable_exec_count
    _immutable_exec_count = 0

    try:
        r1 = _immutable_extractor(SAMPLE_INPUT)
        r2 = _immutable_extractor(SAMPLE_INPUT)

        returns_ok = r1 == FEATURE_TUPLE and r2 == FEATURE_TUPLE
        exec_once = _immutable_exec_count == 1

        try:
            r1[0] = 9.9  # type: ignore[index]
            immutability_enforced = False
        except TypeError:
            immutability_enforced = True

        info = _immutable_extractor.cache_info()
        hit_recorded = info.hits >= 1
        miss_recorded = info.misses >= 1

        passed = (
            returns_ok
            and exec_once
            and immutability_enforced
            and hit_recorded
            and miss_recorded
        )

        return {
            "case": "immutable_cached_tuple_marker",
            "method": "verify_relation",
            "passed": passed,
            "details": {
                "returns_ok": returns_ok,
                "exec_once": exec_once,
                "exec_count": _immutable_exec_count,
                "immutability_enforced": immutability_enforced,
                "hit_recorded": hit_recorded,
                "miss_recorded": miss_recorded,
                "cache_info": info._asdict(),
            },
        }
    except Exception as e:
        return {
            "case": "immutable_cached_tuple_marker",
            "method": "verify_relation",
            "passed": False,
            "details": {"exception": f"{type(e).__name__}: {e}"},
        }


# ----------------------------------------------------------------------
# Unhashable list argument
# ----------------------------------------------------------------------

_unhashable_exec_count = 0


@lru_cache(maxsize=32)
def _unhashable_extractor(x):
    global _unhashable_exec_count
    _unhashable_exec_count += 1
    return [0.1, 0.2, 0.3]


def unhashable_list_argument_marker_inspect_inputs() -> Dict[str, Any]:
    _unhashable_extractor.cache_clear()
    global _unhashable_exec_count
    _unhashable_exec_count = 0

    test_input = ["a", "b"]
    input_is_list = isinstance(test_input, list)

    try:
        hash(tuple(test_input))
        list_is_unhashable_marker = False
    except TypeError:
        list_is_unhashable_marker = True

    # confirm list itself is unhashable
    try:
        hash(test_input)
        input_hashable = True
    except TypeError:
        input_hashable = False

    info = _unhashable_extractor.cache_info()

    passed = (
        input_is_list
        and not input_hashable
        and _unhashable_exec_count == 0
        and info.hits == 0
        and info.misses == 0
    )

    return {
        "case": "unhashable_list_argument_marker",
        "method": "inspect_inputs",
        "passed": passed,
        "details": {
            "input_is_list": input_is_list,
            "input_hashable": input_hashable,
            "exec_count": _unhashable_exec_count,
            "cache_hits": info.hits,
            "cache_misses": info.misses,
            "cache_currsize": info.currsize,
        },
    }


def unhashable_list_argument_marker_execute_cache() -> Dict[str, Any]:
    _unhashable_extractor.cache_clear()
    global _unhashable_exec_count
    _unhashable_exec_count = 0

    info_before = _unhashable_extractor.cache_info()
    test_input = ["a", "b"]

    exception_type = None
    body_executed = False

    try:
        _unhashable_extractor(test_input)
        body_executed = _unhashable_exec_count > 0
        passed = False
        exception_type = None
    except TypeError as e:
        exception_type = "TypeError"
        body_executed = _unhashable_exec_count > 0
        info_after = _unhashable_extractor.cache_info()
        counters_unchanged = (
            info_after.hits == info_before.hits
            and info_after.misses == info_before.misses
        )
        passed = (not body_executed) and counters_unchanged
    except Exception as e:
        exception_type = type(e).__name__
        passed = False
        info_after = _unhashable_extractor.cache_info()
        counters_unchanged = None
    else:
        info_after = _unhashable_extractor.cache_info()
        counters_unchanged = None

    if exception_type == "TypeError":
        info_after = _unhashable_extractor.cache_info()
        counters_unchanged_val = (
            info_after.hits == info_before.hits
            and info_after.misses == info_before.misses
        )
    else:
        counters_unchanged_val = counters_unchanged

    return {
        "case": "unhashable_list_argument_marker",
        "method": "execute_cache",
        "passed": passed,
        "details": {
            "exception_type": exception_type,
            "body_executed": body_executed,
            "exec_count": _unhashable_exec_count,
            "info_before": info_before._asdict(),
            "info_after": info_after._asdict()
            if "info_after" in locals()
            else None,
            "counters_unchanged": counters_unchanged_val,
        },
    }


def unhashable_list_argument_marker_verify_relation() -> Dict[str, Any]:
    _unhashable_extractor.cache_clear()
    global _unhashable_exec_count
    _unhashable_exec_count = 0

    info_before = _unhashable_extractor.cache_info()
    test_input = ["a", "b"]

    try:
        _unhashable_extractor(test_input)
        # should not reach here
        passed = False
        exception_raised = False
        exception_type = None
    except TypeError:
        exception_raised = True
        exception_type = "TypeError"
        body_did_not_execute = _unhashable_exec_count == 0
        info_after = _unhashable_extractor.cache_info()
        counters_unchanged = (
            info_after.hits == info_before.hits
            and info_after.misses == info_before.misses
        )
        passed = exception_raised and body_did_not_execute and counters_unchanged
    except Exception as e:
        passed = False
        exception_raised = True
        exception_type = type(e).__name__
        body_did_not_execute = None
        counters_unchanged = None
        info_after = _unhashable_extractor.cache_info()

    return {
        "case": "unhashable_list_argument_marker",
        "method": "verify_relation",
        "passed": passed,
        "details": {
            "exception_raised": exception_raised if "exception_raised" in locals() else False,
            "exception_type": exception_type if "exception_type" in locals() else None,
            "body_did_not_execute": body_did_not_execute
            if "body_did_not_execute" in locals()
            else None,
            "counters_unchanged": counters_unchanged
            if "counters_unchanged" in locals()
            else None,
            "exec_count": _unhashable_exec_count,
            "info_before": info_before._asdict(),
            "info_after": info_after._asdict()
            if "info_after" in locals()
            else None,
        },
    }


# ----------------------------------------------------------------------
# Dispatcher / CLI
# ----------------------------------------------------------------------

CASES = [
    "repeated_feature_cache_hit_marker",
    "mutable_cached_return_alias_marker",
    "immutable_cached_tuple_marker",
    "unhashable_list_argument_marker",
]

METHODS = ["inspect_inputs", "execute_cache", "verify_relation"]

DISPATCH = {
    ("repeated_feature_cache_hit_marker", "inspect_inputs"): repeated_feature_cache_hit_marker_inspect_inputs,
    ("repeated_feature_cache_hit_marker", "execute_cache"): repeated_feature_cache_hit_marker_execute_cache,
    ("repeated_feature_cache_hit_marker", "verify_relation"): repeated_feature_cache_hit_marker_verify_relation,
    ("mutable_cached_return_alias_marker", "inspect_inputs"): mutable_cached_return_alias_marker_inspect_inputs,
    ("mutable_cached_return_alias_marker", "execute_cache"): mutable_cached_return_alias_marker_execute_cache,
    ("mutable_cached_return_alias_marker", "verify_relation"): mutable_cached_return_alias_marker_verify_relation,
    ("immutable_cached_tuple_marker", "inspect_inputs"): immutable_cached_tuple_marker_inspect_inputs,
    ("immutable_cached_tuple_marker", "execute_cache"): immutable_cached_tuple_marker_execute_cache,
    ("immutable_cached_tuple_marker", "verify_relation"): immutable_cached_tuple_marker_verify_relation,
    ("unhashable_list_argument_marker", "inspect_inputs"): unhashable_list_argument_marker_inspect_inputs,
    ("unhashable_list_argument_marker", "execute_cache"): unhashable_list_argument_marker_execute_cache,
    ("unhashable_list_argument_marker", "verify_relation"): unhashable_list_argument_marker_verify_relation,
}


def run_all() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case in CASES:
        for method in METHODS:
            fn = DISPATCH[(case, method)]
            row = fn()
            # sanity: case/method labels match
            assert row["case"] == case
            assert row["method"] == method
            rows.append(row)
    return rows


def main() -> int:
    rows = run_all()

    # observations.json
    with open("observations.json", "w") as f:
        json.dump(rows, f, indent=2)

    # RESULTS.md
    with open("RESULTS.md", "w") as f:
        f.write("# RESULTS\n\n")
        f.write("| # | case | method | passed |\n")
        f.write("|---|------|--------|--------|\n")
        for i, r in enumerate(rows, 1):
            f.write(
                f"| {i} | {r['case']} | {r['method']} | {r['passed']} |\n"
            )
        passed_count = sum(1 for r in rows if r["passed"])
        f.write(f"\nPassed: {passed_count}/{len(rows)}\n")

    print(f"wrote {len(rows)} rows, {passed_count} passed")
    for i, r in enumerate(rows, 1):
        status = "PASS" if r["passed"] else "FAIL"
        print(f"{i:2d}. {r['case']} / {r['method']} … {status}")

    return 0 if passed_count == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
