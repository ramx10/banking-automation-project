# AI-Powered Automated Testing Framework for a Banking Web Application

This project is a comprehensive college-level implementation of an advanced testing framework designed for a modern web application, specifically built for the "Advanced Automation & Industry Practices" unit.

It demonstrates a full Software Testing Life Cycle (STLC) augmented with AI concepts, Behavior Driven Development (BDD), Scriptless Automation, Security Testing, and DevSecOps.

---

## 📁 Project Structure

1. **`/webapp`**: The target banking application built using Node.js, Express, and SQLite. Features registration, login, dashboard, and money transfers.
2. **`/automation-testing`**: A Java Maven project utilizing Selenium WebDriver and Cucumber for BDD. Contains feature files for functional testing.
3. **`/ai-test-generation`**: A Python engine that parses a JSON definition of a UI module (e.g., Login Page) and dynamically generates valid, invalid, and boundary test cases.
4. **`/scriptless-automation`**: A framework in Python using Selenium that reads test steps from a JSON file and executes them on the browser, demonstrating no-code/low-code automation.
5. **`/security-testing`**: Python scripts demonstrating automated DAST (Dynamic Application Security Testing). It tests the application endpoints for SQL Injection and Cross-Site Scripting (XSS) vulnerabilities.
6. **`.github/workflows`**: Contains a CI/CD pipeline configuration (`ci.yml`) to automatically execute all testing frameworks upon code push, demonstrating DevSecOps practices.

---

## 🚀 How to Run the Project (For Viva Demonstration)

### Prerequisites
- Node.js (v18+)
- Java (JDK 11+) and Maven
- Python 3.10+
- Chrome Browser

### 1. Start the Target Web Application
Open a terminal and navigate to the `/webapp` directory:
```bash
cd webapp
npm install
npm start
```
*The app will run on `http://localhost:3000`.*

### 2. Run BDD Automation Tests (Selenium + Cucumber)
In a new terminal, navigate to `/automation-testing`:
```bash
cd automation-testing
mvn clean test
```
*Cucumber HTML reports will be generated in `target/cucumber-reports/`.*

### 3. Generate AI Test Cases
Navigate to `/ai-test-generation`:
```bash
cd ai-test-generation
python generate_tests.py
```
*Observe the generated JSON test permutations based on the login module schema.*

### 4. Execute Scriptless Automation
Navigate to `/scriptless-automation`:
```bash
cd scriptless-automation
pip install selenium webdriver-manager
python executor.py
```
*This will execute the browser automation steps defined entirely in `test_steps.json`.*

### 5. Run Security Tests
Navigate to `/security-testing`:
```bash
cd security-testing
pip install requests
python security_scanner.py
```
*Observe the results of SQLi and XSS payloads against the locally running web app.*

---

## ☁️ Cloud Deployment Guide (Basic Integration)

For academic purposes, you can deploy the web application using platforms like **Render** or **Heroku**.

1. Create an account on [Render.com](https://render.com/).
2. Connect your GitHub repository containing this project.
3. Create a new "Web Service".
4. Set the Root Directory to `webapp`.
5. Build Command: `npm install`
6. Start Command: `npm start`
7. Render will provide a live URL (e.g., `https://banking-app-xyz.onrender.com`). You can point your automated testing tools to this URL instead of `localhost:3000` for a cloud-based test run!

---

## 🎯 Final Summary for Project Report

This project successfully integrates multiple facets of modern software quality assurance:
- **Functional validation** through BDD and Selenium.
- **Efficiency improvements** via AI-assisted test permutations and Scriptless json-based test execution.
- **Security consciousness** via automated injection and reflection testing.
- **Continuous Integration** via GitHub actions.

It perfectly encapsulates the "Advanced Automation & Industry Practices" curriculum requirements.
