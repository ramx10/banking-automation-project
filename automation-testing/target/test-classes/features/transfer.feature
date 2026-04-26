Feature: Money Transfer Functionality
  As a logged-in bank customer
  I want to be able to transfer money to other users
  So that I can make payments easily

  Background:
    Given the user is logged into the dashboard

  # ✅ TC-05: Positive - Valid transfer should show success
  Scenario: Successful money transfer to valid recipient
    When the user transfers "10" dollars to "receiverUser"
    Then a success message "Transfer successful" should be displayed

  # ❌ TC-06: Negative - Insufficient balance should show error
  Scenario: Transfer fails due to insufficient balance
    When the user transfers "50000" dollars to "receiverUser"
    Then an error message "Insufficient balance" should be displayed on dashboard
