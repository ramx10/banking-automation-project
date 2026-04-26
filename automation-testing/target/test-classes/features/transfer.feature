Feature: Money Transfer Functionality

  Background:
    Given the user is logged into the dashboard

  Scenario: Successful money transfer
    When the user transfers "50" dollars to "receiverUser"
    Then a success message "Transfer successful" should be displayed

  Scenario: Unsuccessful transfer due to insufficient balance
    When the user transfers "50000" dollars to "receiverUser"
    Then an error message "Insufficient balance" should be displayed on dashboard
