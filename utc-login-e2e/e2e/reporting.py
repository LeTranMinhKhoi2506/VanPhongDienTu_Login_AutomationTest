"""Thu thập kết quả unittest và xuất báo cáo HTML độc lập."""

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from time import perf_counter
import unittest


class HtmlTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.records = []
        self._current = None

    def startTest(self, test):
        super().startTest(test)
        self._started = perf_counter()
        self._current = {
            "id": test.id(),
            "description": test.shortDescription() or test.id(),
            "status": "PASS",
            "details": [],
        }

    def _mark(self, status, detail=""):
        # Một test có thể vừa fail assertion vừa lỗi cleanup.
        priority = {"PASS": 0, "SKIP": 1, "XFAIL": 1, "XPASS": 2, "FAIL": 3, "ERROR": 4}
        if priority[status] >= priority[self._current["status"]]:
            self._current["status"] = status
        if detail:
            self._current["details"].append(detail)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._mark("FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        # Lỗi setUpClass/module không có startTest: vẫn phải xuất lỗi.
        if self._current is None:
            self.records.append({
                "id": test.id(), "description": str(test), "status": "ERROR",
                "details": [self._exc_info_to_string(err, test)], "duration": 0.0,
            })
        else:
            self._mark("ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self._current is None:
            self.records.append({
                "id": test.id(), "description": str(test), "status": "SKIP",
                "details": [reason], "duration": 0.0,
            })
        else:
            self._mark("SKIP", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._mark("XFAIL", self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._mark("XPASS", "Test được đánh dấu expectedFailure nhưng lại thành công.")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            status = "FAIL" if issubclass(err[0], test.failureException) else "ERROR"
            self._mark(status, str(subtest) + "\n" + self._exc_info_to_string(err, test))

    def stopTest(self, test):
        self._current["duration"] = perf_counter() - self._started
        self.records.append(self._current)
        self._current = None
        super().stopTest(test)


def write_html_report(result, output, started_at, elapsed, browser, headless):
    statuses = ("PASS", "FAIL", "ERROR", "SKIP", "XFAIL", "XPASS")
    counts = {status: sum(row["status"] == status for row in result.records) for status in statuses}
    cards = "".join(
        f'<div class="card"><span>{status}</span><strong class="{status}">{counts[status]}</strong></div>'
        for status in statuses
    )
    rows = []
    for row in result.records:
        details = ""
        if row["details"]:
            details = '<details><summary>Xem chi tiết</summary><pre>' + escape("\n\n".join(row["details"])) + '</pre></details>'
        rows.append(
            f'<tr data-status="{row["status"]}"><td><b>{escape(row["description"])}</b>'
            f'<small>{escape(row["id"])}</small>{details}</td>'
            f'<td><span class="badge {row["status"]}">{row["status"]}</span></td>'
            f'<td>{row["duration"]:.2f} s</td></tr>'
        )
    options = "".join(f'<option value="{status}">{status}</option>' for status in statuses)
    success = result.wasSuccessful() and result.testsRun > 0
    verdict = "Hoàn tất — đạt" if success else "Cần kiểm tra kết quả"
    timestamp = started_at.astimezone(timezone(timedelta(hours=7))).strftime("%d/%m/%Y %H:%M:%S (UTC+7)")
    document = '''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UTC Login — Báo cáo Selenium</title>
<style>
:root{font-family:Segoe UI,Arial,sans-serif;color:#18263a;background:#f2f5fa}
body{margin:0}main{max-width:1120px;margin:36px auto;padding:0 20px}
header{background:#152b48;color:white;padding:28px;border-radius:16px}
h1{margin:6px 0 12px;font-size:28px}header p{color:#d5e2f4;line-height:1.7;margin:6px 0}
.eyebrow{font-size:12px;letter-spacing:2px}.cards{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:22px 0}
.card{background:white;border:1px solid #e0e6ee;padding:18px;border-radius:12px}.card span{font-size:12px;color:#607086}
.card strong{display:block;font-size:30px;margin-top:6px}.PASS{color:#13794a}.FAIL,.ERROR,.XPASS{color:#bf2539}
.SKIP,.XFAIL{color:#916300}.controls{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}
input,select{font:inherit;padding:10px;border:1px solid #c4cfdd;border-radius:8px}input{flex:1;min-width:180px}
.table-wrap{overflow:auto;background:white;border-radius:12px;border:1px solid #e0e6ee}
table{border-collapse:collapse;width:100%}th{text-align:left;background:#e9eff7;font-size:13px}th,td{padding:16px;border-bottom:1px solid #e7ecf2}
td{vertical-align:top}td:first-child{width:75%}small{display:block;color:#64748b;margin-top:6px;overflow-wrap:anywhere}
.badge{font-size:12px;font-weight:700;white-space:nowrap}summary{cursor:pointer;color:#245fab;margin-top:12px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fa;padding:12px;border-radius:8px;font-size:12px}
.note{color:#53677f;line-height:1.6;font-size:14px}#empty{padding:16px;color:#64748b}
@media(max-width:700px){.cards{grid-template-columns:repeat(3,1fr)}main{margin:16px auto}h1{font-size:23px}}
</style></head><body><main>
<header><span class="eyebrow">UTC · SELENIUM E2E</span><h1>Báo cáo kiểm thử đăng nhập</h1>
<p>__VERDICT__ · __TOTAL__ test đã chạy · __ELAPSED__ giây</p>
<p>__TIMESTAMP__<br>Trình duyệt: __BROWSER__ · Chế độ: __MODE__</p></header>
<section class="cards" aria-label="Tổng hợp kết quả">__CARDS__</section>
<p class="note">PASS nghĩa là test đã xác nhận đăng nhập bị từ chối đúng kỳ vọng.
FAIL là sai kỳ vọng; ERROR là lỗi thực thi. SKIP/XFAIL không được tính là PASS.</p>
<div class="controls"><input id="search" aria-label="Tìm test case" placeholder="Tìm tên hoặc mã test case…">
<select id="status" aria-label="Lọc kết quả"><option value="">Tất cả kết quả</option>__OPTIONS__</select></div>
<div class="table-wrap"><table><thead><tr><th>Test case</th><th>Kết quả</th><th>Thời gian</th></tr></thead>
<tbody>__ROWS__</tbody></table><p id="empty" hidden>Không có test phù hợp.</p></div>
<p class="note">File HTML độc lập, có thể mở trực tiếp hoặc gửi để xem kết quả lần chạy này.</p>
</main><script>
const search=document.querySelector('#search'),status=document.querySelector('#status');
function filter(){let visible=0;document.querySelectorAll('tbody tr').forEach(row=>{
const match=(!status.value||row.dataset.status===status.value)&&row.textContent.toLocaleLowerCase().includes(search.value.toLocaleLowerCase());
row.hidden=!match;if(match)visible++;});document.querySelector('#empty').hidden=visible>0;}
search.addEventListener('input',filter);status.addEventListener('change',filter);filter();
</script></body></html>'''
    replacements = {
        "__VERDICT__": escape(verdict), "__TOTAL__": str(result.testsRun),
        "__ELAPSED__": f"{elapsed:.2f}", "__TIMESTAMP__": escape(timestamp),
        "__BROWSER__": escape(browser), "__MODE__": "Headless" if headless else "Hiển thị cửa sổ",
        "__CARDS__": cards, "__OPTIONS__": options, "__ROWS__": "".join(rows),
    }
    # Thay placeholder một lượt để dữ liệu test không bị thay thế tiếp.
    import re
    document = re.sub(r"__[A-Z]+__", lambda match: replacements[match.group()], document)
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return output
