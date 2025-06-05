import requests
from bs4 import BeautifulSoup

def extract_metadata(url: str) -> dict:
    """Extract title, description, and H1 tags from the given website URL."""
    try:
        r = requests.get(url)
        r.raise_for_status()
        html = r.text
    except Exception as e:
        return {"error": f"Could not fetch the website: {e}"}

    soup = BeautifulSoup(html, 'html.parser')

    title = soup.title.string if soup.title else None

    desc_tag = soup.find('meta', attrs={'name': 'description'})
    description = desc_tag['content'] if desc_tag and 'content' in desc_tag.attrs else None

    h1_tags = [h.text.strip() for h in soup.find_all('h1')]

    return {
        "title": title,
        "description": description,
        "h1_tags": h1_tags
    }

def main():
    # Hardcoded URL for proof of concept
    url = "https://www.codeant.ai"
    print(f"Extracting metadata from: {url}")
    metadata = extract_metadata(url)

    print("\n--- Website Metadata ---")
    if "error" in metadata:
        print(f"Error: {metadata['error']}")
    else:
        print(f"Title: {metadata.get('title') or 'N/A'}")
        print(f"Description: {metadata.get('description') or 'N/A'}")
        print("\nH1 Tags:")
        if metadata.get('h1_tags'):
            for i, h1 in enumerate(metadata['h1_tags'], 1):
                print(f"  {i}. {h1}")
        else:
            print("  No H1 tags found.")

if __name__ == "__main__":
    main()
