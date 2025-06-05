
# === Standard Library ===
import re
from collections import Counter
from typing import List
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

# === Third-party Libraries ===
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

# === Local Imports ===
from metadata_extractor import extract_metadata

from scraper import outbounds
from keyword_extractor import get_target_keywords
from keyword_extractor import get_core_pages, extract_keywords_from_page
from local_llm_summary_and_blogs import analyze_website


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield

app = FastAPI(lifespan=lifespan)



@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get("/meta_data")
@cache(expire=3600)
async def analyze_meta(url: str = Query(..., description="Website URL to analyze")):
    """
    Extracts title, meta description, and H1 tags from the given website URL.
    """
    metadata = extract_metadata(url)
    if "error" in metadata:
        return JSONResponse(content=metadata, status_code=400)
    return JSONResponse(content=metadata)



@app.get("/outbound-links")
@cache(expire=3600)
async def outbound_links(url: str = Query(..., description="Website URL to extract outbound links from")):
    
    links = outbounds(url)
    if isinstance(links, dict) and "error" in links:
        return JSONResponse(content=links, status_code=400)
        print("something bad happened in the outbound links extractor")
    return JSONResponse(content={"outbound_links": links})



@app.get("/target-keywords")
@cache(expire=3600)
async def target_keywords(url: str = Query(..., description="Website URL to analyze")):
    """
    Scrapes core pages and extracts probable target keywords
    """
    result = get_target_keywords(url)
    return JSONResponse(content=result)



@app.get("/analyze-website")  # this is on device llm, it gives the summary, blog posts and channels
@cache(expire=3600)
async def analyze_website_endpoint(url: str = Query(..., description="Website URL to analyze")):
    """
    Analyzes a website and provides:
    - Company summary
    - Blog post suggestions
    - Marketing channel recommendations
    """
    result = analyze_website(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result)


@app.get("/company-summary")  #this uses openai api
@cache(expire=3600)
async def company_summary(url: str = Query(..., description="Website URL to analyze")):
    """
    Summarizes the company's offering and recommends marketing channels.
    """
    result = analyze_website(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result)





@app.get("/suggest-blogs") #this uses openai api
@cache(expire=3600) 
async def suggest_blogs_endpoint(url: str = Query(..., description="Website URL to analyze")):
    """
    Suggests 3 SEO-friendly blog post titles for the company.
    """
 #   result = suggest_blogs(url)
  #  if "error" in result:
 #       return JSONResponse(content=result, status_code=400)
   # return JSONResponse(content=result)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("centre:app", host="127.0.0.1", port=8000, reload=True)
