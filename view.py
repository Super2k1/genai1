# To run this code you need to install the following dependencies:
# pip install google-genai python-dotenv

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate(user_input: str = None):
    """Generate content using Gemini API with advanced reasoning.
    
    Args:
        user_input: The text prompt to send to the model. If None, prompts user.
    """
    if user_input is None:
        user_input = input("Enter your prompt: ")
    
    if not user_input.strip():
        print("Error: Input cannot be empty")
        return
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        return
    
    try:
        client = genai.Client(api_key=api_key)
        
        model = "gemini-2.0-flash-lite"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)],
            ),
        ]
        
        tools = [types.Tool(google_search=types.GoogleSearch())]
        
        generate_content_config = types.GenerateContentConfig(
            system_instruction="Use deep reasoning to provide comprehensive answers.",
            tools=tools,
        )
        
        print("\n" + "="*50)
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate()
