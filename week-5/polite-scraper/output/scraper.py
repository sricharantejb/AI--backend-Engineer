import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "books.json")

# Polite scraper: identify ourselves
HEADERS = {
    "User-Agent": "PoliteBookScraper/1.0 (Educational Assignment)"
}

# Wait between requests
REQUEST_DELAY = 2

# Number of pages required by the assignment
PAGES_TO_SCRAPE = 3


# ============================================================
# SCHEMA
# ============================================================

REQUIRED_FIELDS = {
    "title",
    "price",
    "currency",
    "availability",
    "rating",
    "url"
}


# ============================================================
# GET PAGE
# ============================================================

def get_page(url):
    """
    Download a webpage safely.
    """

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as e:
        print(f"Failed to download page: {e}")
        return None


# ============================================================
# CLEAN PRICE
# ============================================================

def clean_price(price_text):
    """
    Convert messy price text such as:

        £51.77
        Â£51.77
        Â51.77

    into:

        51.77
    """

    if not price_text:
        raise ValueError("Price is empty")

    # Remove common encoding problems
    price_text = (
        price_text
        .replace("Â", "")
        .replace("£", "")
        .replace(",", "")
        .strip()
    )

    # Keep only numbers and decimal point
    cleaned = re.sub(r"[^0-9.]", "", price_text)

    if not cleaned:
        raise ValueError(f"Invalid price: {price_text}")

    return float(cleaned)


# ============================================================
# CONVERT RATING
# ============================================================

def get_rating(rating_class):
    """
    Convert CSS rating class into an integer.

    Example:

        star-rating Three

    becomes:

        3
    """

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    for word, number in rating_map.items():
        if word in rating_class:
            return number

    return 0


# ============================================================
# VALIDATE BOOK
# ============================================================

def validate_book(book):
    """
    Check that a scraped book contains all required fields
    and that the values have the correct types.
    """

    # Check required fields
    if not REQUIRED_FIELDS.issubset(book.keys()):
        return False

    # Check title
    if not isinstance(book["title"], str) or not book["title"].strip():
        return False

    # Check price
    if not isinstance(book["price"], (int, float)):
        return False

    # Check currency
    if book["currency"] != "GBP":
        return False

    # Check availability
    if not isinstance(book["availability"], str):
        return False

    # Check rating
    if not isinstance(book["rating"], int):
        return False

    if book["rating"] < 1 or book["rating"] > 5:
        return False

    # Check URL
    if not isinstance(book["url"], str) or not book["url"].startswith("http"):
        return False

    return True


# ============================================================
# SCRAPE ONE BOOK
# ============================================================

def scrape_book(book_element):
    """
    Extract one book from the HTML.
    """

    # -----------------------------
    # Title
    # -----------------------------

    title_element = book_element.find("h3").find("a")

    title = title_element.get("title", "").strip()

    if not title:
        raise ValueError("Missing title")

    # -----------------------------
    # Price
    # -----------------------------

    price_element = book_element.find("p", class_="price_color")

    if price_element is None:
        raise ValueError("Missing price")

    price_text = price_element.get_text(strip=True)

    price = clean_price(price_text)

    # -----------------------------
    # Availability
    # -----------------------------

    availability_element = book_element.find(
        "p",
        class_="instock availability"
    )

    if availability_element:
        availability = availability_element.get_text(
            " ",
            strip=True
        )
    else:
        availability = "Unknown"

    # -----------------------------
    # Rating
    # -----------------------------

    rating_element = book_element.find(
        "p",
        class_="star-rating"
    )

    if rating_element:
        rating = get_rating(
            " ".join(rating_element.get("class", []))
        )
    else:
        rating = 0

    # -----------------------------
    # URL
    # -----------------------------

    relative_url = title_element.get("href")

    if not relative_url:
        raise ValueError("Missing URL")

    # Convert relative URL into absolute URL
    book_url = requests.compat.urljoin(
        "https://books.toscrape.com/catalogue/",
        relative_url
    )

    # -----------------------------
    # Create book object
    # -----------------------------

    book = {
        "title": title,
        "price": price,
        "currency": "GBP",
        "availability": availability,
        "rating": rating,
        "url": book_url
    }

    # -----------------------------
    # Validate
    # -----------------------------

    if not validate_book(book):
        raise ValueError("Book failed schema validation")

    return book


# ============================================================
# SCRAPE ONE PAGE
# ============================================================

def scrape_page(page_number):
    """
    Scrape one catalogue page.
    """

    url = BASE_URL.format(page_number)

    print()
    print("=" * 60)
    print(f"Scraping page {page_number}: {url}")
    print("=" * 60)

    html = get_page(url)

    if html is None:
        print("Skipping page because it could not be downloaded.")
        return []

    soup = BeautifulSoup(html, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    print(f"Found {len(books)} books")

    page_books = []

    for book_element in books:

        try:

            book = scrape_book(book_element)

            page_books.append(book)

        except Exception as e:

            print(
                f"Skipping broken book record: {e}"
            )

    print(
        f"Successfully processed {len(page_books)} books"
    )

    return page_books


# ============================================================
# SAVE JSON
# ============================================================

def save_books(books):
    """
    Save books to output/books.json.
    """

    # Automatically create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            books,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("DATA SAVED")
    print("=" * 60)
    print(f"Total books: {len(books)}")
    print(f"File: {OUTPUT_FILE}")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("POLITE BOOK SCRAPER")
    print("=" * 60)

    all_books = []

    # -----------------------------
    # Scrape 3 pages
    # -----------------------------

    for page_number in range(1, PAGES_TO_SCRAPE + 1):

        page_books = scrape_page(page_number)

        all_books.extend(page_books)

        # Wait between requests
        if page_number < PAGES_TO_SCRAPE:

            print()
            print(
                f"Waiting {REQUEST_DELAY} seconds "
                "before next request..."
            )

            time.sleep(REQUEST_DELAY)

    # -----------------------------
    # Save results
    # -----------------------------

    save_books(all_books)

    # -----------------------------
    # Final validation
    # -----------------------------

    print()
    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    if len(all_books) == 60:

        print("SUCCESS: Exactly 60 books were scraped.")

    else:

        print(
            f"WARNING: Expected 60 books, "
            f"but got {len(all_books)}."
        )

    # Check every record
    invalid_books = [
        book
        for book in all_books
        if not validate_book(book)
    ]

    if len(invalid_books) == 0:

        print("SUCCESS: All records passed validation.")

    else:

        print(
            f"WARNING: {len(invalid_books)} "
            "records failed validation."
        )

    print()
    print("Scraping completed.")


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()