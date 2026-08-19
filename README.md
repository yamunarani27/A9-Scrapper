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

## Lane

| | |
|---|---|
| Language | Python 3.10+ (free, python.org) |
| HTTP requests | Requests |
| HTML parser | Beautiful Soup |
| Schema validator | Pydantic |
| Output | Built-in `json` module → JSON |
| Target | Books to Scrape — a sandbox built for practice |

## How to install and run

```bash
pip install -r requirements.txt
python main.py
```

This produces `output/books.json` and `output/run-report.json`.

## Record schema

Each record in `output/books.json` follows this shape:

| Field | Type | Required | Notes |
|---|---|---|---|
| `product_url` | string (URL) | Yes | Canonical identity of the record; always starts with `https://` |
| `title` | string | Yes | Book title |
| `price_text` | string | Yes | Raw price as shown on the page, e.g. `"£51.77"` |
| `price_gpb` | float | Yes | Cleaned numeric price, e.g. `51.77` |
| `availability_text` | string | Yes | Stock status text |
| `rating_text` | string | Yes | Star rating word, e.g. `"Three"` |
| `description` | string or `null` | No | Some books have no description on the site; stored as `null`, never invented |
| `source_page` | string | Yes | Which cached catalogue page this book was discovered on |
| `fetched_at` | string (ISO 8601 UTC) | Yes | Timestamp of when the book's detail page was fetched |

## Politeness rules

- **Honest User-Agent**: every request identifies this bot by name with a link to this repo, so a site owner can see who's visiting and why.
- **Timeout**: every request gives up after 5 seconds rather than hanging indefinitely.
- **Caching**: every fetched page (catalogue and book detail) is saved to `cache/` and re-read from disk on subsequent runs, so re-running the script during development does not repeatedly hit the live site.
- **Selective retry**: timeouts and server errors (5xx) are retried once after a short delay; not-found (404) and forbidden (403) responses are never retried, since retrying those wouldn't help and would just add unnecessary load.

## Sample run report

```json
{
  "start_time": "2026-08-19T12:16:28Z",
  "duration": 0.358055,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}
```

## Why this assignment needed no browser

Book data from `https://books.toscrape.com/` appears directly in the raw HTML returned by the first request — nothing is added by JavaScript after the page loads — so a full browser was not needed for this assignment.

## Ethics note

This site is an official sandbox built for scraping practice, so no API exists here — but on a real project, an official API would always be preferred over scraping when one is available. This scraper never attempts to bypass logins, paywalls, or blocks (a 403 response is treated as final, not retried) — a refusal from the site is respected, not worked around. Only the specific fields needed for this assignment were collected, not the entire site.

## Known limitation

This scraper only fetches 3 of the site's ~50 catalogue pages (60 of the site's ~1000 books). It was scoped to a fixed sample for this assignment, not built to crawl the full catalogue.