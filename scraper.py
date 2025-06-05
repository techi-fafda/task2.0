# scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def outbounds(url: str):
    """Fetch outbound links from the given URL."""
    try:
        res = requests.get(url)
        html = res.text
    except Exception as e:
        return {"error": f"Could not fetch the website: {str(e)}"}

    soup = BeautifulSoup(html, 'html.parser')
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc

    links = []
    for tag in soup.find_all('a', href=True):
        link = tag['href']
        # Convert relative URLs to absolute
        link = urljoin(url, link)
        # Check if link is outbound
        if urlparse(link).netloc != base_domain:
            links.append(link)

    # Remove duplicates
    links = list(set(links))

    return links

def main():
    test_url = "https://www.codeant.ai"  # Hardcoded URL for proof of concept
    print(f"Testing get_outbound_links with URL: {test_url}")
    result = outbounds(test_url)
    print("\n--- Outbound Links ---")
    if isinstance(result, dict) and "error" in result:
        print(f"Error: {result['error']}")
    elif not result:
        print("No outbound links found.")
    else:
        for i, link in enumerate(result, 1):
            print(f"{i}. {link}")

if __name__ == "__main__":
    main()
