"""Gemini AI client with caching and retry logic."""

import json
import time
from typing import Optional
import hashlib

import google.generativeai as genai
from loguru import logger

from config.settings import settings


class GeminiClient:
    """
    Client for Google Gemini API with built-in caching and retry logic.
    """

    def __init__(self, model_name: Optional[str] = None):
        """Initialize Gemini client."""
        api_key = settings.gemini.api_key

        # Validate API key
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "Invalid Gemini API key. Please set GEMINI_API_KEY in your .env file.\n"
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name or settings.gemini.model)
        self._cache = {}  # Simple in-memory cache

    def _get_cache_key(self, text: str, task: str = "default") -> str:
        """Generate cache key from text."""
        content = f"{task}:{text}"
        return hashlib.md5(content.encode()).hexdigest()

    def embed(self, text: str, use_cache: bool = True) -> Optional[list[float]]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed
            use_cache: Whether to use cache

        Returns:
            List of floats (embedding vector) or None if failed
        """
        cache_key = self._get_cache_key(text, "embed")

        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Cache hit for embedding: {text[:50]}...")
            return self._cache[cache_key]

        # Generate embedding
        try:
            result = genai.embed_content(model="models/embedding-001", content=text, task_type="retrieval_document")

            embedding = result["embedding"]

            # Cache result
            if use_cache:
                self._cache[cache_key] = embedding

            logger.debug(f"Generated embedding for: {text[:50]}...")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    async def generate(self, prompt: str, temperature: float = 0.7, use_cache: bool = True, retry: int = 3) -> Optional[str]:
        """
        Generate text completion.

        Args:
            prompt: Input prompt
            temperature: Creativity (0-1)
            use_cache: Whether to use cache
            retry: Max retry attempts

        Returns:
            Generated text or None if failed
        """
        import asyncio
        
        cache_key = self._get_cache_key(prompt, f"gen_{temperature}")

        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Cache hit for generation: {prompt[:50]}...")
            return self._cache[cache_key]

        # Generate with retry
        for attempt in range(retry):
            try:
                def make_request():
                    return self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(temperature=temperature),
                    )

                response = await asyncio.to_thread(make_request)
                result = response.text

                # Cache result
                if use_cache:
                    self._cache[cache_key] = result

                logger.debug(f"Generated text for: {prompt[:50]}...")
                return result

            except Exception as e:
                error_msg = str(e).lower()

                # Check for API key issues
                if "api" in error_msg and ("key" in error_msg or "auth" in error_msg or "invalid" in error_msg):
                    logger.error(f"API authentication failed. Please check your GEMINI_API_KEY in .env file: {e}")
                    return None

                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")

                if attempt < retry - 1:
                    # Exponential backoff
                    sleep_time = 2**attempt
                    logger.info(f"Retrying in {sleep_time}s...")
                    await asyncio.sleep(sleep_time)
                else:
                    logger.error(f"All retry attempts failed: {e}")
                    return None

        return None

    async def generate_json(self, prompt: str, temperature: float = 0.3, use_cache: bool = True) -> Optional[dict]:
        """
        Generate JSON response.

        Args:
            prompt: Input prompt (should ask for JSON)
            temperature: Creativity (lower for JSON)
            use_cache: Whether to use cache

        Returns:
            Parsed JSON dict or None if failed
        """
        result = await self.generate(prompt, temperature=temperature, use_cache=use_cache)

        if not result:
            return None

        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            clean_result = result.strip()
            if clean_result.startswith("```json"):
                clean_result = clean_result[7:]
            if clean_result.startswith("```"):
                clean_result = clean_result[3:]
            if clean_result.endswith("```"):
                clean_result = clean_result[:-3]

            return json.loads(clean_result.strip())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {result}")
            return None


# Lazy-initialized global client instance
class _GeminiClientProxy:
    """Proxy to lazy-load GeminiClient only when actually used."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = GeminiClient()
        return self._client

    def __getattr__(self, name):
        return getattr(self._get_client(), name)

gemini_client = _GeminiClientProxy()
