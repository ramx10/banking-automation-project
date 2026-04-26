Feature: Bank Login Functionality
  As a bank customer
  I want to be able to log in to the application
  So that I can access my account securely

  # ✅ TC-01: Positive - Valid credentials should redirect to dashboard
  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When the user enters username "admin" and password "password123"
    And clicks on the login button
    Then the user should be redirected to the dashboard

  # ❌ TC-02: Validation - Empty fields should show an error (client-side)
  Scenario: Login with empty username and password
    Given the user is on the login page
    When the user enters username "" and password ""
    And clicks on the login button
    Then the user should remain on the login page

  # ❌ TC-03: Negative - Wrong password should stay on login page
  Scenario: Login with invalid credentials
    Given the user is on the login page
    When the user enters username "testuser" and password "wrongpass"
    And clicks on the login button
    Then an error message "Invalid username or password" should be displayed

  # 🚪 TC-04: Logout should redirect to login page
  Scenario: User can log out of the application
    Given the user is on the login page
    When the user enters username "admin" and password "password123"
    And clicks on the login button
    Then the user should be redirected to the dashboard
    And the user clicks the logout button
    Then the user should be redirected to the login page
