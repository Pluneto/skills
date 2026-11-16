"""Tests for compaction_replay.py's pure parts, on synthetic data.
Run: python3 -m unittest discover -s plugins/t3code/evals"""
import json
import unittest

import compaction_replay as replay


def assistant(msg_id, blocks, tokens=1000, sidechain=False):
    return json.dumps({"type": "assistant", "isSidechain": sidechain, "sessionId": "old", "timestamp": "t",
                       "message": {"id": msg_id, "content": blocks, "usage": {"input_tokens": 1, "cache_read_input_tokens": tokens}}})


def user(blocks):
    return json.dumps({"type": "user", "sessionId": "old", "message": {"content": blocks}})


TEXT = [{"type": "text", "text": "done"}]
USE = [{"type": "tool_use", "id": "toolu_1", "name": "Bash", "input": {}}]
RESULT = [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "ok"}]


class Scoring(unittest.TestCase):
    def test_all_strings_must_appear_ignoring_case_and_markup(self):
        self.assertEqual(replay.score_probe("The **Alpha-7** task and `beta`", ["alpha-7", "BETA"]), (True, []))
        self.assertEqual(replay.score_probe("only alpha-7", ["alpha-7", "beta"]), (False, ["beta"]))

    def test_alternatives_with_a_bar(self):
        self.assertTrue(replay.score_probe("ran the R9 step", ["price watch|R9"])[0])
        self.assertFalse(replay.score_probe("nothing", ["price watch|R9"])[0])

    def test_missing_answer_fails_with_everything_missing(self):
        self.assertEqual(replay.score_probe(None, ["a", "b"]), (False, ["a", "b"]))

    def test_split_answers_by_label_across_lines_and_bold(self):
        text = "A1: first\nmore of one\n**A2:** second\nA10) tenth"
        self.assertEqual(replay.split_answers(text), {1: "first\nmore of one", 2: "second", 10: "tenth"})

    def test_score_answers_counts_passes(self):
        probes = [{"q": "x", "all": ["one"]}, {"q": "y", "all": ["two"]}, {"q": "z", "all": ["three"]}]
        rows = replay.score_answers("A1: one\nA2: nope", probes)
        self.assertEqual([row["passed"] for row in rows], [True, False, False])
        self.assertEqual(rows[2]["answer"], None)


class Transcript(unittest.TestCase):
    def test_context_size_adds_the_three_input_counts(self):
        self.assertEqual(replay.context_size({"input_tokens": 1, "cache_read_input_tokens": 20, "cache_creation_input_tokens": 300,
                                              "output_tokens": 9}), 321)

    def test_calls_skip_sidechains_and_repeat_message_ids(self):
        lines = [assistant("m1", USE, 10), assistant("m1", TEXT, 10), assistant("s", TEXT, 99, sidechain=True),
                 assistant("m2", TEXT, 20)]
        self.assertEqual([size for _, _, size in replay.assistant_calls(lines)], [11, 21])

    def test_clean_cut_ends_in_text_and_has_no_open_tool_call(self):
        lines = [assistant("m1", USE), user(RESULT), assistant("m2", TEXT)]
        self.assertEqual(replay.dangling_tool_calls(lines), set())
        self.assertEqual(replay.dangling_tool_calls(lines[:1]), {"toolu_1"})
        self.assertTrue(replay.ends_in_text(json.loads(lines[2])))
        self.assertFalse(replay.ends_in_text(json.loads(lines[0])))

    def test_fork_renames_the_session_and_cuts(self):
        lines = [user(TEXT), assistant("m1", TEXT), assistant("m2", TEXT)]
        forked = replay.fork_transcript(lines, 2, "new-id").splitlines()
        self.assertEqual(len(forked), 2)
        self.assertTrue(all(json.loads(line)["sessionId"] == "new-id" for line in forked))

    def test_fork_refuses_a_cut_inside_a_tool_call(self):
        with self.assertRaises(SystemExit):
            replay.fork_transcript([assistant("m1", USE), user(RESULT)], 1, "new-id")

    def test_project_slug_replaces_every_non_alphanumeric(self):
        self.assertEqual(replay.project_slug("/a/.b_c/d"), "-a--b-c-d")


class Stream(unittest.TestCase):
    def test_first_call_after_the_boundary_and_its_metadata(self):
        import os
        import tempfile
        events = [
            {"type": "system", "subtype": "init", "tools": ["Read", "mcp__x__y"]},
            {"type": "assistant", "message": {"id": "a", "content": [], "usage": {"input_tokens": 500}}},
            {"type": "system", "subtype": "compact_boundary", "compact_metadata": {"trigger": "manual", "pre_tokens": 500, "post_tokens": 7}},
            {"type": "assistant", "message": {"id": "b", "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "p"}}],
                                              "usage": {"input_tokens": 40}}},
            {"type": "assistant", "message": {"id": "c", "content": [], "usage": {"input_tokens": 60}}},
            {"type": "result", "result": "A1: ok"},
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as handle:
            handle.write("\n".join(json.dumps(event) for event in events))
        try:
            info = replay.analyse_stream(handle.name)
        finally:
            os.unlink(handle.name)
        self.assertEqual(info["after_boundary"], 40)
        self.assertEqual(info["boundary"], {"trigger": "manual", "pre_tokens": 500, "post_tokens": 7})
        self.assertEqual(info["tool_uses"][0]["name"], "Read")
        self.assertEqual(info["final_text"], "A1: ok")
        self.assertFalse(info["nudge_fired"])


if __name__ == "__main__":
    unittest.main()
