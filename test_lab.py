#!/usr/bin/env python3
"""test_lab.py — unittest verification for python-lru-cache-feature-lab"""

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

    # ------------------------------------------------------------------
    # Corruption tests for production input-check helpers
    # ------------------------------------------------------------------

    def test_repeated_input_check_rejects_corrupted(self):
        # production helper rejects non-string input
        self.assertFalse(run_lab.check_repeated_inputs(123, 0, 0, 0, 0))
        # rejects unhashable input (list)
        self.assertFalse(run_lab.check_repeated_inputs(["x"], 0, 0, 0, 0))
        # rejects non-empty cache state
        self.assertFalse(run_lab.check_repeated_inputs("sample-1", 1, 0, 0, 0))
        self.assertFalse(run_lab.check_repeated_inputs("sample-1", 0, 1, 0, 0))
        self.assertFalse(run_lab.check_repeated_inputs("sample-1", 0, 0, 1, 0))
        # rejects non-zero exec_count
        self.assertFalse(run_lab.check_repeated_inputs("sample-1", 0, 0, 0, 1))
        # accepts valid input
        self.assertTrue(run_lab.check_repeated_inputs("sample-1", 0, 0, 0, 0))

    def test_mutable_input_check_rejects_corrupted(self):
        # production helper rejects tuple (should be list)
        self.assertFalse(run_lab.check_mutable_inputs((0.1, 0.2, 0.3), 0, 0, 0))
        # rejects wrong values
        self.assertFalse(run_lab.check_mutable_inputs([9.9, 9.9, 9.9], 0, 0, 0))
        # rejects empty list
        self.assertFalse(run_lab.check_mutable_inputs([], 0, 0, 0))
        # rejects non-empty cache
        self.assertFalse(run_lab.check_mutable_inputs([0.1, 0.2, 0.3], 1, 0, 0))
        self.assertFalse(run_lab.check_mutable_inputs([0.1, 0.2, 0.3], 0, 1, 0))
        # accepts valid input
        self.assertTrue(run_lab.check_mutable_inputs([0.1, 0.2, 0.3], 0, 0, 0))

    def test_immutable_input_check_rejects_corrupted(self):
        # production helper rejects list (should be tuple)
        self.assertFalse(run_lab.check_immutable_inputs([0.1, 0.2, 0.3], 0, 0, 0, 0))
        # rejects wrong tuple values
        self.assertFalse(run_lab.check_immutable_inputs((9.9, 9.9, 9.9), 0, 0, 0, 0))
        # rejects non-empty cache
        self.assertFalse(run_lab.check_immutable_inputs((0.1, 0.2, 0.3), 1, 0, 0, 0))
        # rejects non-zero exec_count
        self.assertFalse(run_lab.check_immutable_inputs((0.1, 0.2, 0.3), 0, 0, 0, 1))
        # accepts valid input
        self.assertTrue(run_lab.check_immutable_inputs((0.1, 0.2, 0.3), 0, 0, 0, 0))

    def test_unhashable_input_check_rejects_corrupted(self):
        # production helper rejects hashable replacement (tuple)
        self.assertFalse(run_lab.check_unhashable_inputs(("a", "b"), 0, 0, 0))
        # rejects string (hashable)
        self.assertFalse(run_lab.check_unhashable_inputs("ab", 0, 0, 0))
        # rejects non-zero exec_count
        self.assertFalse(run_lab.check_unhashable_inputs(["a", "b"], 1, 0, 0))
        # rejects non-empty cache
        self.assertFalse(run_lab.check_unhashable_inputs(["a", "b"], 0, 1, 0))
        # accepts valid input (list, unhashable)
        self.assertTrue(run_lab.check_unhashable_inputs(["a", "b"], 0, 0, 0))

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
