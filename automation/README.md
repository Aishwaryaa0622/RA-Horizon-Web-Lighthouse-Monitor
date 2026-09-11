﻿# Horizon Plus Playwright Login Automation Guide

This folder contains an automated end-to-end browser test built with [Playwright](https://playwright.dev/python/) for the **Horizon Plus** web application.

---

## Target Web Application
- **Base URL:** https://horizon-plus.dfp8hwwhcxnpq.amplifyapp.com/languages
- **Sign In URL:** https://horizon-plus.dfp8hwwhcxnpq.amplifyapp.com/signin

---

## How It Works

```
Start Test
  ↓
Load Credentials from .env (HORIZON_USERNAME, HORIZON_PASSWORD)
  ↓
Launch Headless Chromium Browser
  ↓
Navigate to Target Application
  ↓
Detect and Verify Sign-In Page
  ↓
Locate Email and Password Inputs (Stable Selectors)
  ↓
Fill Credentials and Click "Login Now"
  ↓
Monitor Network Response & Navigation
  ↓
Capture Result Screenshot to screenshots/
  ↓
Print PASS or FAIL with Diagnostics
```

---

## Configuration

Credentials must **never** be hard-coded into test files or committed to Git. Instead, they are loaded securely from a `.env` file in the project root.

1. In the project root, make a copy of `.env.example`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your authorized credentials:
   ```ini
   HORIZON_USERNAME=your_authorized_email@example.com
   HORIZON_PASSWORD=your_authorized_password
   PLAYWRIGHT_HEADLESS=true
   ```

> [!TIP]
> Setting `PLAYWRIGHT_HEADLESS=false` in `.env` opens a visible browser window so you can watch the automation interact with the website in real time.

---

## Running the Automation Test

Run the test from the project root directory:

```bash
# On Windows:
.\venv\Scripts\python.exe automation/login_test.py

# Or on macOS/Linux:
python automation/login_test.py
```

---

## Expected Output

### On Successful Login:
```text
=================================
HORIZON LOGIN AUTOMATION
Opening website...
Login page detected.
Entering credentials...
Clicking Login...
Checking successful login...
LOGIN TEST: PASS
Screenshot saved to:
screenshots/login-success.png
```

### On Unsuccessful Login:
```text
=================================
HORIZON LOGIN AUTOMATION
Opening website...
Login page detected.
Entering credentials...
Clicking Login...
Checking successful login...
LOGIN TEST: FAIL
Reason: The username or password is not correct
Screenshot saved to:
screenshots/login-failed.png
```

---

## Stable Selectors Used

| Element | Selector Used | Fallback Selector |
| :--- | :--- | :--- |
| **Email Field** | `input[name='email']` | `input#email` |
| **Password Field** | `input[name='pass']` | `input[type='password']` |
| **Login Button** | `button:has-text('Login Now')` | `button[type='submit']` |

If the target website's UI changes in the future, update these selectors in `automation/login_test.py`.

---

## Safety & Ethics Guidelines

1. **Authorized Use Only:** Only run this test with accounts and credentials you are explicitly authorized to test.
2. **No Brute-Forcing:** Never use this script to guess passwords or perform dictionary attacks.
3. **No Security Circumvention:** This test automates the standard login flow. If a site introduces CAPTCHA, Multi-Factor Authentication (MFA), or bot verification, do not attempt to bypass it.
