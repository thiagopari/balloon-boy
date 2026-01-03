"""
Tool Manager for Balloon Boy
Manages all available tools and their execution
"""
from tools.web_fetch import WebFetchTool, get_fetch_tool_definition
from ddgs import DDGS
from datetime import datetime
from typing import Dict, Callable, List
import json
from tools.resume_generator import ResumeGenerator

class ToolManager:
    """
    Central registry for all Balloon Boy's tools
    
    Current tools:
    - get_current_date: Returns actual current date
    - web_search: Search the internet for information
    - search_news: Search for recent news
    """
    
    def __init__(self):
        self.search = DDGS()
        self.fetcher = WebFetchTool()
        self.tools = {}  # name -> function mapping
        self.definitions = []  # OpenAI function definitions
        self.resume_gen = ResumeGenerator()

        # Register built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register all built-in tools"""
        
        # Tool 1: Get current date
        self.register_tool(
            name="get_current_date",
            function=self._get_current_date,
            definition={
                "type": "function",
                "function": {
                    "name": "get_current_date",
                    "description": "Get the actual current date and time. Use when asked 'what is today's date', 'what day is it', or when you need to know the current date.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        )
        
        # Tool 2: Web search
        self.register_tool(
            name="web_search",
            function=self._web_search,
            definition={
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": (
                        "Search the internet for current information. "
                        "Use for: movie reviews, current events, recent news, "
                        "weather, sports scores, product info, or any information "
                        "beyond your knowledge cutoff (October 2023)."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., 'Primate movie 2024 reviews', 'weather Boston today')"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Number of results to return (1-5)",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        )
        
        # Tool 3: News search
        self.register_tool(
            name="search_news",
            function=self._search_news,
            definition={
                "type": "function",
                "function": {
                    "name": "search_news",
                    "description": "Search specifically for recent news articles. Use when asked about recent events, breaking news, or current happenings.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "News search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Number of news articles (1-5)",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        )

        # Tool 4: Generate tailored resume
        self.register_tool(
            name="generate_tailored_resume",
            function=self._generate_resume,
            definition={
                "type": "function",
                "function": {
                    "name": "generate_tailored_resume",
                    "description": "Generate a tailored resume PDF for a job. Analyzes job description, selects best matching projects, compiles to PDF in ~/resumes/",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "job_description": {
                                "type": "string",
                                "description": "Full job description text"
                            },
                            "company_name": {
                                "type": "string",
                                "description": "Company name (for filename)"
                            },
                            "position_name": {
                                "type": "string",
                                "description": "Position title (for filename)"
                            }
                        },
                        "required": ["job_description", "company_name", "position_name"]
                    }
                }
            }
        )
        # Tool 5: Fetch webpage content
        self.register_tool(
            name = "fetch_webpage",
            function = self._fetch_webpage,
            definition = get_fetch_tool_definition()
        )
    def _fetch_webpage(self,url:str) -> str:
        """Fetch webpage content (tool implementation)"""
        return self.fetcher.fetch_url(url)

    def _generate_resume(self, job_description: str, company_name: str, position_name: str) -> str:
        """Generate resume tool implementation"""
        result = self.resume_gen.generate_resume(job_description, company_name, position_name)
        
        if result["status"] == "success":
            return (
                f"✅ Resume generated!\n\n"
                f"📄 PDF: {result['pdf_path']}\n\n"
                f"Projects: {result['projects_used']}\n"
                f"{result['analysis']['reasoning']}"
            )
        else:
            return f"❌ Failed: {result.get('error', 'Unknown error')}"
            
    def register_tool(self, name: str, function: Callable, definition: Dict):
        """Register a new tool"""
        self.tools[name] = function
        self.definitions.append(definition)
    
    def execute_tool(self, name: str, **kwargs) -> str:
        """Execute a tool by name"""
        if name not in self.tools:
            return f"Error: Unknown tool '{name}'"
        
        try:
            result = self.tools[name](**kwargs)
            return result
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get all tool definitions for OpenAI API"""
        return self.definitions
    
    # Built-in tool implementations
    
    def _get_current_date(self) -> str:
        """Get current date"""
        now = datetime.now()
        return now.strftime("%B %d, %Y at %I:%M %p")  # e.g., "January 02, 2026 at 03:45 PM"
    
    def _web_search(self, query: str, max_results: int = 3) -> str:
        """Search the web"""
        try:
            results = list(self.search.text(query, max_results=max_results))
            
            if not results:
                return "No results found."
            
            # Format results
            output = f"Search results for '{query}':\n\n"
            for i, r in enumerate(results, 1):
                output += f"{i}. {r.get('title', 'No title')}\n"
                output += f"   {r.get('body', 'No description')}\n"
                output += f"   URL: {r.get('href', 'No URL')}\n\n"
            
            return output
            
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    def _search_news(self, query: str, max_results: int = 3) -> str:
        """Search for news"""
        try:
            results = list(self.search.news(query, max_results=max_results))
            
            if not results:
                return "No news found."
            
            # Format results
            output = f"News results for '{query}':\n\n"
            for i, r in enumerate(results, 1):
                output += f"{i}. {r.get('title', 'No title')}\n"
                output += f"   {r.get('body', 'No description')}\n"
                output += f"   Date: {r.get('date', 'Unknown')}\n"
                output += f"   URL: {r.get('url', 'No URL')}\n\n"
            
            return output
            
        except Exception as e:
            return f"News search failed: {str(e)}"


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Create tool manager
    tools = ToolManager()
    
    # Create OpenAI client with tools
    client = OpenAIClientWithTools(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )
    
    # Register all tools
    for tool_def in tools.get_tool_definitions():
        tool_name = tool_def["function"]["name"]
        
        # Use closure to capture tool_name
        def make_tool_func(name):
            return lambda **kwargs: tools.execute_tool(name, **kwargs)
        
        client.register_tool(
            name=tool_name,
            function=make_tool_func(tool_name),
            definition=tool_def
        )
    
    # Test: Ask about current date
    print("\n📅 Testing date tool...")
    messages = [Message(role="user", content="What is today's date?")]
    response = client.generate_with_tools(messages)
    print(f"Response: {response}\n")
    
    # Test: Ask about a movie
    print("\n🎬 Testing web search...")
    messages = [Message(role="user", content="Tell me about the movie Primate and if it's any good")]
    response = client.generate_with_tools(messages)
    print(f"Response: {response}")
