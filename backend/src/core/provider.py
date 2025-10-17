import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

class LLMProvider:
    def __init__(self, requests_per_minute=15):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.requests_per_minute = requests_per_minute
        self.delay = 60.0 / requests_per_minute
        self.last_request_time = 0

    def generate(self, prompt: str) -> str:
        """
        Generates content based on a given prompt with rate limiting.
        """
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        
        self.last_request_time = time.time()

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error during text generation: {e}")
            return ""

# Singleton instance
llm_provider = LLMProvider()
