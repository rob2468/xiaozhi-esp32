import pathlib
import shutil
import subprocess
import tempfile
import unittest


class KeywordTurnTest(unittest.TestCase):
    def test_turn_lifecycle_and_interruption(self):
        compiler = shutil.which("c++")
        self.assertIsNotNone(compiler, "A host C++ compiler is required")
        root = pathlib.Path(__file__).resolve().parents[2]
        source = r'''
#include "keyword_turn.h"
#include <cassert>
int main() {
    KeywordTurn turn;
    // Unsolicited server greetings cannot start playback in standby.
    assert(!turn.StartReply());
    assert(!turn.AcceptTranscript());
    turn.Wake();
    assert(turn.IsListening());
    // A delayed reply from an aborted turn must not interrupt new capture.
    assert(!turn.StartReply());
    assert(turn.AcceptTranscript());
    assert(!turn.IsListening());
    assert(!turn.AcceptTranscript());
    assert(turn.StartReply());
    assert(!turn.StartReply());
    // Playback gaps before TTS stop must not end the turn.
    assert(!turn.FinishPlayback(true));
    turn.StopReply();
    assert(!turn.FinishPlayback(false));
    assert(turn.FinishPlayback(true));
    assert(!turn.StartReply());
    // Wake during draining cancels the old completion.
    turn.Wake();
    assert(turn.AcceptTranscript());
    assert(turn.StartReply());
    turn.StopReply();
    turn.Wake();
    assert(!turn.FinishPlayback(true));
    turn.StopReply();
    assert(turn.IsListening());
    // Disconnect/error clears the armed turn.
    turn.Reset();
    assert(!turn.AcceptTranscript());
    assert(!turn.StartReply());
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            cpp = pathlib.Path(tmp) / "test.cc"
            binary = pathlib.Path(tmp) / "test"
            cpp.write_text(source)
            subprocess.run([compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                            "-I", str(root / "main"), str(cpp), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
