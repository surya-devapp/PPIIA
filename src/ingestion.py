import os
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import PyPDF2
from duckduckgo_search import DDGS

def search_bill_url(query):
    """
    Searches specifically for a PDF on sansad.in or general web matching the bill name.
    """
    search_query = f"site:sansad.in {query} filetype:pdf"
    print(f"Searching for: {search_query}")
    try:
        results = DDGS().text(search_query, max_results=5)
        if results:
            # Return the first result's URL and Title
            first_result = results[0]
            return {"url": first_result['href'], "title": first_result['title']}
    except Exception as e:
        print(f"Search failed: {e}")
        # Fallback to broader search if site:sansad.in fails? 
        # For now, let's keep it strict or try a secondary query without site constraint but keeping filetype:pdf
        try:
             broad_query = f"{query} bill india filetype:pdf"
             results = DDGS().text(broad_query, max_results=3)
             if results:
                 return {"url": results[0]['href'], "title": results[0]['title']}
        except:
            pass
            
    return None

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file object (stream) or path.
    """
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_url(url):
    """
    Fetches content from a URL.
    Attempts to parse main text or handle PDF URLs.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        # Check URL ending or Content-Disposition if header misses application/pdf
        if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
            f = BytesIO(response.content)
            return extract_text_from_pdf(f)
        else:
            # Assume HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract text from p, h1, h2, h3, h4, h5, h6, li
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'article'])
            text = "\n".join([t.get_text(strip=True) for t in text_elements])
            return text
            
    except Exception as e:
        return f"Error fetching URL: {e}"
