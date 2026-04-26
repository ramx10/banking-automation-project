import requests

def test_sql_injection(url):
    print(f"\n--- Testing SQL Injection on {url} ---")
    
    # Classic auth bypass payload
    payload = "' OR 1=1 --"
    
    data = {
        "username": payload,
        "password": "random_password"
    }
    
    print(f"Sending Payload: {payload}")
    
    try:
        response = requests.post(url, data=data, allow_redirects=False)
        
        # If the server redirects us (302) to the dashboard, it means login succeeded
        if response.status_code == 302 and '/dashboard' in response.headers.get('Location', ''):
            print("[!] VULNERABILITY DETECTED: SQL Injection successful. Authentication bypassed!")
        else:
            print("[+] SECURE: Application blocked SQL Injection payload.")
    except Exception as e:
        print(f"Error testing SQLi: {e}")

def test_xss(url):
    print(f"\n--- Testing Cross-Site Scripting (XSS) on {url} ---")
    
    payload = "<script>alert('XSS')</script>"
    
    # Simulating XSS in a transfer or registration field
    data = {
        "username": payload,
        "password": "testpassword"
    }
    
    print(f"Sending Payload: {payload}")
    try:
        response = requests.post(url, data=data)
        
        if payload in response.text:
            print("[!] VULNERABILITY DETECTED: XSS Payload reflected in response body!")
        else:
            print("[+] SECURE: XSS Payload was sanitized or not reflected.")
    except Exception as e:
        print(f"Error testing XSS: {e}")


if __name__ == "__main__":
    base_url = "http://localhost:3000"
    
    print("Starting Automated Security Tests...")
    # Test SQLi on login
    test_sql_injection(f"{base_url}/login")
    
    # Test XSS on registration (which reflects the username error if already exists, etc)
    # Actually, let's test it on register endpoint.
    test_xss(f"{base_url}/register")
    
    print("\nSecurity Testing Completed.")
