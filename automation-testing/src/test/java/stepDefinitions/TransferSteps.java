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
        driver.get("http://localhost:3000/register");
        driver.findElement(By.id("username")).sendKeys("testsender");
        driver.findElement(By.id("password")).sendKeys("pass");
        driver.findElement(By.id("register-btn")).click();
        
        driver.get("http://localhost:3000/register");
        driver.findElement(By.id("username")).sendKeys("receiverUser");
        driver.findElement(By.id("password")).sendKeys("pass");
        driver.findElement(By.id("register-btn")).click();

        // Login as the sender
        driver.get("http://localhost:3000/login");
        driver.findElement(By.id("username")).sendKeys("testsender");
        driver.findElement(By.id("password")).sendKeys("pass");
        driver.findElement(By.id("login-btn")).click();
    }

    @When("the user transfers {string} dollars to {string}")
    public void theUserTransfersDollarsTo(String amount, String receiver) {
        driver.findElement(By.id("receiver")).sendKeys(receiver);
        driver.findElement(By.id("amount")).sendKeys(amount);
        driver.findElement(By.id("transfer-btn")).click();
    }

    @Then("a success message {string} should be displayed")
    public void aSuccessMessageShouldBeDisplayed(String successMessage) {
        org.openqa.selenium.support.ui.WebDriverWait wait = new org.openqa.selenium.support.ui.WebDriverWait(driver, java.time.Duration.ofSeconds(10));
        wait.until(org.openqa.selenium.support.ui.ExpectedConditions.visibilityOfElementLocated(By.className("success")));
        String actualMessage = driver.findElement(By.className("success")).getText();
        Assert.assertEquals(successMessage, actualMessage);
    }

    @Then("an error message {string} should be displayed on dashboard")
    public void anErrorMessageShouldBeDisplayedOnDashboard(String errorMessage) {
        org.openqa.selenium.support.ui.WebDriverWait wait = new org.openqa.selenium.support.ui.WebDriverWait(driver, java.time.Duration.ofSeconds(10));
        wait.until(org.openqa.selenium.support.ui.ExpectedConditions.visibilityOfElementLocated(By.className("error")));
        String actualMessage = driver.findElement(By.className("error")).getText();
        Assert.assertEquals(errorMessage, actualMessage);
    }
}
