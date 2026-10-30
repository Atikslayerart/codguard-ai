# AI Usage Log

## Tools used

- ChatGPT and Perplexity for debugging, understanding errors, and finding solutions.
- AI assistant for project planning, code structure, and documentation drafting.
- VS Code for development.
- Python, pandas, Flask, HTML, CSS, and JavaScript for implementation.

## How AI was used

I wrote and tested the project myself, but I used ChatGPT and Perplexity as debugging and learning assistants throughout the build.

Specifically, I used AI to:

- Understand the assignment and break it into smaller build steps.
- Set up the Python virtual environment and install missing packages such as pandas and Flask.
- Debug errors such as `ModuleNotFoundError`, incorrect CSV file paths, and missing columns.
- Understand why the dashboard was not loading data and fix mismatched API field names.
- Get help with Flask routes, pandas grouping, JavaScript event listeners, and CSS layout issues.
- Draft parts of the documentation, which I reviewed and edited to match the actual project.

## Where AI was wrong or weak

### 1. Wrong column name

AI initially suggested grouping the data by a column called `customer_history`.

**Problem:** My cleaned dataset does not have that column. The correct column is `customer_prior_rto`.

**Fix:** I checked the dataset columns using `df.columns`, replaced the wrong column name, and reran the analysis.

### 2. Incorrect financial framing

AI initially presented an estimated savings number as if it were a confirmed result.

**Problem:** The calculation assumed that half of prepaid nudges prevent an RTO and did not properly account for discount costs or customers who would have paid prepaid anyway.

**Fix:** I changed the dashboard and memo to clearly label the number as an illustrative estimate, not a measured saving.

### 3. Overly complex frontend suggestion

AI initially suggested building a larger multi-page application with separate routes and more UI components.

**Problem:** It would have taken more time and made the project harder to run quickly.

**Fix:** I used a single-page dashboard with JavaScript-based page switching instead.

### 4. Navigation not working initially

AI gave JavaScript that used different class and ID names from my HTML.

**Problem:** The sidebar links did not switch pages because the JavaScript was selecting the wrong elements.

**Fix:** I compared the HTML IDs and `data-page` values with the JavaScript selectors, then corrected the code.

## Verification approach

- Ran every backend script and checked the terminal output.
- Compared dashboard totals with the cleaned dataset: 1,987 orders and 565 RTOs.
- Verified that address-group RTO rates added up correctly.
- Tested the order analyzer with low-risk, medium-risk, and high-risk example orders.
- Tested WhatsApp flows for YES, NO, random replies, 24-hour timeout, and payment simulation.
- Fixed errors myself after using AI to understand the cause.