# The Polite Scraper

## Overview

A Python web scraper that collects 60 books from
Books to Scrape across three pages.

The scraper:

- Uses a descriptive User-Agent
- Waits between requests
- Extracts book information
- Cleans price values
- Validates records
- Handles request failures
- Saves clean JSON output

## Technologies

- Python
- Requests
- BeautifulSoup
- Pydantic

## Project Structure

```text
polite-scraper/
├── scraper.py
├── requirements.txt
├── README.md
├── .gitignore
└── output/
    └── books.json