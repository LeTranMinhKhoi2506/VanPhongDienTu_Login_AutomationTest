"""Khởi tạo trình duyệt và đóng WebDriver sau từng test case."""

import os
import unittest

from selenium import webdriver


class BaseTest(unittest.TestCase):
    def setUp(self):
        browser = os.getenv("BROWSER", "chrome").lower()
        if browser not in {"chrome", "edge"}:
            raise ValueError("BROWSER phải là chrome hoặc edge")
        options = (
            webdriver.ChromeOptions() if browser == "chrome"
            else webdriver.EdgeOptions()
        )
        if os.getenv("HEADLESS", "1") == "1":
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,900")
        factory = webdriver.Chrome if browser == "chrome" else webdriver.Edge
        self.driver = factory(options=options)
        self.addCleanup(self.driver.quit)
        self.driver.set_page_load_timeout(30)
        self.timeout = 20
