"""Kiểm tra báo cáo bằng test giả lập, không gửi yêu cầu đăng nhập."""

from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from e2e.reporting import HtmlTestResult, write_html_report


class ReportingTests(unittest.TestCase):
    def run_sample(self, case):
        return unittest.TextTestRunner(
            stream=StringIO(), resultclass=HtmlTestResult,
        ).run(unittest.defaultTestLoader.loadTestsFromTestCase(case))

    def test_statuses_and_escaped_html(self):
        class Sample(unittest.TestCase):
            def test_pass(self):
                """<script>alert('test')</script>"""
                pass

            def test_fail(self):
                self.fail("<b>assertion failed</b>")

            def test_error(self):
                raise RuntimeError("Execution failed")

            @unittest.skip("Không chạy mẫu")
            def test_skip(self):
                pass

            @unittest.expectedFailure
            def test_xfail(self):
                self.fail("Expected failure")

            @unittest.expectedFailure
            def test_xpass(self):
                pass

        result = self.run_sample(Sample)
        self.assertEqual(result.testsRun, 6)
        self.assertEqual({r["status"] for r in result.records}, {"PASS", "FAIL", "ERROR", "SKIP", "XFAIL", "XPASS"})
        self.assertFalse(result.wasSuccessful())
        with TemporaryDirectory() as directory:
            output = write_html_report(result, Path(directory) / "nested/report.html",
                                       datetime(2026, 10, 8, 0, tzinfo=timezone.utc), 1.25, "chrome", True)
            html = output.read_text(encoding="utf-8")
        self.assertIn("08/10/2026 07:00:00 (UTC+7)", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;b&gt;assertion failed&lt;/b&gt;", html)
        self.assertEqual(html.count('<tr data-status='), 6)
        self.assertTrue(all(r["duration"] >= 0 for r in result.records))

    def test_subtest_failure_is_not_reported_as_pass(self):
        class Sample(unittest.TestCase):
            def test_subtests(self):
                with self.subTest(value=1):
                    self.assertEqual(1, 2)
        result = self.run_sample(Sample)
        self.assertEqual(result.records[0]["status"], "FAIL")

    def test_class_setup_error_is_reported(self):
        class Sample(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                raise RuntimeError("Setup failed")

            def test_never_runs(self):
                pass
        result = self.run_sample(Sample)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(result.records[0]["status"], "ERROR")
        self.assertIn("Setup failed", result.records[0]["details"][0])
