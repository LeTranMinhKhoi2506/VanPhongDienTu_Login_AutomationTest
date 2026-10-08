"""Page Object cho form đăng nhập tài khoản văn phòng điện tử."""

from urllib.parse import urlsplit

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from e2e.pages.base_page import BasePage


class LoginPage(BasePage):
    URL = "https://vanphongdientu.utc.edu.vn/Login?r=https%3A%2F%2Fvanphongdientu.utc.edu.vn%2F"
    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "userpwd")
    SUBMIT = (By.CSS_SELECTOR, "input.submit_login")
    ERROR = (By.CSS_SELECTOR, ".form .error")
    REMEMBER = (By.ID, "persistent")
    REMEMBER_LABEL = (By.CSS_SELECTOR, "label.check[for='persistent']")

    def open(self):
        self.driver.get(self.URL)
        self.visible(self.USERNAME)
        self.visible(self.PASSWORD)
        return self

    def submit(self, username, password, *, via_enter=False, remember=False):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        checkbox = self.driver.find_element(*self.REMEMBER)
        if checkbox.is_selected() != remember:
            # Checkbox bị ẩn bởi trang; click label hiển thị như người dùng.
            self.click(self.REMEMBER_LABEL)
        if checkbox.is_selected() != remember:
            raise AssertionError("Không thay đổi được tùy chọn giữ đăng nhập")
        old_submit = self.visible(self.SUBMIT)
        if via_enter:
            self.visible(self.PASSWORD).send_keys(Keys.ENTER)
        else:
            self.click(self.SUBMIT)
        # Form POST tải trang mới: tránh đọc lại DOM/thông báo cũ.
        self.wait.until(EC.staleness_of(old_submit))
        return self.visible(self.ERROR).text.strip()

    def is_login_form_visible(self):
        current = urlsplit(self.driver.current_url)
        expected = urlsplit(self.URL)
        return (
            current.scheme == expected.scheme
            and current.netloc == expected.netloc
            and current.path.rstrip("/").lower() == "/login"
            and self.visible(self.USERNAME).is_displayed()
            and self.visible(self.PASSWORD).is_displayed()
            and self.visible(self.SUBMIT).is_displayed()
        )
