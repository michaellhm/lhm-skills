import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / 'assets/systemd/lhm-cto-plugin-dispatch.service'


class DispatchServiceTests(unittest.TestCase):
    def test_review_directory_with_spaces_is_quoted_as_one_path(self):
        text = SERVICE.read_text(encoding='utf-8')
        self.assertIn(
            'ReadWritePaths="/home/hermes/.hermes/profiles/lhm_brain/vault/01 Inbox/Hermes Reviews"',
            text,
        )
        self.assertNotIn('\\x20Inbox', text)
        self.assertNotIn('\\x20Reviews', text)


if __name__ == '__main__':
    unittest.main()
