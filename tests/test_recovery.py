
from pathlib import Path

from playwright.sync_api import sync_playwright

from recovery_engine import recover_and_confirm


BASE_DIR = Path(__file__).resolve().parent.parent
TEST_PAGE = BASE_DIR / "test_page.html"
DYNAMIC_TEST_PAGE = BASE_DIR / "dynamic_test_page.html"

def test_normal_workflow():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(TEST_PAGE.as_uri())

            result = recover_and_confirm(page)

            assert result["success"] is True
            assert result["verified_status"] == "Order status: Confirmed"
            assert result["successful_strategy"] == "original_selector"
        finally:
            browser.close()


def test_recovers_when_selector_changes():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(TEST_PAGE.as_uri())

            # Simulate a website change.
            page.locator("#confirm-order").evaluate(
                "(element) => element.id = 'confirm-order-updated'"
            )

            result = recover_and_confirm(page)

            assert result["success"] is True
            assert result["verified_status"] == "Order status: Confirmed"
            assert result["successful_strategy"] == "inspect_and_match_button"
            assert result["attempts"][0]["result"] == "timed_out"
        finally:
            browser.close()


def test_fails_safely_when_button_is_missing():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(TEST_PAGE.as_uri())

            # Remove the action entirely.
            page.locator("#confirm-order").evaluate(
                "(element) => element.remove()"
            )

            result = recover_and_confirm(page)

            assert result["success"] is False
            assert result["successful_strategy"] is None
            assert result["verified_status"] == "Order status: Pending"
            assert result["reason"] == "No matching button found"
        finally:
            browser.close()


def test_refuses_ambiguous_buttons():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(TEST_PAGE.as_uri())

            # Add a second button with the same name.
            page.locator("body").evaluate("""
                (body) => {
                    const button = document.createElement("button");
                    button.textContent = "Confirm Order";
                    body.appendChild(button);
                }
            """)

            # Force the engine to use recovery.
            page.locator("#confirm-order").evaluate(
                "(element) => element.id = 'changed-id'"
            )

            result = recover_and_confirm(page)

            assert result["success"] is False
            assert result["successful_strategy"] is None
            assert result["reason"] == (
                "Multiple matching buttons; refusing to guess"
            )
            assert result["verified_status"] == "Order status: Pending"
        finally:
            browser.close()

def test_does_not_retry_after_action_executes_but_verification_fails():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(TEST_PAGE.as_uri())

            # Make the button clickable without changing the status.
            page.locator("#confirm-order").evaluate("""
                (element) => {
                    element.onclick = () => {
                        window.clickCount = (window.clickCount || 0) + 1;
                    };
                }
            """)

            result = recover_and_confirm(page)

            click_count = page.evaluate("window.clickCount || 0")

            assert click_count == 1
            assert result["success"] is False
            assert result["reason"] == (
                "Click executed but outcome was not verified"
            )
            assert result["attempts"][0]["result"] == "executed"
            assert result["attempts"][0]["verification"] == "failed"
        finally:
            browser.close()


def test_trace_records_successful_recovery():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(TEST_PAGE.as_uri())

            page.locator("#confirm-order").evaluate(
                "(element) => element.id = 'changed-id'"
            )

            result = recover_and_confirm(page)

            events = result["trace"]["events"]

            assert result["success"] is True
            assert len(events) == 2
            assert events[0]["result"] == "timed_out"
            assert events[1]["result"] == "executed"
            assert events[1]["verification"] == "passed"
        finally:
            browser.close()


def test_trace_records_ambiguous_target():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(TEST_PAGE.as_uri())

            page.locator("body").evaluate("""
                (body) => {
                    const button = document.createElement("button");
                    button.textContent = "Confirm Order";
                    body.appendChild(button);
                }
            """)

            page.locator("#confirm-order").evaluate(
                "(element) => element.id = 'changed-id'"
            )

            result = recover_and_confirm(page)

            events = result["trace"]["events"]

            assert result["success"] is False
            assert events[-1]["result"] == "ambiguous"
            assert events[-1]["reason"] == (
                "Multiple matching buttons found"
            )
        finally:
            browser.close()


def test_recovers_from_dynamic_selector_change():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(DYNAMIC_TEST_PAGE.as_uri())

            # Wait until the page changes the button ID.
            page.wait_for_timeout(500)

            result = recover_and_confirm(page)

            assert result["success"] is True
            assert result["verified_status"] == "Order status: Confirmed"
            assert result["successful_strategy"] == (
                "inspect_and_match_button"
            )

            events = result["trace"]["events"]

            assert events[0]["result"] == "timed_out"
            assert events[1]["result"] == "executed"
            assert events[1]["verification"] == "passed"

        finally:
            browser.close()

def test_recovers_using_accessible_label():
    from pathlib import Path
    from playwright.sync_api import sync_playwright

    html_path = (
        Path(__file__).resolve().parent.parent
        / "accessible_label_test_page.html"
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(html_path.as_uri())

            result = recover_and_confirm(page)

            assert result["success"] is True
            assert result["verified_status"] == "Order status: Confirmed"
            assert result["successful_strategy"] == "inspect_and_match_button"

        finally:
            browser.close()

def test_recovers_from_async_element_loading():
    from pathlib import Path
    from playwright.sync_api import sync_playwright

    html_path = (
        Path(__file__).resolve().parent.parent
        / "async_test_page.html"
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(html_path.as_uri())

            result = recover_and_confirm(page)

            assert result["success"] is True
            assert result["verified_status"] == "Order status: Confirmed"
            assert result["successful_strategy"] == "inspect_and_match_button"

        finally:
            browser.close()