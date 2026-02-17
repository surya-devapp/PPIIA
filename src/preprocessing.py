import re

def clean_text(text):
    """
    Basic text cleaning.
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text, chunk_size=3000, overlap=200):
    """
    Splits text into chunks for LLM processing.
    Simple character-based splitting for now.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks
