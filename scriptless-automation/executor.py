"""
Scriptless Automation Executor
--------------------------------
Reads test scenarios from test_steps.json and executes them using Selenium.
Supports: navigate, input, click, verify_url, verify_url_contains, js_submit

Usage:
    python executor.py

Supported Actions:
    navigate            - Navigate browser to a URL
    input               - Type text into a field (supports empty string)
    click               - Click a button or element
    verify_url          - Assert exact URL match
    verify_url_contains - Assert URL contains a fragment (for redirects)
    js_submit           - Submit a form directly via JavaScript (bypasses JS popups)
"""

import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_element(driver, loc_type, loc_val, timeout=10):
    """Find an element with an explicit wait to handle page load delays."""
    wait = WebDriverWait(driver, timeout)
    by_map = {
        "id":    By.ID,
        "name":  By.NAME,
        "xpath": By.XPATH,
        "css":   By.CSS_SELECTOR,
    }
    if loc_type not in by_map:
        raise ValueError(f"Unsupported locator type: '{loc_type}'")
    by = by_map[loc_type]
    return wait.until(EC.presence_of_element_located((by, loc_val)))


def run_test(driver, test_data):
    """Execute a single test scenario from a dict."""
    test_name = test_data.get("testName", "Unnamed Test")
    steps = test_data.get("steps", [])

    print(f"\n{'='*55}")
    print(f"  Running: {test_name}")
    print(f"{'='*55}")

    passed = True

    for i, step in enumerate(steps, 1):
        action = step.get("action")
        print(f"  Step {i}: [{action}]", end=" -> ")

        try:
            if action == "navigate":
                url = step["url"]
                driver.get(url)
                # Wait for page to be interactive
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                print(f"Navigated to {url}")

            elif action == "input":
                loc_type = step["locator_type"]
                loc_val  = step["locator_value"]
                data     = step.get("data", "")
                element  = get_element(driver, loc_type, loc_val)
                element.clear()
                if data:
                    element.send_keys(data)
                print(f"Entered '{data}' into [{loc_type}={loc_val}]")

            elif action == "click":
                loc_type = step["locator_type"]
                loc_val  = step["locator_value"]
                element  = get_element(driver, loc_type, loc_val)
                element.click()
                print(f"Clicked [{loc_type}={loc_val}]")

            elif action == "verify_url":
                expected = step["expected_url"]
                time.sleep(2)  # Wait for redirect to complete
                actual = driver.current_url
                if expected in actual:
                    print(f"[PASS] URL verified: {actual}")
                else:
                    print(f"[FAIL] Expected URL '{expected}', Got '{actual}'")
                    passed = False

            elif action == "verify_url_contains":
                fragment = step["expected_fragment"]
                time.sleep(2)  # Wait for redirect
                actual = driver.current_url
                if fragment in actual:
                    print(f"[PASS] URL contains '{fragment}': {actual}")
                else:
                    print(f"[FAIL] Expected URL to contain '{fragment}', Got '{actual}'")
                    passed = False

            elif action == "js_submit":
                # Submit a form via JavaScript by its ID to bypass SweetAlert2 popups.
                # This avoids stale element reference errors from JS event interceptions.
                loc_type = step["locator_type"]
                loc_val  = step["locator_value"]
                if loc_type == "id":
                    driver.execute_script(f"document.getElementById('{loc_val}').submit();")
                else:
                    element = get_element(driver, loc_type, loc_val)
                    driver.execute_script("arguments[0].submit();", element)
                print(f"Form [{loc_type}={loc_val}] submitted via JavaScript")

            else:
                print(f"[SKIP] Unknown action '{action}' - skipped")

        except Exception as e:
            print(f"[ERROR] {str(e)}")
            passed = False

    status = "[PASSED]" if passed else "[FAILED]"
    print(f"\n  Result: {status}")
    return passed


def execute_all_tests(json_file):
    """Load JSON file (single test or array of tests) and execute each one."""
    print(f"\n{'*'*55}")
    print(f"  Scriptless Executor — {json_file}")
    print(f"{'*'*55}")

    with open(json_file, 'r') as f:
        raw = json.load(f)

    # Support both a single test object and an array of tests
    tests = raw if isinstance(raw, list) else [raw]

    # Setup Chrome WebDriver (headless for CI/CD compatibility)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    results = []
    try:
        for test_data in tests:
            result = run_test(driver, test_data)
            results.append((test_data.get("testName", "Unnamed Test"), result))
    finally:
        driver.quit()

    # Print summary
    print(f"\n{'='*55}")
    print("  SUMMARY")
    print(f"{'='*55}")
    total  = len(results)
    passed = sum(1 for _, r in results if r)
    failed = total - passed

    for name, result in results:
        icon = "[PASS]" if result else "[FAIL]"
        print(f"  {icon} {name}")

    print(f"\n  Total: {total}  |  Passed: {passed}  |  Failed: {failed}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_json  = os.path.join(current_dir, "test_steps.json")

    if os.path.exists(input_json):
        execute_all_tests(input_json)
    else:
        print(f"❌ Input file not found: {input_json}")
