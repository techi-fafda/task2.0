# website_analyzer.py
import requests
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Dict

# Initialize Mistral model (load once)
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype="auto"
)

# Create text generation pipeline
mistral_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
    temperature=0.7
)

def clean_html_text(html: str) -> str:
    """Extract and clean text from HTML content"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove unwanted elements
    for tag in soup(["script", "style", "nav", "footer", "header", "form"]):
        tag.decompose()
    
    # Get text and clean
    text = soup.get_text(separator=' ')
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return ' '.join(chunk for chunk in chunks if chunk)

def analyze_website(url: str) -> Dict[str, str]:
    try:
        # Fetch and clean website content
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        clean_text = clean_html_text(response.text)[:3000]  # Limit input size
        
        # Generate company summary
        summary_prompt = f"[INST]Summarize what this company does in 3 sentences:\n{clean_text}[/INST]"
        summary = mistral_pipeline(summary_prompt)[0]['generated_text'].split("[/INST]")[-1].strip()
        
        # Generate blog suggestions
        blog_prompt = f"[INST]Suggest 3 SEO-friendly blog titles for this company:\n{summary}[/INST]"
        blog_output = mistral_pipeline(blog_prompt)[0]['generated_text']
        blogs = [line.strip("-* ") for line in blog_output.split("\n") if line.strip()][:3]
        
        # Recommend marketing channels
        channel_prompt = f"[INST]Recommend best marketing channels from [SEO, PPC, Social Media, Content Marketing]:\n{summary}[/INST]"
        channel_output = mistral_pipeline(channel_prompt)[0]['generated_text']
        channels = [line.strip("-* ") for line in channel_output.split("\n") if line.strip()][:3]

        return {
            "summary": summary,
            "blog_titles": blogs,
            "marketing_channels": channels
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch website: {str(e)}"}
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

# Example usage
if __name__ == "__main__":
    result = analyze_website("https://www.codeant.ai")
    print("Company Summary:", result.get("summary"))
    print("\nBlog Suggestions:", result.get("blog_titles"))
    print("\nMarketing Channels:", result.get("marketing_channels"))
