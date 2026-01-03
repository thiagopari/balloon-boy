"""
Web Fetch Tool - Retrieve actual webpage content
Different from web_search which only returns snippets
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional

class WebFetchTool:
    """
    Fetch and extract text content from URLs
    Enables reading actual webpages, not just search results
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_url(self, url: str, max_length: int = 10000) -> str:
        """
        Fetch content from a URL
        
        Args:
            url: URL to fetch
            max_length: Maximum characters to return (prevent huge pages)
            
        Returns:
            Text content of the page
        """
        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            print(f"    📡 Fetching {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            # Truncate if too long
            if len(cleaned_text) > max_length:
                cleaned_text = cleaned_text[:max_length] + f"\n\n[Truncated - original length: {len(cleaned_text)} chars]"
            
            print(f"    ✓ Retrieved {len(cleaned_text)} characters")
            return cleaned_text
            
        except requests.Timeout:
            return f"Error: Request to {url} timed out"
        except requests.RequestException as e:
            return f"Error fetching {url}: {str(e)}"
        except Exception as e:
            return f"Error parsing {url}: {str(e)}"


# Tool definition for OpenAI function calling
def get_fetch_tool_definition() -> dict:
    """OpenAI function definition for web fetch"""
    return {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": (
                "Fetch and read the actual content of a specific webpage. "
                "Use this when you have a URL and need to read what's on that page. "
                "Different from web_search - this retrieves the actual page content, "
                "not search results about it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch (e.g., 'https://thiagopari.github.io/ThiagoPari')"
                    }
                },
                "required": ["url"]
            }
        }
    }


# Example usage
if __name__ == "__main__":
    fetcher = WebFetchTool()
    
    # Test fetching your portfolio
    content = fetcher.fetch_url("https://thiagopari.github.io/ThiagoPari")
    print(content[:1000])
