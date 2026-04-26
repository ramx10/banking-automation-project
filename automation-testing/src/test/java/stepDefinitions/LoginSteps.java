package stepDefinitions;

import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.junit.Assert;
import java.time.Duration;

public class LoginSteps {

    public static WebDriver driver;

    // Base URL for the deployed application
    private static final String BASE_URL = "https://banking-automation-project.onrender.com";

    @Before
    public void setup() {
        if (driver == null) {
            WebDriverManager.chromedriver().setup();
            ChromeOptions options = new ChromeOptions();
            options.addArguments("--headless");         // Run without opening a visible browser
            options.addArguments("--window-size=1920,1080");
            options.addArguments("--disable-gpu");
            options.addArguments("--no-sandbox");
            driver = new ChromeDriver(options);
        }
    }

    // ---------------------------------------------------------------
    // GIVEN steps
    // ---------------------------------------------------------------

    @Given("the user is on the login page")
    public void theUserIsOnTheLoginPage() {
        driver.get(BASE_URL + "/login");

        // Wait for the login button to be visible before interacting
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("login-btn")));
    }

    // ---------------------------------------------------------------
    // WHEN steps
    // ---------------------------------------------------------------

    @When("the user enters username {string} and password {string}")
    public void theUserEntersUsernameAndPassword(String username, String password) {
        // Clear fields first to avoid stale data, then type
        driver.findElement(By.id("username")).clear();
        driver.findElement(By.id("username")).sendKeys(username);

        driver.findElement(By.id("password")).clear();
        driver.findElement(By.id("password")).sendKeys(password);
    }

    @And("clicks on the login button")
    public void clicksOnTheLoginButton() {
        driver.findElement(By.id("login-btn")).click();
    }

    @And("the user clicks the logout button")
    public void theUserClicksTheLogoutButton() {
        // Wait for the page to load after login, then find logout
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.urlContains("/dashboard"));

        // Logout is a form submit button — click it
        driver.findElement(By.cssSelector("button[type='submit']")).click();
    }

    // ---------------------------------------------------------------
    // THEN steps
    // ---------------------------------------------------------------

    @Then("the user should be redirected to the dashboard")
    public void theUserShouldBeRedirectedToTheDashboard() {
        // Wait until the URL changes to dashboard
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.urlContains("/dashboard"));

        String currentUrl = driver.getCurrentUrl();
        Assert.assertTrue("Expected /dashboard in URL but got: " + currentUrl,
            currentUrl.contains("/dashboard"));
    }

    @Then("the user should remain on the login page")
    public void theUserShouldRemainOnTheLoginPage() {
        // For empty input, client-side HTML5 validation prevents submission
        // Page should still be the login page
        String currentUrl = driver.getCurrentUrl();
        Assert.assertTrue("Expected to remain on login page, but got: " + currentUrl,
            currentUrl.contains("/login"));
    }

    @Then("the user should be redirected to the login page")
    public void theUserShouldBeRedirectedToTheLoginPage() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.urlContains("/login"));

        String currentUrl = driver.getCurrentUrl();
        Assert.assertTrue("Expected /login in URL but got: " + currentUrl,
            currentUrl.contains("/login"));
    }

    @Then("an error message {string} should be displayed")
    public void anErrorMessageShouldBeDisplayed(String errorMessage) {
        // Wait for the error alert box to appear on the page
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("alert")));

        String actualError = driver.findElement(By.className("alert")).getText();
        Assert.assertTrue("Expected error: '" + errorMessage + "', Got: '" + actualError + "'",
            actualError.contains(errorMessage));
    }

    // ---------------------------------------------------------------
    // Cleanup: quit browser after each scenario
    // ---------------------------------------------------------------

    @After
    public void tearDown() {
        if (driver != null) {
            driver.quit();
            driver = null;
        }
    }
}
