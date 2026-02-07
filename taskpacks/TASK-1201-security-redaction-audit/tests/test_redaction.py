import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def _redact_with_evidence():
    from src.redaction import redact_with_evidence
    return redact_with_evidence


class TestRedaction(unittest.TestCase):
    def test_redacts_expected_patterns(self) -> None:
        text = "email a@b.com ip 192.0.2.1 token ABCDEFGHIJKLMNOPQRST"
        res = _redact_with_evidence()(text)
        self.assertIn("[REDACTED_EMAIL]", res.redacted_text)
        self.assertIn("[REDACTED_IPV4]", res.redacted_text)
        self.assertIn("[REDACTED_TOKEN]", res.redacted_text)
        self.assertEqual(res.counts["email"], 1)
        self.assertEqual(res.counts["ipv4"], 1)
        self.assertEqual(res.counts["token"], 1)

    def test_hashes_present(self) -> None:
        res = _redact_with_evidence()("x")
        self.assertEqual(len(res.input_sha256), 64)
        self.assertEqual(len(res.output_sha256), 64)
