"""Chỉ kiểm thử đăng nhập thất bại; không sử dụng tài khoản thật."""

import unittest
from uuid import uuid4

from e2e.base.base_test import BaseTest
from e2e.pages.login_page import LoginPage


class LoginE2ETest(BaseTest):
    INVALID_PASSWORD = "InvalidPassword!123"
    INVALID_CREDENTIALS_ERROR = "Tài khoản hoặc mật khẩu không đúng."

    def setUp(self):
        super().setUp()
        self.login_page = LoginPage(self.driver, self.timeout).open()
        self.unknown_username = "selenium_nonexistent_" + uuid4().hex

    def assert_login_rejected(self, username, password, expected_error, **options):
        actual_error = self.login_page.submit(username, password, **options)
        self.assertEqual(actual_error, expected_error)
        self.assertTrue(
            self.login_page.is_login_form_visible(),
            "Đăng nhập thất bại phải giữ người dùng ở trang đăng nhập",
        )

    def test_tc01_both_fields_empty(self):
        """TC01: Bỏ trống cả tên đăng nhập và mật khẩu."""
        self.assert_login_rejected("", "", "Bạn chưa nhập tên đăng nhập")


    def test_tc02_username_empty(self):
        """TC02: Bỏ trống tên đăng nhập, có mật khẩu."""
        self.assert_login_rejected("", self.INVALID_PASSWORD, "Bạn chưa nhập tên đăng nhập")


    def test_tc03_password_empty(self):
        """TC03: Có tên tài khoản giả, bỏ trống mật khẩu."""
        self.assert_login_rejected(self.unknown_username, "", "Bạn chưa nhập mật khẩu")


if __name__ == "__main__":
    unittest.main(verbosity=2)
