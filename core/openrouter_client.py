"""OpenRouter API client."""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    def __init__(self, api_key: str = None):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key
        """
        # Priority order: passed parameter > st.secrets > environment variable > None
        if api_key:
            self.api_key = api_key
        else:
            # Try st.secrets first (for Streamlit Cloud), then fall back to env var
            try:
                if hasattr(st, 'secrets') and "OPENROUTER_API_KEY" in st.secrets:
                    self.api_key = st.secrets["OPENROUTER_API_KEY"]
                else:
                    self.api_key = os.getenv("OPENROUTER_API_KEY")
            except Exception:
                # If secrets aren't available, use environment variable
                self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        self.base_url = "https://openrouter.ai/api/v1"
        
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Mono33/linda-quiz-generator",
                "X-Title": "Linda Quiz Generator"
            }
        else:
            self.headers = {}

    def is_available(self) -> bool:
        """Check if OpenRouter API is available and API key is valid."""
        if not self.api_key:
            return False
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Generate text using the OpenRouter API.

        Args:
            model: Name of the model to use
            prompt: Prompt to send to the model
            temperature: Temperature for sampling
            max_tokens: Maximum number of tokens to generate

        Returns:
            Generated text
        """
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                st.error("No response generated from the model")
                return ""
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling OpenRouter API: {e}")
            return ""


