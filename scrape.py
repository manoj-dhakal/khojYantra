import os
import requests
import json
from bs4 import BeautifulSoup

# List of base URLs for the main pages
BASE_URLS = [
    "https://nkp.gov.np/advance_search/?Submit=Yes&year=2075&month=7",
    "https://nkp.gov.np/advance_search/?Submit=Yes&year=2075&month=8",
    # Add more URLs as needed
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

def extract_links_from_main_page(main_page_url):
    """Extract all article links from the main search page."""
    html_content = fetch_page_content(main_page_url)
    if html_content is None:
        print("Failed to fetch the main page content.")
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    article_links = []

    # Update the selector to match the structure of the links on the main page
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/full_detail/" in href:  # Filter relevant links
            full_link = href if href.startswith("http") else "https://nkp.gov.np" + href
            article_links.append(full_link)
    
    return list(set(article_links))  # Return unique links

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

def process_base_url(base_url):
    """Process a single base URL."""
    print(f"Fetching links from the main page: {base_url}")
    article_links = extract_links_from_main_page(base_url)
    print(f"Found {len(article_links)} article links.")

    for article_url in article_links:
        print(f"Processing: {article_url}")

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