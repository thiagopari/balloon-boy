"""
OpenAI Client with Function Calling Support
"""
from openai import OpenAI
from typing import List, Dict, Optional, Callable
import json

class Message:
    """Standard message format"""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class OpenAIClientWithTools:
    """
    OpenAI client that supports function calling (tools)
    
    Enables agentic behavior:
    - Model decides when to use tools
    - Executes tool functions
    - Returns results to model
    - Model generates final response
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.model = model
        # Simplified initialization to avoid httpx version conflicts
        self.client = OpenAI(api_key=api_key)
        self.available_tools = {}  # name -> function mapping
        self.tool_definitions = []  # OpenAI tool definitions
        
    def register_tool(self, name: str, function: Callable, definition: Dict):
        """
        Register a tool that the model can call
        
        Args:
            name: Tool name (must match definition)
            function: Python function to execute
            definition: OpenAI function definition dict
        """
        self.available_tools[name] = function
        self.tool_definitions.append(definition)
        print(f"  ✓ Registered tool: {name}")
    
    def generate_with_tools(
        self,
        messages: List[Message],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        max_tool_iterations: int = 5
    ) -> str:
        """
        Generate response with automatic tool use
        
        The model will:
        1. Decide if it needs tools
        2. Call tools if needed
        3. Use tool results to generate final answer
        
        Args:
            messages: Conversation history
            max_tokens: Max tokens in response
            temperature: Sampling temperature
            max_tool_iterations: Max tool calls before forcing response
            
        Returns:
            Final response text
        """
        # Convert to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        iteration = 0
        
        while iteration < max_tool_iterations:
            iteration += 1
            
            # Call OpenAI with tools available
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                tools=self.tool_definitions if self.tool_definitions else None,
                tool_choice="auto"  # Let model decide
            )
            
            message = response.choices[0].message
            
            # Check if model wants to use tools
            if message.tool_calls:
                # Model requested tool use
                print(f"  🔧 Model requested {len(message.tool_calls)} tool(s)")
                
                # Add assistant's tool request to conversation
                openai_messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"    → Calling {function_name}({function_args})")
                    
                    # Execute the tool
                    if function_name in self.available_tools:
                        try:
                            result = self.available_tools[function_name](**function_args)
                            result_str = json.dumps(result) if not isinstance(result, str) else result
                        except Exception as e:
                            result_str = f"Error executing {function_name}: {str(e)}"
                            print(f"      ❌ {result_str}")
                    else:
                        result_str = f"Error: Unknown tool {function_name}"
                        print(f"      ❌ {result_str}")
                    
                    # Add tool result to conversation
                    openai_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str
                    })
                
                # Continue loop - model will use tool results to generate response
                
            else:
                # Model provided final answer (no tool use)
                return message.content
        
        # Max iterations reached, return what we have
        return message.content if message.content else "I apologize, I couldn't complete that request."
    
    def generate(
        self,
        messages: List[Message],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """
        Main generation method
        Automatically uses tools if registered, otherwise simple generation
        """
        if self.tool_definitions:
            # Use tool-enabled generation
            return self.generate_with_tools(messages, max_tokens, temperature)
        else:
            # Simple generation without tools
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
    
    def is_available(self) -> bool:
        """Check if API key is valid"""
        try:
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            print(f"OpenAI availability check failed: {e}")
            return False


# Test the tool system
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize client
    client = OpenAIClientWithTools(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )
    
    # Define a simple test tool
    def get_current_date() -> str:
        return datetime.now().strftime("%B %d, %Y")
    
    # Register it
    client.register_tool(
        name="get_current_date",
        function=get_current_date,
        definition={
            "type": "function",
            "function": {
                "name": "get_current_date",
                "description": "Get the current date",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    )
    
    # Test
    messages = [Message(role="user", content="What is today's date?")]
    response = client.generate_with_tools(messages)
    print(f"Response: {response}")