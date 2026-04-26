Feature: Bank Login Functionality

  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When the user enters username "testuser" and password "password123"
    And clicks on the login button
    Then the user should be redirected to the dashboard

  Scenario: Unsuccessful login with invalid credentials
    Given the user is on the login page
    When the user enters username "invaliduser" and password "wrongpass"
    And clicks on the login button
    Then an error message "Invalid username or password" should be displayed
