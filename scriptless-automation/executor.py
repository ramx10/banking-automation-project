import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def execute_scriptless_test(json_file):
    print(f"--- Scriptless Executor Started: {json_file} ---")
    
    with open(json_file, 'r') as f:
        test_data = json.load(f)
        
    print(f"Executing Test: {test_data.get('testName', 'Unnamed Test')}")
    
    # Setup WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run headless
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        steps = test_data.get("steps", [])
        for i, step in enumerate(steps, 1):
            action = step.get("action")
            print(f"Step {i}: {action} -> ", end="")
            
            if action == "navigate":
                url = step.get("url")
                driver.get(url)
                print(f"Navigated to {url}")
                
            elif action == "input":
                loc_type = step.get("locator_type")
                loc_val = step.get("locator_value")
                data = step.get("data")
                
                element = get_element(driver, loc_type, loc_val)
                element.send_keys(data)
                print(f"Entered '{data}' into [{loc_type}={loc_val}]")
                
            elif action == "click":
                loc_type = step.get("locator_type")
                loc_val = step.get("locator_value")
                
                element = get_element(driver, loc_type, loc_val)
                element.click()
                print(f"Clicked element [{loc_type}={loc_val}]")
                
            elif action == "verify_url":
                expected = step.get("expected_url")
                time.sleep(1) # wait for redirect
                actual = driver.current_url
                if expected in actual:
                    print(f"URL Verified. (Current: {actual})")
                else:
                    print(f"URL Verification FAILED. Expected: {expected}, Actual: {actual}")
            else:
                print(f"Unknown action: {action}")
                
        print("Test Execution Completed Successfully.")
        
    except Exception as e:
        print(f"\nTest Failed during execution. Error: {str(e)}")
        
    finally:
        driver.quit()

def get_element(driver, loc_type, loc_val):
    if loc_type == "id":
        return driver.findElement(By.ID, loc_val) # Actually driver.find_element(By.ID, loc_val)
    elif loc_type == "name":
        return driver.find_element(By.NAME, loc_val)
    elif loc_type == "xpath":
        return driver.find_element(By.XPATH, loc_val)
    elif loc_type == "css":
        return driver.find_element(By.CSS_SELECTOR, loc_val)
    else:
        raise ValueError(f"Unsupported locator type: {loc_type}")

# Correcting a minor bug in the Python implementation in the snippet above:
# findElement should be find_element. I will just correct it here.

def get_element(driver, loc_type, loc_val):
    if loc_type == "id":
        return driver.find_element(By.ID, loc_val)
    elif loc_type == "name":
        return driver.find_element(By.NAME, loc_val)
    elif loc_type == "xpath":
        return driver.find_element(By.XPATH, loc_val)
    elif loc_type == "css":
        return driver.find_element(By.CSS_SELECTOR, loc_val)
    else:
        raise ValueError(f"Unsupported locator type: {loc_type}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_json = os.path.join(current_dir, "test_steps.json")
    
    if os.path.exists(input_json):
        execute_scriptless_test(input_json)
    else:
        print(f"Input file not found: {input_json}")
