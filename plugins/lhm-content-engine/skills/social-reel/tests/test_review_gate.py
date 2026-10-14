import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('review_gate', Path(__file__).parents[1] / 'scripts/review_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class ReviewGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write('script.json', ['A practical clinic tip.'])
        self.write('voice.json', {'engine': 'local', 'model': 'test', 'references': ['ref.wav'], 'playback_rate': 1.5})
        self.write('audio-manifest.json', {'audio': ['speech.wav']})
        (self.root / 'ref.wav').write_bytes(b'reference')
        (self.root / 'speech.wav').write_bytes(b'narration')

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value))

    def approve(self):
        return gate.approve(self.root, 'Michael', 'Approved this script and audio draft')

    def test_missing_approval_stops_build(self):
        with self.assertRaises(ValueError):
            gate.check(self.root)

    def test_exact_approval_passes_without_publication(self):
        self.approve()
        self.assertEqual(gate.check(self.root)['publication'], 'not_authorised')

    def test_changed_script_invalidates(self):
        self.approve()
        self.write('script.json', ['Changed hook.'])
        with self.assertRaisesRegex(ValueError, 'stale'):
            gate.check(self.root)

    def test_changed_audio_or_reference_invalidates(self):
        for name in ['speech.wav', 'ref.wav']:
            with self.subTest(name=name):
                self.approve()
                (self.root / name).write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'stale'):
                    gate.check(self.root)

    def test_speed_change_invalidates(self):
        self.approve()
        self.write('voice.json', {'engine': 'local', 'model': 'test', 'playback_rate': 1.2})
        with self.assertRaisesRegex(ValueError, 'stale'):
            gate.check(self.root)

    def test_visual_change_does_not_invalidate(self):
        self.approve()
        (self.root / 'visual-plan.json').write_text('{"colour":"orange"}')
        self.assertEqual(gate.check(self.root)['state'], 'script_audio_approved')

    def test_external_audio_is_rejected(self):
        self.write('audio-manifest.json', {'audio': ['../outside.wav']})
        with self.assertRaises(ValueError):
            self.approve()


if __name__ == '__main__':
    unittest.main()
