import pytest
from playwright.sync_api import Page
from healer import smart_click, smart_fill, generate_html_report


def test_user_can_login(page: Page):
    page.goto("https://practicetestautomation.com/practice-test-login/")

    # Intentionally wrong selectors — AI will heal them
    smart_fill(page, "#wrong-username-field", "student")
    smart_fill(page, "#wrong-password-field", "Password123")
    smart_click(page, "#wrong-submit-btn")

    assert "logged-in-successfully" in page.url
    print("✅ Login successful!")

    # Auto-generate HTML report after test
    generate_html_report()
    print("📊 HTML report generated: healing_report.html")