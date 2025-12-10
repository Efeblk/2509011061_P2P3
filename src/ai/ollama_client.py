"""Ollama AI client for local LLM inference."""

import json
import requests
from typing import Optional
from loguru import logger

from config.settings import settings


class OllamaClient:
    """
    Client for Local Ollama API.
    Mimics the interface of GeminiClient for easy swapping.
    """

    def __init__(self):
        """Initialize Ollama client."""
        self.base_url = settings.ollama.base_url
        self.model = settings.ollama.model

    def embed(self, text: str) -> Optional[list[float]]:
        """
        Generate embedding vector for text using Ollama.

        Args:
            text: Text to embed

        Returns:
            List of floats (embedding vector) or None if failed
        """
        try:
            url = f"{self.base_url}/api/embeddings"
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get("embedding")

        except Exception as e:
            logger.error(f"Error generating embedding with Ollama: {e}")
            return None

    def generate(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate text completion.

        Args:
            prompt: Input prompt
            temperature: Creativity (0-1)

        Returns:
            Generated text or None if failed
        """
        return self._generate_request(prompt, temperature=temperature, format=None)

    def generate_json(self, prompt: str, temperature: float = 0.3) -> Optional[dict]:
        """
        Generate JSON response.

        Args:
            prompt: Input prompt
            temperature: Creativity

        Returns:
            Parsed JSON dict or None if failed
        """
        # Append logic to enforce JSON if not in prompt
        json_prompt = prompt
        if "json" not in prompt.lower():
            json_prompt += "\nRespond strictly with VALID JSON."

        result = self._generate_request(json_prompt, temperature=temperature, format="json")

        if not result:
            return None
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from Ollama: {result[:100]}...")
            return None

    def _generate_request(self, prompt: str, temperature: float, format: Optional[str] = None) -> Optional[str]:
        """Internal method for generation request."""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_ctx": 4096  # Reasonable context window
                }
            }
            
            if format == "json":
                payload["format"] = "json"

            response = requests.post(url, json=payload, timeout=120)  # Local LLMs can be slow
            response.raise_for_status()
            
            return response.json().get("response")

        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return None

# Global instance
ollama_client = OllamaClient()
