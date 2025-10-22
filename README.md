# Lottery Results Data Pipeline

This project is an automated data pipeline that scrapes the "Mahajana Sampatha" lottery results from the official NLB website.

It is built to handle dynamic, JavaScript-loaded content and run on a fully automated daily schedule using GitHub Actions. The goal is to build a clean, historical database of all past lottery draws for analysis.

## Features

* **Dynamic Content Scraping:** Uses **Selenium** and `webdriver-manager` to control a headless Chrome browser, allowing it to scrape content that is loaded via JavaScript.
* **Idempotent:** The pipeline is "idempotent," meaning it can be run any number of times without creating duplicate entries. It checks the existing database and only adds new results.
* **Fully Automated:** A **GitHub Actions** workflow runs the pipeline on a daily schedule, so it runs completely "serverlessly" without needing a personal machine to be on.
* **Structured Storage:** Results are cleaned, structured using **Pandas**, and loaded into an **SQLite** database (`lottery.db`).

## Tech Stack

* **Language:** Python 3.10+
* **Web Scraping:** Selenium (to render JS), BeautifulSoup4 (to parse HTML)
* **Data Handling:** Pandas
* **Database:** SQLAlchemy & SQLite
* **Automation:** GitHub Actions

---

## How it Works: The Pipeline

1.  **Schedule:** The GitHub Action workflow is triggered daily at 12:00 PM (Sri Lanka Time).
2.  **Extract:** A virtual Linux runner launches. It installs Google Chrome and our Python libraries.
3.  **Transform:** The `app/main.py` script is executed.
    * Selenium starts a headless Chrome browser.
    * It navigates to the target URL and waits for the JavaScript to load the results table.
    * The page HTML is passed to `BeautifulSoup` and `Pandas` to parse the table.
4.  **Load:**
    * The script connects to the existing `lottery.db` file (if it exists).
    * It compares the scraped draw numbers with the draw numbers already in the database.
    * Only *new* draw results are appended to the `mahajana_sampatha` table.
5.  **Store:** The workflow uploads the updated `lottery.db` file as a GitHub "Artifact," making the latest data available for download.

---

## How to Use

### Local Setup (For Development/Testing)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ChanukaKaviniduLiyanage/lottery-pipeline.git](https://github.com/ChanukaKaviniduLiyanage/lottery-pipeline.git)
    cd lottery-pipeline
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On Mac/Linux
    source venv/bin/activate
    ```

3.  **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the pipeline:**
    ```bash
    python -m app.main
    ```

### Accessing the Automated Data

The `lottery.db` file is updated by the GitHub Action every day.

1.  Go to the **"Actions"** tab of this repository.
2.  Click on the latest successful run under the **"Run Lottery Scraper"** workflow.
3.  Scroll to the bottom of the run's summary page.
4.  Download the **`lottery-database`** artifact.
5.  Unzip the file to get the `lottery.db`. You can open this file with a tool like [DB Browser for SQLite](https://sqlitebrowser.org/) to view the data.
