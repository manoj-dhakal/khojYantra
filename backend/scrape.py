import os
import requests
import json
from bs4 import BeautifulSoup

# List of base URLs for the main pages
BASE_URLS = [
    "https://nkp.gov.np/advance_search/?Submit=Yes&year=2080", #226 
    "https://nkp.gov.np/advance_search/?Submit=Yes&year=2079", #207
    "https://nkp.gov.np/advance_search/?Submit=Yes&year=2078", #191
    "https://nkp.gov.np/advance_search/?Submit=Yes&year=2077" #
    
]

# Folder to save the scraped articles
OUTPUT_FOLDER = "scraped_articles"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def fetch_page_content(url):
    """Fetch content from a given URL."""
    response = requests.get(url, verify=False)  # Bypass SSL for simplicity
    if response.status_code == 200:
        response.encoding = "utf-8"
        return response.text
    return None


def extract_links_from_main_page(base_url):
    """Extract all article links using per_page-based pagination."""
    article_links = set()
    per_page = 0
    step = 20
    max_pages = 100  # Safety limit

    while per_page <= step * max_pages:
        if per_page == 0:
            url = f"{base_url}"
        else:
            url = f"{base_url}&per_page={per_page}"

        print(f"Fetching articles from: {url}")
        html_content = fetch_page_content(url)
        if html_content is None:
            print(f"Failed to fetch page at per_page={per_page}. Stopping.")
            break

        soup = BeautifulSoup(html_content, "html.parser")
        new_links = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/full_detail/" in href:
                full_link = href if href.startswith("http") else "https://nkp.gov.np" + href
                new_links.add(full_link)

        if not new_links:
            print("No more articles found. Pagination complete.")
            break

        before = len(article_links)
        article_links.update(new_links)
        after = len(article_links)

        if before == after:
            print("No new unique links added. Ending.")
            break

        per_page += step
        time.sleep(1)

    print(f"Total unique articles found: {len(article_links)}")
    return list(article_links)


def extract_article_details(article_url):
    """Extract required information from the article page."""
    html_content = fetch_page_content(article_url)
    if html_content is None:
        return None

    soup = BeautifulSoup(html_content, "html.parser")

    # Extract post title
    title = None
    title_tag = soup.find("h1", class_="post-title")
    if title_tag and title_tag.a:
        title = title_tag.a.text.strip()

    # Extract edition info
    edition_info = None
    edition_info_div = soup.find("div", id="edition-info")
    if edition_info_div:
        edition_info = " | ".join(
            [span.text.strip() for span in edition_info_div.find_all("span")]
        )

    # Extract post meta
    post_meta = None
    post_meta_div = soup.find("div", class_="post-meta")
    if post_meta_div:
        post_meta = post_meta_div.text.strip()

    # Extract faisala detail
    faisala_detail = None
    faisala_div = soup.find("div", id="faisala_detail ")
    if faisala_div:
        paragraphs = faisala_div.find_all("p")
        if paragraphs:
            faisala_detail = "\n".join([para.text.strip() for para in paragraphs])

    return {
        "Title": title,
        "Edition Info": edition_info,
        "Post Meta": post_meta,
        "Faisala Detail": faisala_detail,
    }

def save_article_to_json(article_details, folder):
    """Save the extracted details into a JSON file."""
    title = article_details.get("Title", "Untitled")
    safe_title = title.replace("/", "-").replace("\\", "-")  # Sanitize title for file names
    file_path = os.path.join(folder, f"{safe_title}.json")
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(article_details, f, ensure_ascii=False, indent=4)

import time

def process_base_url(base_url):
    print(f"Fetching links from the main page: {base_url}")
    article_links = extract_links_from_main_page(base_url)
    print(f"Found {len(article_links)} article links.")

    for article_url in article_links:
        print(f"Processing: {article_url}")
        time.sleep(1)  # ⏱️ Add a 1-second delay between article requests

        try:
            article_details = extract_article_details(article_url)
            if article_details and article_details.get("Faisala Detail"):  # Ensure faisala detail exists
                save_article_to_json(article_details, OUTPUT_FOLDER)
                print(f"Saved article: {article_details.get('Title', 'Untitled')}")
            else:
                print(f"Skipped article: {article_url} (No Faisala Detail found)")
        except Exception as e:
            print(f"Error processing article: {article_url}. Error: {e}")
def main():
    for base_url in BASE_URLS:
        process_base_url(base_url)

if __name__ == "__main__":
    # Disable SSL warnings (optional)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
