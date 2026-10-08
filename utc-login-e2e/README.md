# UTC Login E2E — Python Selenium

Project dùng Page Object Model và `unittest` (có sẵn trong Python).
Chỉ kiểm thử đăng nhập thất bại trên form tài khoản văn phòng điện tử.

```text
utc-login-e2e/
├── requirements.txt
├── README.md
├── run_tests.py             # Chạy test và tạo báo cáo HTML
└── e2e/
    ├── reporting.py          # Thu thập kết quả và dựng HTML
    ├── base/
    │   └── base_test.py       # WebDriver, timeout, đóng browser mỗi test
    ├── pages/
    │   ├── base_page.py       # Chờ, click, nhập liệu
    │   └── login_page.py      # Form đăng nhập và thông báo lỗi
    └── tests/
        └── test_login_e2e.py  # Mỗi phương thức là một test case
```

## Chạy test (PowerShell)

Cần Python 3.10+ và Chrome hoặc Edge đã cài đặt.
Từ `D:\Selenium`:

```powershell
cd utc-login-e2e
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s e2e/tests -v
```

Mặc định chạy Chrome headless. Để xem trình duyệt hoặc dùng Edge:

```powershell
$env:HEADLESS = "0"
$env:BROWSER = "edge"
.\.venv\Scripts\python.exe -m unittest discover -s e2e/tests -v
```

Chạy riêng một test:

```powershell
.\.venv\Scripts\python.exe -m unittest e2e.tests.test_login_e2e.LoginE2ETest.test_tc01_both_fields_empty -v
```

Nếu Selenium đã cài sẵn, thay `.\.venv\Scripts\python.exe` bằng `python`.
Lần chạy đầu cần Internet để Selenium Manager tìm/tải WebDriver phù hợp.
Tham khảo [Selenium Manager](https://www.selenium.dev/documentation/selenium_manager/)
và [explicit waits](https://www.selenium.dev/documentation/webdriver/waits/).

## Báo cáo HTML sau khi chạy test

Từ thư mục `utc-login-e2e`, chạy:

```powershell
python run_tests.py --open
```

Lệnh chạy toàn bộ 20 test, tạo `artifacts/report.html` và mở báo cáo bằng
trình duyệt mặc định. Nếu dùng `.venv`, thay `python` bằng
`.\.venv\Scripts\python.exe`. Để nhìn thấy Chrome thao tác trong lúc chạy:

```powershell
$env:HEADLESS = "0"
$env:BROWSER = "chrome"
python run_tests.py --open
```

Chỉ chạy một test và xuất báo cáo:

```powershell
python run_tests.py --test e2e.tests.test_login_e2e.LoginE2ETest.test_tc01_both_fields_empty --open
```

Mỗi lần chạy sẽ ghi đè `artifacts/report.html`. Muốn lưu riêng từng lần:

```powershell
python run_tests.py --report artifacts/report-01.html --open
```

Báo cáo có tổng hợp PASS/FAIL/ERROR/SKIP, thời gian từng test, tìm kiếm,
lọc trạng thái và chi tiết lỗi có thể mở rộng. Giờ hiển thị theo UTC+7.
PASS nghĩa là test xác nhận đăng nhập thất bại đúng kỳ vọng.
File HTML chứa sẵn nội dung, không cần server hoặc Internet để xem.
Thư mục `artifacts/` được Git bỏ qua.

Runner vẫn tạo báo cáo khi test FAIL hoặc ERROR và trả mã thoát `1`;
chạy thành công trả mã `0`. Lệnh `python -m unittest ...` cũ vẫn dùng được,
nhưng không tự tạo báo cáo. Kiểm tra riêng chức năng báo cáo (không Selenium):

```powershell
python -m unittest discover -s verification -v
```

## Test cases

Mỗi test mở trình duyệt mới, nhập dữ liệu, gửi form, chờ phản hồi,
kiểm tra chính xác thông báo lỗi và form vẫn hiển thị tại `/Login`.
Tên tài khoản giả được tạo bằng UUID, không dùng thông tin đăng nhập thật.
Không kiểm thử OAuth Google hoặc gửi email khôi phục mật khẩu.

| ID | Tình huống | Kết quả mong đợi |
| --- | --- | --- |
| TC01 | Cả hai trường trống | Bạn chưa nhập tên đăng nhập |
| TC02 | Tên đăng nhập trống, có mật khẩu | Bạn chưa nhập tên đăng nhập |
| TC03 | Có tên tài khoản giả, mật khẩu trống | Bạn chưa nhập mật khẩu |
| TC04 | Tài khoản giả và mật khẩu sai | Tài khoản hoặc mật khẩu không đúng. |
| TC05 | Tên đăng nhập là ba khoảng trắng | Tài khoản hoặc mật khẩu không đúng. |
| TC06 | Mật khẩu là ba khoảng trắng, tài khoản giả | Tài khoản hoặc mật khẩu không đúng. |
| TC07 | Gửi tài khoản giả bằng phím Enter | Tài khoản hoặc mật khẩu không đúng. |
| TC08 | Bật giữ đăng nhập với tài khoản giả | Tài khoản hoặc mật khẩu không đúng. |
| TC09 | Tên đăng nhập giả có Unicode | Tài khoản hoặc mật khẩu không đúng. |
| TC10 | Email UTC giả trong form thường | Tài khoản hoặc mật khẩu không đúng. |
| TC11 | Tên tài khoản giả có khoảng trắng đầu/cuối | Tài khoản hoặc mật khẩu không đúng. |
| TC12 | Tên tài khoản giả có khoảng trắng ở giữa | Tài khoản hoặc mật khẩu không đúng. |
| TC13 | Tên tài khoản giả có ký tự đặc biệt | Tài khoản hoặc mật khẩu không đúng. |
| TC14 | Mật khẩu Unicode với tài khoản giả | Tài khoản hoặc mật khẩu không đúng. |
| TC15 | Tên đăng nhập giả dài 256 ký tự | Tài khoản hoặc mật khẩu không đúng. |
| TC16 | Mật khẩu dài 256 ký tự với tài khoản giả | Tài khoản hoặc mật khẩu không đúng. |
| TC17 | Sau lỗi sai tài khoản, gửi lại tên trống | Thông báo mới: Bạn chưa nhập tên đăng nhập |
| TC18 | Sau lỗi sai tài khoản, gửi lại mật khẩu trống | Thông báo mới: Bạn chưa nhập mật khẩu |
| TC19 | Sau lỗi bỏ trống, gửi lại tài khoản giả | Thông báo mới: Tài khoản hoặc mật khẩu không đúng. |
| TC20 | Kiểm tra ô mật khẩu sau khi bị từ chối | Ô mật khẩu rỗng, vẫn ở trang đăng nhập |

Các kỳ vọng dựa trên phản hồi thực tế của trang ngày 08/10/2026.
Trang hiện không coi chuỗi chỉ có khoảng trắng là trường trống;
các tình huống đó được kiểm tra theo phản hồi từ chối thông tin đăng nhập.
Các test Unicode, email, khoảng trắng và dữ liệu dài dùng tài khoản giả để
kiểm tra hệ thống từ chối và vẫn hiển thị form. Chúng không chứng minh
quy tắc chuẩn hóa tên đăng nhập hoặc giới hạn độ dài của tài khoản hợp lệ.
TC17–TC19 kiểm tra thông báo mới sau khi gửi lại form; TC20 kiểm tra ô
mật khẩu được xóa sau khi bị từ chối.
Lỗi kết nối, timeout hoặc WebDriver là lỗi thực thi test, không tính là PASS.

## Commit

Git được khởi tạo tại `D:\Selenium`. Mỗi commit `test(login): TCxx ...`
thêm đúng một test case và dòng mô tả tương ứng. Commit TC01 gồm cả
khung project dùng chung. Xem lịch sử bằng `git log --oneline`.
