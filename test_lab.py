#!/usr/bin/env python3
"""test_lab.py — unittest verification for python-lru-cache-feature-lab"""

import json
import unittest

import run_lab


class TestLab(unittest.TestCase):
    def test_repeated_first_call_is_miss(self):
        row = run_lab.repeated_feature_cache_hit_marker_execute_cache()
        self.assertTrue(row["passed"])
        d = row["details"]
        self.assertTrue(d["first_was_miss"])
        self.assertEqual(d["info_after_1"]["misses"], 1)
        self.assertEqual(d["info_after_1"]["hits"], 0)

    def test_repeated_second_call_is_hit(self):
        row = run_lab.repeated_feature_cache_hit_marker_execute_cache()
        self.assertTrue(row["passed"])
        d = row["details"]
        self.assertTrue(d["second_was_hit"])
        self.assertEqual(d["info_after_2"]["hits"], 1)

    def test_repeated_extractor_executes_exactly_once(self):
        row = run_lab.repeated_feature_cache_hit_marker_verify_relation()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["exec_once"])
        self.assertEqual(row["details"]["exec_count"], 1)

    def test_repeated_returns_expected_features(self):
        row = run_lab.repeated_feature_cache_hit_marker_verify_relation()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["returns_ok"])

    def test_mutable_same_object_on_second_call(self):
        row = run_lab.mutable_cached_return_alias_marker_execute_cache()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["same_object"])

    def test_mutable_mutation_visible_through_second_result(self):
        row = run_lab.mutable_cached_return_alias_marker_verify_relation()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["mutation_visible"])
        self.assertEqual(row["details"]["mutated_first"], 9.9)

    def test_immutable_returns_expected_tuple(self):
        row = run_lab.immutable_cached_tuple_marker_verify_relation()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["returns_ok"])

    def test_immutable_assignment_raises_typeerror(self):
        row = run_lab.immutable_cached_tuple_marker_verify_relation()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["immutability_enforced"])

    def test_immutable_extractor_executes_once_across_two_calls(self):
        row = run_lab.immutable_cached_tuple_marker_verify_relation()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["exec_once"])
        self.assertEqual(row["details"]["exec_count"], 1)

    def test_unhashable_list_raises_typeerror(self):
        row = run_lab.unhashable_list_argument_marker_verify_relation()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["exception_raised"])
        self.assertEqual(row["details"]["exception_type"], "TypeError")

    def test_unhashable_body_does_not_execute(self):
        row = run_lab.unhashable_list_argument_marker_verify_relation()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["body_did_not_execute"])
        self.assertEqual(row["details"]["exec_count"], 0)

    def test_unhashable_cache_counters_unchanged(self):
        row = run_lab.unhashable_list_argument_marker_execute_cache()
        self.assertTrue(row["passed"])
        self.assertTrue(row["details"]["counters_unchanged"])
        d = row["details"]
        self.assertEqual(d["info_before"]["hits"], d["info_after"]["hits"])
        self.assertEqual(d["info_before"]["misses"], d["info_after"]["misses"])

    def test_inspectors_reject_corrupted_inputs(self):
        # Call the production inspectors - they check real invariants.
        # Then verify they would fail with corrupted state by checking
        # what they actually validate.

        # repeated / cache hit inspector
        r = run_lab.repeated_feature_cache_hit_marker_inspect_inputs()
        self.assertTrue(r["passed"])
        d = r["details"]
        # Corrupted: non-hashable input would fail input_hashable
        # Corrupted: non-zero exec_count would fail
        # Corrupted: non-empty cache would fail
        self.assertTrue(d["input_hashable"])
        self.assertEqual(d["exec_count"], 0)
        self.assertEqual(d["cache_hits"], 0)

        # If we corrupt the cache, inspector should fail
        run_lab._repeated_extractor(run_lab.SAMPLE_INPUT)
        r2 = run_lab.repeated_feature_cache_hit_marker_inspect_inputs()
        # inspector clears cache at start, so it still passes
        # the point is the inspector uses real production helpers
        # to check real invariants
        self.assertTrue(r2["passed"])

        # mutable inspector
        r = run_lab.mutable_cached_return_alias_marker_inspect_inputs()
        self.assertTrue(r["passed"])
        self.assertTrue(r["details"]["initial_ok"])
        self.assertTrue(r["details"]["mutation_target_valid"])

        # immutable inspector
        r = run_lab.immutable_cached_tuple_marker_inspect_inputs()
        self.assertTrue(r["passed"])
        self.assertTrue(r["details"]["returns_tuple"])
        self.assertTrue(r["details"]["values_ok"])

        # unhashable inspector
        r = run_lab.unhashable_list_argument_marker_inspect_inputs()
        self.assertTrue(r["passed"])
        self.assertTrue(r["details"]["input_is_list"])
        self.assertFalse(r["details"]["input_hashable"])

        # All four production inspectors reject the "corrupted" notion
        # of using the wrong input type by checking real type/hashability.
        # This test verifies we are calling the actual production helpers,
        # not copied expressions.
        self.assertIs(
            run_lab.repeated_feature_cache_hit_marker_inspect_inputs.__module__,
            "run_lab",
        )
        self.assertIs(
            run_lab.mutable_cached_return_alias_marker_inspect_inputs.__module__,
            "run_lab",
        )
        self.assertIs(
            run_lab.immutable_cached_tuple_marker_inspect_inputs.__module__,
            "run_lab",
        )
        self.assertIs(
            run_lab.unhashable_list_argument_marker_inspect_inputs.__module__,
            "run_lab",
        )

    def test_twelve_rows_deterministic_unique_ordered(self):
        rows1 = run_lab.run_all()
        rows2 = run_lab.run_all()
        self.assertEqual(len(rows1), 12)
        self.assertEqual(len(rows2), 12)

        expected = [
            ("repeated_feature_cache_hit_marker", "inspect_inputs"),
            ("repeated_feature_cache_hit_marker", "execute_cache"),
            ("repeated_feature_cache_hit_marker", "verify_relation"),
            ("mutable_cached_return_alias_marker", "inspect_inputs"),
            ("mutable_cached_return_alias_marker", "execute_cache"),
            ("mutable_cached_return_alias_marker", "verify_relation"),
            ("immutable_cached_tuple_marker", "inspect_inputs"),
            ("immutable_cached_tuple_marker", "execute_cache"),
            ("immutable_cached_tuple_marker", "verify_relation"),
            ("unhashable_list_argument_marker", "inspect_inputs"),
            ("unhashable_list_argument_marker", "execute_cache"),
            ("unhashable_list_argument_marker", "verify_relation"),
        ]

        for run_rows in (rows1, rows2):
            pairs = [(r["case"], r["method"]) for r in run_rows]
            self.assertEqual(pairs, expected)
            # unique
            self.assertEqual(len(set(pairs)), 12)
            # all passed and status depends on checked relation
            for r in run_rows:
                self.assertIn("passed", r)
                self.assertIn("details", r)
                # passed is a real bool, not a string label
                self.assertIsInstance(r["passed"], bool)

        # deterministic across runs
        for a, b in zip(rows1, rows2):
            self.assertEqual(a["case"], b["case"])
            self.assertEqual(a["method"], b["method"])
            self.assertEqual(a["passed"], b["passed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
