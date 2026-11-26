"""Tests for pin.py, driven through its public seam: hook input JSON on stdin and the environment in,
hook stdout and the pin files in the plugin data folder out.
Run: python3 -m unittest discover -s plugins/pin/hooks"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "pin.py"
SID = "11111111-1111-1111-1111-111111111111"
LIMIT = 9500


def utf16_len(text):
    return len(text.encode("utf-16-le")) // 2


class PinTestCase(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.TemporaryDirectory()
        self.addCleanup(self.data.cleanup)
        self.env = {k: v for k, v in os.environ.items() if k not in ("T3CODE_THREAD_ID", "CLAUDE_PLUGIN_DATA")}
        self.env["CLAUDE_PLUGIN_DATA"] = self.data.name

    def run_hook(self, payload, env=None, raw=None):
        stdin = raw if raw is not None else json.dumps(payload)
        run = subprocess.run([sys.executable, str(SCRIPT)], input=stdin, capture_output=True, text=True,
                             env=env or self.env)
        self.assertEqual(run.returncode, 0, run.stderr)
        return run.stdout

    def context(self, stdout):
        """The additionalContext of a hook's JSON output, or None when it printed nothing."""
        return json.loads(stdout)["hookSpecificOutput"]["additionalContext"] if stdout.strip() else None

    def submit(self, prompt, session_id=SID, env=None, **extra):
        out = self.run_hook({"hook_event_name": "UserPromptSubmit", "session_id": session_id, "prompt": prompt, **extra}, env)
        return self.context(out)

    def compact(self, session_id=SID, env=None, **extra):
        out = self.run_hook({"hook_event_name": "SessionStart", "source": "compact", "session_id": session_id, **extra}, env)
        return self.context(out)

    def pin_files(self):
        return sorted(Path(self.data.name).glob("*.txt"))

    def pinned_text(self):
        (path,) = self.pin_files()
        return path.read_bytes().decode("utf-8")


class CaptureAndReinject(PinTestCase):
    def test_text_below_the_marker_comes_back_after_compaction_byte_for_byte(self):
        rules = "1. No code comments.\n2.  Keep   spacing, ünïcode and trailing space \n\n3. Last rule"
        self.submit(f"Please build the thing.\n#pin\n{rules}")
        self.assertEqual(self.pinned_text(), rules)
        injected = self.compact()
        self.assertTrue(injected.endswith("\n\n" + rules))
        self.assertIn("the user set these instructions earlier in this thread", injected.splitlines()[0])

    def test_a_message_that_starts_with_a_slash_command_can_pin(self):
        self.submit("/some-skill with args\n#pin\nrule")
        self.assertEqual(self.pinned_text(), "rule")

    def test_crlf_line_ends_do_not_leave_a_stray_carriage_return_at_the_ends(self):
        self.submit("task\r\n#pin\r\nfirst\r\nsecond\r\n")
        self.assertEqual(self.pinned_text(), "first\r\nsecond")
        self.assertTrue(self.compact().endswith("\n\nfirst\r\nsecond"))

    def test_text_above_the_marker_is_not_pinned(self):
        self.submit("task text\n#pin\nrule")
        self.assertNotIn("task text", self.pinned_text())

    def test_marker_is_case_insensitive_and_must_be_alone_on_its_line(self):
        self.submit("#PIN\nupper")
        self.assertEqual(self.pinned_text(), "upper")
        self.submit("see #pin in the docs\nnot a marker", session_id="other")
        self.assertEqual(len(self.pin_files()), 1)

    def test_message_without_marker_changes_nothing_and_prints_nothing(self):
        self.assertIsNone(self.submit("just a question"))
        self.assertEqual(self.pin_files(), [])

    def test_no_pin_file_means_no_injection(self):
        self.assertIsNone(self.compact())

    def test_the_capturing_turn_tells_the_agent_what_was_stored(self):
        note = self.submit("#pin\nrule one\nrule two")
        self.assertIn("2 lines", note)
        self.assertIn("rule one", note)
        self.assertIn("one line", note)

    def test_non_compact_session_start_injects_nothing(self):
        self.submit("#pin\nrule")
        out = self.run_hook({"hook_event_name": "SessionStart", "source": "startup", "session_id": SID})
        self.assertEqual(out, "")


class AddAndClear(PinTestCase):
    def test_a_second_pin_is_added_below_the_first(self):
        self.submit("#pin\nfirst rule")
        self.submit("more\n#pin\nsecond rule")
        self.assertEqual(self.pinned_text(), "first rule\n\nsecond rule")
        self.assertTrue(self.compact().endswith("first rule\n\nsecond rule"))

    def test_a_second_marker_in_one_message_keeps_the_text_in_between(self):
        self.submit("#pin\nfirst\n#pin\nsecond")
        self.assertEqual(self.pinned_text(), "first\nsecond")

    def test_unpin_clears_the_pin_and_says_so(self):
        self.submit("#pin\nrule")
        note = self.submit("changed my mind\n#unpin")
        self.assertIn("cleared", note)
        self.assertEqual(self.pin_files(), [])
        self.assertIsNone(self.compact())

    def test_unpin_without_a_pin_prints_nothing(self):
        self.assertIsNone(self.submit("#unpin"))

    def test_unpin_then_pin_in_one_message_replaces_the_pin(self):
        self.submit("#pin\nold rule")
        self.submit("#unpin\n#pin\nnew rule")
        self.assertEqual(self.pinned_text(), "new rule")

    def test_text_after_unpin_is_not_pinned(self):
        self.submit("#pin\nold rule")
        self.submit("#unpin\nthis is a normal request")
        self.assertEqual(self.pin_files(), [])

    def test_a_pin_stays_until_unpin_however_old(self):
        self.submit("#pin\nrule")
        (path,) = self.pin_files()
        os.utime(path, (0, 0))
        self.assertTrue(self.compact().endswith("rule"))


class Budget(PinTestCase):
    def room(self):
        """How many ASCII characters of pin still fit in the budget next to the header."""
        self.submit("#pin\nx")
        return LIMIT - utf16_len(self.compact()) + 1

    def test_a_pin_that_exactly_fits_is_not_cut(self):
        pin = "a" * self.room()
        self.submit(f"#pin\n{pin}", session_id="fit")
        injected = self.compact(session_id="fit")
        self.assertEqual(utf16_len(injected), LIMIT)
        self.assertTrue(injected.endswith(pin))
        self.assertNotIn("cut", injected.lower())

    def test_a_pin_one_unit_over_the_budget_is_cut(self):
        pin = "a" * (self.room() + 1)
        self.submit(f"#pin\n{pin}", session_id="over")
        injected = self.compact(session_id="over")
        self.assertLessEqual(utf16_len(injected), LIMIT)
        self.assertIn("cut", injected.lower())

    def test_a_longer_pin_is_cut_with_a_note_and_the_file_path(self):
        pin = "".join(f"rule {n}\n" for n in range(3000)).strip()
        self.submit(f"#pin\n{pin}")
        injected = self.compact()
        (path,) = self.pin_files()
        self.assertLessEqual(utf16_len(injected), LIMIT)
        self.assertIn("cut", injected.lower())
        self.assertIn(str(path), injected)
        self.assertIn("rule 0\nrule 1\nrule 2\n", injected)
        self.assertEqual(path.read_bytes().decode("utf-8"), pin)

    def test_the_budget_counts_utf16_code_units_so_emoji_count_twice(self):
        pin = "\U0001F600" * 6000
        self.submit(f"#pin\n{pin}")
        injected = self.compact()
        self.assertLessEqual(utf16_len(injected), LIMIT)
        self.assertGreater(len(injected), 1000)
        self.assertIn("cut", injected.lower())
        self.assertIn("\U0001F600" * 100, injected)
        self.assertTrue(pin.startswith(injected.split("\n\n", 1)[1]))


class WhoseThread(PinTestCase):
    def with_thread(self, thread):
        return {**self.env, "T3CODE_THREAD_ID": thread}

    def test_native_sub_agents_neither_capture_nor_receive_the_pin(self):
        self.submit("#pin\nrule")
        self.assertIsNone(self.submit("#pin\nsub-agent rule", agent_id="agent-1"))
        self.assertIsNone(self.compact(agent_id="agent-1"))
        self.assertEqual(self.pinned_text(), "rule")

    def test_the_t3_thread_id_is_the_key_when_the_environment_has_one(self):
        env = self.with_thread("thread:abc")
        self.submit("#pin\nrule", session_id="session-1", env=env)
        self.assertTrue(self.compact(session_id="session-2", env=env).endswith("rule"))

    def test_the_session_id_is_the_key_without_a_t3_thread_id(self):
        self.submit("#pin\nrule", session_id="session-1")
        self.assertTrue(self.compact(session_id="session-1").endswith("rule"))
        self.assertIsNone(self.compact(session_id="session-2"))

    def test_any_id_gives_a_safe_file_name_inside_the_data_folder(self):
        for thread in ("thread:delegated-task:100%25/../..", "..", "a" * 400, "тред"):
            self.submit("#pin\nrule", env=self.with_thread(thread))
        names = [path.name for path in Path(self.data.name).iterdir()]
        self.assertEqual(len(names), 4)
        self.assertTrue(all("/" not in name and not name.startswith(".") for name in names))

    def test_a_parent_thread_and_its_delegated_child_never_share_a_pin(self):
        parent, child = self.with_thread("thread:parent"), self.with_thread("thread:delegated-task:child")
        self.submit("#pin\nparent rule", env=parent)
        self.assertIsNone(self.compact(env=child))
        self.submit("#pin\nchild rule", env=child)
        self.submit("#unpin", env=child)
        self.assertTrue(self.compact(env=parent).endswith("parent rule"))
        self.assertIsNone(self.compact(env=child))


class NeverFailsTheSession(PinTestCase):
    def test_malformed_input_prints_nothing(self):
        for raw in ("not json", "[1, 2]", '{"hook_event_name": "UserPromptSubmit", "prompt": 5}', ""):
            self.assertEqual(self.run_hook(None, raw=raw), "")

    def test_an_unknown_event_prints_nothing(self):
        self.assertEqual(self.run_hook({"hook_event_name": "Stop", "session_id": SID}), "")

    def test_an_unwritable_data_folder_prints_nothing(self):
        blocker = Path(self.data.name) / "file"
        blocker.write_text("")
        env = {**self.env, "CLAUDE_PLUGIN_DATA": str(blocker / "data")}
        self.assertIsNone(self.submit("#pin\nrule", env=env))
        self.assertIsNone(self.compact(env=env))

    def test_hook_input_without_any_thread_key_pins_nothing(self):
        out = self.run_hook({"hook_event_name": "UserPromptSubmit", "prompt": "#pin\nrule"})
        self.assertEqual(out, "")
        self.assertEqual(self.pin_files(), [])

    def test_a_missing_data_folder_variable_prints_nothing(self):
        env = {k: v for k, v in self.env.items() if k != "CLAUDE_PLUGIN_DATA"}
        self.assertIsNone(self.submit("#pin\nrule", env=env))


if __name__ == "__main__":
    unittest.main()
