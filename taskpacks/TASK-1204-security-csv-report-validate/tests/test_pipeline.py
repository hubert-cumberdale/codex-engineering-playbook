import pathlib
import unittest
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import read_csv, summarize  # noqa: E402


class TestPipeline(unittest.TestCase):
    def test_read_csv_and_hash(self) -> None:
        csv_path = ROOT / "data" / "sample_coverage.csv"
        rows, digest = read_csv(str(csv_path))
        self.assertTrue(rows)
        self.assertEqual(len(digest), 64)

    def test_summarize_counts(self) -> None:
        csv_path = ROOT / "data" / "sample_coverage.csv"
        rows, _ = read_csv(str(csv_path))
        summ = summarize(rows)
        self.assertEqual(summ["total_rows"], 6)
        by_status = summ["by_status"]
        self.assertEqual(by_status["covered"], 2)
        self.assertEqual(by_status["partial"], 2)
        self.assertEqual(by_status["missing"], 2)
