from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin
import logging

def extract_web_content(response_text, base_url=None):
    """
    Extract text content from HTML and JavaScript in a web response.
    
    Args:
        response_text (str): The raw HTML response text
        base_url (str, optional): Base URL for resolving relative URLs
        
    Returns:
        dict: Dictionary containing extracted text content, structured data, and metadata
    """
    
    def clean_text(text):
        """Remove extra whitespace and normalize text"""
        if not text:
            return ""
        return " ".join(text.split())
    
    def extract_js_content(script_text):
        """Extract text content and data from JavaScript"""
        content = []
        
        # Extract string literals
        string_literals = re.findall(r'["\']([^"\'\\]*(?:\\.[^"\'\\]*)*)["\']', script_text)
        
        # Extract JSON-like objects
        json_pattern = r'\{[^{}]*\}'
        potential_json = re.finditer(json_pattern, script_text)
        
        for match in potential_json:
            try:
                json_obj = json.loads(match.group())
                # Recursively extract text from JSON object
                def extract_text_from_json(obj):
                    if isinstance(obj, str):
                        return [obj]
                    elif isinstance(obj, (list, tuple)):
                        return [item for sublist in [extract_text_from_json(i) for i in obj] for item in sublist]
                    elif isinstance(obj, dict):
                        return [item for sublist in [extract_text_from_json(v) for v in obj.values()] for item in sublist]
                    return []
                
                content.extend(extract_text_from_json(json_obj))
            except json.JSONDecodeError:
                continue
        
        # Filter and clean extracted content
        content.extend(string_literals)
        content = [clean_text(text) for text in content if text and len(text) > 3]
        return list(set(content))  # Remove duplicates
    
    try:
        soup = BeautifulSoup(response_text, 'html.parser')
        extracted_content = {
            'visible_text': [],
            'metadata': {
                'title': '',
                'description': '',
                'keywords': []
            },
            'js_content': [],
            'links': [],
            'structured_data': []
        }
        
        # Extract metadata
        title_tag = soup.find('title')
        if title_tag:
            extracted_content['metadata']['title'] = clean_text(title_tag.string)
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            extracted_content['metadata']['description'] = clean_text(meta_desc['content'])
        
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            extracted_content['metadata']['keywords'] = [k.strip() for k in meta_keywords['content'].split(',')]
        
        # Extract visible text content
        for text in soup.stripped_strings:
            cleaned = clean_text(text)
            if cleaned and cleaned not in extracted_content['visible_text']:
                extracted_content['visible_text'].append(cleaned)
        
        # Extract and process JavaScript content
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                js_content = extract_js_content(script.string)
                extracted_content['js_content'].extend(js_content)
        
        # Extract links
        if base_url:
            for link in soup.find_all('a', href=True):
                full_url = urljoin(base_url, link['href'])
                link_text = clean_text(link.get_text())
                if link_text and full_url:
                    extracted_content['links'].append({
                        'url': full_url,
                        'text': link_text
                    })
        
        # Extract structured data (JSON-LD)
        structured_data = soup.find_all('script', type='application/ld+json')
        for data in structured_data:
            try:
                if data.string:
                    json_data = json.loads(data.string)
                    extracted_content['structured_data'].append(json_data)
            except json.JSONDecodeError:
                continue
        
        return extracted_content
        
    except Exception as e:
        logging.error(f"Error extracting content: {str(e)}")
        return None