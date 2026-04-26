package stepDefinitions;

import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.junit.Assert;

public class TransferSteps {

    // Share the driver from LoginSteps
    WebDriver driver = LoginSteps.driver;

    @Given("the user is logged into the dashboard")
    public void theUserIsLoggedIntoTheDashboard() {
        if (driver == null) {
            // Re-initialize if null
            LoginSteps loginSteps = new LoginSteps();
            loginSteps.setup();
            driver = LoginSteps.driver;
        }
        
        // Register a test user
        driver.get("https://banking-automation-project.onrender.com/register");
        driver.findElement(By.id("username")).sendKeys("testsender");
        driver.findElement(By.id("password")).sendKeys("pass");
        driver.findElement(By.id("register-btn")).click();
        
        driver.get("https://banking-automation-project.onrender.com/register");
        driver.findElement(By.id("username")).sendKeys("receiverUser");
        driver.findElement(By.id("password")).sendKeys("pass");
        driver.findElement(By.id("register-btn")).click();

        // Login as the sender
        driver.get("https://banking-automation-project.onrender.com/login");
        driver.findElement(By.id("username")).sendKeys("testsender");
        driver.findElement(By.id("password")).sendKeys("pass");
        driver.findElement(By.id("login-btn")).click();
        
        // Wait until dashboard has loaded before proceeding
        org.openqa.selenium.support.ui.WebDriverWait loginWait = 
            new org.openqa.selenium.support.ui.WebDriverWait(driver, java.time.Duration.ofSeconds(20));
        loginWait.until(org.openqa.selenium.support.ui.ExpectedConditions.urlContains("/dashboard"));
    }

    @When("the user transfers {string} dollars to {string}")
    public void theUserTransfersDollarsTo(String amount, String receiver) {
        // Navigate to the dedicated transfer page
        driver.get("https://banking-automation-project.onrender.com/transfer");
        
        // Wait for the transfer form to be visible
        org.openqa.selenium.support.ui.WebDriverWait wait = new org.openqa.selenium.support.ui.WebDriverWait(driver, java.time.Duration.ofSeconds(20));
        wait.until(org.openqa.selenium.support.ui.ExpectedConditions.presenceOfElementLocated(By.id("receiver")));
        
        driver.findElement(By.id("receiver")).sendKeys(receiver);
        driver.findElement(By.id("amount")).sendKeys(amount);
        // Use JavaScript to submit the form directly (bypasses SweetAlert popup)
        driver.findElement(By.id("transfer-btn")).click();
        ((org.openqa.selenium.JavascriptExecutor) driver).executeScript(
            "document.getElementById('transferForm').submit();"
        );
    }

    @Then("a success message {string} should be displayed")
    public void aSuccessMessageShouldBeDisplayed(String successMessage) {
        // Wait for SweetAlert2 popup to appear
        org.openqa.selenium.support.ui.WebDriverWait wait = new org.openqa.selenium.support.ui.WebDriverWait(driver, java.time.Duration.ofSeconds(15));
        wait.until(org.openqa.selenium.support.ui.ExpectedConditions.visibilityOfElementLocated(
            By.cssSelector(".swal2-popup")
        ));
        String actualMessage = driver.findElement(By.cssSelector(".swal2-html-container")).getText();
        Assert.assertTrue("Expected: " + successMessage + ", Got: " + actualMessage,
            actualMessage.contains(successMessage));
    }

    @Then("an error message {string} should be displayed on dashboard")
    public void anErrorMessageShouldBeDisplayedOnDashboard(String errorMessage) {
        // Wait for SweetAlert2 error popup or redirect with error
        org.openqa.selenium.support.ui.WebDriverWait wait = new org.openqa.selenium.support.ui.WebDriverWait(driver, java.time.Duration.ofSeconds(15));
        try {
            // Try SweetAlert2 popup first
            wait.until(org.openqa.selenium.support.ui.ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector(".swal2-popup")
            ));
            String actualMessage = driver.findElement(By.cssSelector(".swal2-html-container")).getText();
            Assert.assertTrue("Expected: " + errorMessage + ", Got: " + actualMessage,
                actualMessage.contains(errorMessage));
        } catch (Exception e) {
            // Fallback: check URL query error param or alert element
            String currentUrl = driver.getCurrentUrl();
            Assert.assertTrue("Expected error in URL or page, but got URL: " + currentUrl,
                currentUrl.contains("error"));
        }
    }
}
