import os
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import PyPDF2
from ddgs import DDGS
import wikipedia
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_url_downloadable(url):
    """Checks if a URL is alive and does not return an HTTP 500/403/404 error."""
    # Fix DuckDuckGo providing '+' instead of '%20' for spaces in sansad.in paths
    if 'sansad.in' in url:
        url = url.replace('+', '%20')
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Try a fast HEAD request first
        response = requests.head(url, headers=headers, timeout=5, verify=False, allow_redirects=True)
        if response.status_code == 200:
            return True
        # Fallback to GET stream if HEAD is blocked
        response = requests.get(url, headers=headers, timeout=10, verify=False, stream=True)
        return response.status_code == 200
    except Exception:
        return False

def search_bill_url(query):
    search_query = f"site:sansad.in {query} filetype:pdf"
    print(f"Searching for: {search_query}")
    
    # Trust natural search engine ranking for the exact PDF first, then fallback to sites
    queries = [
        f"{query} filetype:pdf",
        f"site:sansad.in {query} filetype:pdf",
        f"{query} filetype:pdf site:india.gov.in",
        f"{query} filetype:pdf site:prsindia.org"
    ]
    
    try:
        with DDGS() as ddgs:
            for sq in queries:
                try:
                    print(f"Trying DDGS query: {sq}")
                    # Fetch more results to allow for manual strict filtering
                    results = list(ddgs.text(sq, max_results=10))
                    if not results:
                        continue
                        
                    # Pass 1: Strict Government Domain Priority
                    trusted_domains = ['sansad.in', 'india.gov.in', 'prsindia.org', 'nic.in']
                    for r in results:
                        url = r['href'].lower()
                        if any(domain in url for domain in trusted_domains):
                            if is_url_downloadable(r['href']):
                                print(f"-> Selected and verified trusted government link: {url}")
                                return {"url": r['href'], "title": r.get('title', f"Document for {query}")}
                            else:
                                print(f"-> Skipped dead/blocked government link: {url}")
                            
                    # Pass 2: Soft Fallback (Must be PDF, definitely NOT Wikipedia)
                    for r in results:
                        url = r['href'].lower()
                        if 'wikipedia.org' not in url and url.endswith('.pdf'):
                            if is_url_downloadable(r['href']):
                                print(f"-> Selected and verified secondary PDF link: {url}")
                                return {"url": r['href'], "title": r.get('title', f"Document for {query}")}
                            else:
                                print(f"-> Skipped dead/blocked secondary PDF link: {url}")
                            
                except Exception as e:
                    print(f"Query '{sq}' failed: {e}")
                    continue
    except Exception as e:
        print(f"DDGS Client failed: {e}")
        
    print("All DDGS searches failed. Falling back to Wikipedia...")
    try:
        # Try to find the closest Wikipedia page for the query
        wiki_results = wikipedia.search(f"{query} bill india")
        if not wiki_results:
            wiki_results = wikipedia.search(query)
            
            
        if wiki_results:
            # Iterate through results to find a valid page
            for result_title in wiki_results:
                try:
                    wiki_page = wikipedia.page(result_title, auto_suggest=False)
                    return {"url": wiki_page.url, "title": wiki_page.title}
                except wikipedia.exceptions.DisambiguationError as e:
                    # If disambiguation, try the first option
                    try:
                        wiki_page = wikipedia.page(e.options[0], auto_suggest=False)
                        return {"url": wiki_page.url, "title": wiki_page.title}
                    except:
                        continue
                except wikipedia.exceptions.PageError:
                    continue
    except Exception as e:
        print(f"Wikipedia fallback failed: {e}")

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
        
        # Fix DuckDuckGo providing '+' instead of '%20' for spaces in sansad.in paths
        if 'sansad.in' in url:
            url = url.replace('+', '%20')
        
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
