# UTC Login E2E — Python Selenium

Project dùng Page Object Model và `unittest` (có sẵn trong Python).
Chỉ kiểm thử đăng nhập thất bại trên form tài khoản văn phòng điện tử.

```text
utc-login-e2e/
├── requirements.txt
├── README.md
└── e2e/
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
