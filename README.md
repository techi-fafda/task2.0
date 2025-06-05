# Website Analyzer FastAPI Project

This project is a FastAPI-based web service for analyzing websites. It provides endpoints to extract metadata, outbound links, keywords, company summaries, and SEO blog suggestions from a given website URL.

## Features

- **Metadata Extraction**: Extracts the title, meta description, and H1 tags from a website.
- **Outbound Links**: Lists all outbound links found on a website.
- **Target Keywords**: Scrapes core pages and extracts probable target keywords.
- **Company Summary**: Summarizes the company's offering and recommends marketing channels (using OpenAI).
- **Blog Suggestions**: Suggests 3 SEO-friendly blog post titles for the company (using OpenAI).

## Project Structure

```
.
├── main.py
├── metadata_extractor.py
├── scraper.py
├── keyword_extractor.py
├── local_llm_summary_and_blogs.py
├── requirements.txt
├── .gitignore
└── README.md
```

## How It Works

- The main API is defined in `main.py` using FastAPI.
- Caching is handled with Redis via `fastapi_cache`.
- Each endpoint calls a function from the respective module to process the URL and return results as JSON.
- OpenAI is used for advanced summarization and blog suggestions.

## API Endpoints

- `GET /meta_data?url=...`  
  Extracts title, meta description, and H1 tags.

- `GET /outbound-links?url=...`  
  Lists outbound links from the website.

- `GET /target-keywords?url=...`  
  Extracts probable target keywords from core pages.

- `GET /analyze-website?url=...`  
  Provides a company summary, blog suggestions, and marketing channel recommendations.

- `GET /company-summary?url=...`  
  Summarizes the company's offering and recommends marketing channels.

- `GET /suggest-blogs?url=...`  
  Suggests 3 SEO-friendly blog post titles.

## Setup

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**  
   Set the `OPENAI_API_KEY` environment variable.

3. **Start Redis:**  
   Make sure Redis is running locally on the default port (`localhost:6379`).

4. **Run the FastAPI server:**
   ```sh
   uvicorn main:app --reload
   ```
