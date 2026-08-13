## The polite scrapper
A small, polite scraping pipeline: it downloads the first three catalogue pages of Books to Scrape, visits all 60 book pages, turns messy HTML into clean, checked JSON records, survives a broken page without crashing, and ends every run with a short report of what happened.

## Target classification

* **Target Site:** Books to Scrape (`https://books.toscrape.com/`)
* **Why this site:** The site explicitly states on `toscrape.com` that it is a sandbox built specifically for people to practice web scraping on.
* **Scope / How much:** First 3 catalogue pages only.
* **Data collected:** Book Title, Price, Availability, Rating, Product_url and  Description
* **Robots.txt Result:**Request - https://books.toscrape.com/robots.txt gave result 'No robots file found' with a status code 404.
**Appropriateness:** Scraping this site is appropriate because it is a dedicated testing sandbox designed specifically for scraping practice.

> **Note:** I will not reuse this code on another site without checking its rules and terms first.