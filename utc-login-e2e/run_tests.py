"""Chạy Selenium unittest và luôn xuất báo cáo kết quả HTML."""

import argparse
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from time import perf_counter
import unittest
import webbrowser

from e2e.reporting import HtmlTestResult, write_html_report


def main():
    project = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Chạy test Selenium và xuất báo cáo HTML")
    parser.add_argument("--test", action="append", help="Tên test unittest; có thể dùng nhiều lần")
    parser.add_argument("--report", type=Path, default=project / "artifacts/report.html", help="Đường dẫn file báo cáo")
    parser.add_argument("--open", action="store_true", help="Mở báo cáo trong trình duyệt sau khi chạy")
    args = parser.parse_args()
    loader = unittest.TestLoader()
    suite = (loader.loadTestsFromNames(args.test) if args.test else
             loader.discover(str(project / "e2e/tests"), top_level_dir=str(project)))
    if suite.countTestCases() == 0:
        parser.error("Không tìm thấy test case để chạy")
    started_at = datetime.now(timezone(timedelta(hours=7)))
    start = perf_counter()
    result = unittest.TextTestRunner(verbosity=2, resultclass=HtmlTestResult).run(suite)
    output = write_html_report(
        result, args.report, started_at, perf_counter() - start,
        os.getenv("BROWSER", "chrome"), os.getenv("HEADLESS", "1") == "1",
    )
    print(f"\nBáo cáo HTML: {output}")
    if args.open:
        webbrowser.open(output.as_uri())
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
