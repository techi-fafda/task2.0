# keyword_extractor.py
import re
import json
from typing import List
from collections import Counter # Import necessary libraries
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# Load Mistral model and tokenizer (load once)
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

# Create text generation pipeline
keyword_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=100,
    temperature=0.3
)

def get_core_pages(main_url: str) -> List[str]:
    """Identify core pages (home, about, products/services, contact)"""
    try:
        res = requests.get(main_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        core_links = []
        nav_links = soup.find_all('a', href=True)
        
        # Common patterns for core pages
        core_keywords = ['about', 'product', 'service', 'contact', 'features']
        
        for link in nav_links:
            href = link['href'].lower()
            if any(kw in href for kw in core_keywords):
                absolute_url = urljoin(main_url, link['href'])
                core_links.append(absolute_url)
        
        # Ensure homepage is included
        core_links.append(main_url)
        
        # Remove duplicates
        return list(set(core_links))[:5]  # Max 5 core pages
        
    except Exception as e:
        return []

def extract_keywords_from_page(url: str) -> List[str]:
    """Use Mistral AI to extract keywords from page content"""
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        text = soup.get_text(separator=' ')
        text = text[:3000]  # Limit text length for model input
        
        # Prepare prompt for keyword extraction
        prompt = f"""<s>[INST]Analyze this text and extract the top 10 most important keywords 
        for SEO, focusing on business offerings and products. Return only a JSON array:
        {text}[/INST]"""
        
        # Generate keywords
        output = keyword_pipeline(prompt)[0]['generated_text']
        
        # Extract JSON array from output
        try:
            json_str = output.split("[/INST]")[-1].strip()
            keywords = json.loads(json_str)
            if isinstance(keywords, list):
                return keywords[:10]
            return []
        except json.JSONDecodeError:
            return []
            
    except Exception as e:
        return []

def get_target_keywords(main_url: str) -> dict:
    """Main function to get keywords from core pages using Mistral AI"""
    core_pages = get_core_pages(main_url)
    all_keywords = []
    
    for page in core_pages:
        all_keywords.extend(extract_keywords_from_page(page))
        
    # Aggregate and rank keywords
    keyword_counts = Counter(all_keywords)
    return {
        "core_pages": core_pages,
        "keywords": [kw for kw, count in keyword_counts.most_common(15)]
    }