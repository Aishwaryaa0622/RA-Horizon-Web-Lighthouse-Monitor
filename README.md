﻿# Web Lighthouse Performance Monitor + Playwright Login Automation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0+](https://img.shields.io/badge/flask-3.0+-green.svg)](https://palletsprojects.com/p/flask/)
[![Node 18+](https://img.shields.io/badge/node-18+-brightgreen.svg)](https://nodejs.org/)
[![Playwright](https://img.shields.io/badge/playwright-tested-purple.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A beginner-friendly full-stack web application that allows anyone to test website performance, accessibility, best practices, and SEO using **Google Lighthouse**, receive practical fix recommendations in simple language, and execute automated browser login tests using **Playwright**.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Features Implemented](#2-features-implemented)
3. [Technology Stack](#3-technology-stack)
4. [Application Architecture](#4-application-architecture)
5. [Libraries and Dependencies](#5-libraries-and-dependencies)
6. [Prerequisites](#6-prerequisites)
7. [Installation & Setup](#7-installation--setup)
8. [Environment Configuration](#8-environment-configuration)
9. [Running the Web Application](#9-running-the-web-application)
10. [Running the Login Automation Test](#10-running-the-login-automation-test)
11. [Example Usage Walkthrough](#11-example-usage-walkthrough)
12. [Screenshots & Visual Evidence](#12-screenshots--visual-evidence)
13. [Limitations & Known Constraints](#13-limitations--known-constraints)
14. [Future Improvements](#14-future-improvements)

---

## 1. Project Overview

Understanding web performance can be intimidating for beginners. Tools like Google Lighthouse provide vast amounts of technical metrics, but interpreting what those numbers mean and how to fix them can be overwhelming.

This project solves that problem by providing:
- A clean, simple dashboard where users can submit any public URL.
- Automated execution of Google Lighthouse under the hood.
- Clear scores out of 100 for four vital categories: **Performance**, **Accessibility**, **Best Practices**, and **SEO**.
- Plain-English summaries and practical fix recommendations (e.g., how to compress images, eliminate render-blocking CSS, and add missing alt tags).
- A standalone browser automation test using **Playwright** that automates the login workflow for the **Horizon Plus** web app.

---

## 2. Features Implemented

- **Safe URL Validation:** Validates that submitted URLs are not empty, begin with `http://` or `https://`, and contain no harmful characters or shell-injection vectors.
- **Automated Lighthouse Audits:** Runs Google Lighthouse securely in headless Chrome through a specialized Node.js runner.
- **Category Scores Display:** Shows intuitive score cards (0–100) with dynamic color coding:
  - 🟢 **90–100:** Good / Excellent
  - 🟡 **50–89:** Needs Improvement
  - 🔴 **0–49:** Poor
- **Plain-Language Performance Summary:** Automatically evaluates the overall score and gives clear feedback without technical jargon.
- **Actionable Fix Recommendations:** Curates 5–10 critical issues from the audit, explaining:
  - **Problem:** What was detected on the page.
  - **Why it matters:** How it negatively affects real visitors and search engines.
  - **Recommended fix:** Concrete steps to solve the issue.
- **Playwright Login Automation:** Fully automated browser script that tests the login flow on the Horizon Plus streaming web app:
  - Navigates to the application.
  - Locates email and password inputs using stable selectors.
  - Enters credentials loaded securely from environment variables.
  - Submits the form and verifies authentication response.
  - Automatically captures a timestamped full-page screenshot.
  - Prints clear `PASS` or `FAIL` output.
- **Graceful Error Handling:** Displays friendly, informative error banners if a website is down, blocks bots, or fails during an audit.

---

## 3. Technology Stack

- **Frontend:**
  - **HTML5:** Semantic, accessible layout.
  - **CSS3:** Custom responsive styling with CSS variables, flexbox, grid, and animations (no bulky external CSS frameworks).
  - **JavaScript (Vanilla ES6):** Asynchronous `fetch` calls, dynamic DOM manipulation, and interactive state management.
- **Backend:**
  - **Python 3.10+ & Flask:** Lightweight, robust web framework serving the user interface and REST API endpoint (`POST /audit`).
  - **Subprocess Management:** Safely communicates with Node.js without raw shell string concatenation.
- **Performance Engine:**
  - **Node.js (v18+):** Runtime for executing JavaScript tools.
  - **Google Lighthouse:** Industry-standard automated auditing tool for web quality.
  - **Chrome Launcher:** Programmatically launches headless Google Chrome instances with secure sandboxing flags.
- **Browser Automation:**
  - **Playwright (Python):** Modern, reliable browser automation framework used to drive Chromium.
- **Version Control & Security:**
  - **Git & GitHub:** Version tracking with meaningful incremental commits.
  - **python-dotenv:** Safe environment variable management to protect credentials.

---

## 4. Application Architecture

### Web Lighthouse Audit Flow
```
  [User Browser]
       │  (1) Enters URL & clicks "Run Lighthouse Audit"
       ▼
  [Frontend (HTML / CSS / JS)]
       │  (2) POST /audit { "url": "https://example.com" }
       ▼
  [Flask Backend (app.py)]
       │  (3) Validates URL structure & characters
       │  (4) Executes node lighthouse/runner.js <url>
       ▼
  [Lighthouse Runner (Node.js)]
       │  (5) Launches Headless Chrome
       │  (6) Scans site & collects performance metrics
       ▼
  [Lighthouse JSON Output]
       │  (7) Streams JSON report to stdout
       ▼
  [Backend Processing (app.py)]
       │  (8) Calculates scores, summaries & fix recommendations
       ▼
  [Frontend Dynamic Rendering]
          (9) Displays cards, progress bars & recommended fixes
```

### Playwright Login Automation Flow
```
  [Playwright Test (login_test.py)]
       │  (1) Reads HORIZON_USERNAME and HORIZON_PASSWORD from .env
       ▼
  [Launch Chromium Browser]
       │  (2) Opens https://horizon-plus.dfp8hwwhcxnpq.amplifyapp.com/languages
       ▼
  [Navigate to Sign-In Page]
       │  (3) Detects /signin view
       ▼
  [Form Interaction]
       │  (4) Fills input[name="email"] and input[name="pass"]
       │  (5) Clicks "Login Now" button
       ▼
  [Outcome Verification]
       │  (6) Monitors API authentication response & URL redirect
       ├── If Success: Captures screenshots/login-success.png & prints PASS
       └── If Failure: Captures screenshots/login-failed.png & prints FAIL
```

---

## 5. Libraries and Dependencies

### Python Dependencies (`requirements.txt`)
- `Flask>=3.0.0`: Web server and routing.
- `python-dotenv>=1.0.0`: Loads environment variables from `.env`.
- `playwright>=1.40.0`: Browser automation library.
- `requests>=2.31.0`: HTTP client for network checks.

### Node.js Dependencies (`package.json`)
- `lighthouse>=12.0.0`: Google Lighthouse audit core engine.
- `chrome-launcher>=1.1.2`: Utility to launch Google Chrome instances with custom flags.

---

## 6. Prerequisites

Ensure you have the following installed on your operating system:
1. **Python 3.10 or higher:** [python.org/downloads](https://www.python.org/downloads/)
2. **Node.js (LTS version 18 or higher):** [nodejs.org](https://nodejs.org/)
3. **Google Chrome browser:** [google.com/chrome](https://www.google.com/chrome/) (or Chromium)
4. **Git:** [git-scm.com](https://git-scm.com/)

---

## 7. Installation & Setup

Follow these exact beginner-friendly steps to set up the project on your machine:

### Step 1: Clone the Repository
```bash
git clone https://github.com/Aishwaryaa0622/RA-Horizon-Web-Lighthouse-Monitor.git
cd RA-Horizon-Web-Lighthouse-Monitor
```

### Step 2: Set Up Python Virtual Environment
Creating a virtual environment ensures dependencies do not conflict with your global Python installation.

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install Node.js Dependencies
```bash
npm install
```

### Step 5: Install Playwright Browsers
```bash
playwright install chromium
```

---

## 8. Environment Configuration

1. Copy the example configuration template to create your `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in any text editor and configure your variables:
   ```ini
   HORIZON_USERNAME=your_email@example.com
   HORIZON_PASSWORD=your_secure_password
   PORT=5000
   PLAYWRIGHT_HEADLESS=true
   ```

> [!WARNING]
> **Never commit `.env` to GitHub!** Your `.env` file is already listed in `.gitignore` to protect your login credentials from being leaked publicly.

---

## 9. Running the Web Application

Start the Flask application server:

```bash
# With venv activated:
python app.py
```

You will see output similar to:
```text
Starting Web Lighthouse Performance Monitor on http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Open your favorite web browser and visit `http://127.0.0.1:5000`.

---

## 10. Running the Login Automation Test

To execute the Playwright automated login test against Horizon Plus:

```bash
python automation/login_test.py
```

### What happens during the test:
1. Playwright opens headless Chromium.
2. Visits the Horizon Plus application.
3. Navigates to `/signin`.
4. Enters your credentials and clicks **Login Now**.
5. Verifies the result and saves a full screenshot into the `screenshots/` directory.

---

## 11. Example Usage Walkthrough

1. Open `http://127.0.0.1:5000`.
2. In the input box, enter a URL such as `https://example.com` or click one of the quick test chips.
3. Click **Run Lighthouse Audit**.
4. The loading indicator displays while Lighthouse analyzes the website in headless Chrome.
5. Review your results:
   - **Summary Banner:** Overall performance evaluation.
   - **Category Score Cards:** Individual scores for Performance, Accessibility, Best Practices, and SEO.
   - **Recommended Fixes:** Plain-language problem explanations with practical solutions.

---

## 12. Screenshots & Visual Evidence

- **Web Dashboard:** Shows the audit URL field, sample buttons, score cards, progress bars, and fix recommendations.
- **Login Test Screenshot:** Generated automatically after running `automation/login_test.py` and saved to `screenshots/login-success.png` (or `screenshots/login-failed.png`).

---

## 13. Limitations & Known Constraints

- **Bot Protection & Firewalls:** Some websites block automated headless browsers, resulting in audit timeouts.
- **Authentication Barriers:** Lighthouse runs against publicly accessible pages. Pages requiring login or multi-factor authentication cannot be audited without authenticated session tokens.
- **Network Variability:** Lighthouse metrics can fluctuate depending on local internet connection speed and server latency.
- **Third-Party UI Updates:** The Playwright login automation relies on Horizon Plus keeping its current DOM structure. If the login form changes, the selectors in `automation/login_test.py` must be updated.
- **CAPTCHA & MFA:** Playwright cannot and should not bypass CAPTCHA challenges or two-factor authentication prompts.

---

## 14. Future Improvements

- [ ] **Historical Audit Tracking:** Store audit history in SQLite or PostgreSQL to graph improvements over time.
- [ ] **Performance Trend Charts:** Add Chart.js to visualize Core Web Vitals.
- [ ] **Export to PDF / CSV:** Allow developers to download audit reports.
- [ ] **Scheduled Monitoring:** Automatically audit websites on a daily or weekly schedule and send alerts if scores drop below a threshold.
- [ ] **Mobile Emulation Toggle:** Let developers switch between Desktop and Mobile audit profiles.

---

## License

This project is open source and available under the [MIT License](LICENSE).
