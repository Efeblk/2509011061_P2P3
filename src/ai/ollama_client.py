"""Ollama AI client for local LLM inference."""

import json
import os
import requests
from typing import Optional, Any
from loguru import logger

from config.settings import settings


class OllamaClient:
    """
    Client for Local Ollama API.
    Mimics the interface of GeminiClient for easy swapping.
    """

    def __init__(self, model_name: Optional[str] = None):
        """Initialize Ollama client."""
        self.base_url = settings.ollama.base_url
        self.model = model_name or settings.ollama.model

        # Validate Ollama connection on startup
        try:
            health_timeout = int(os.getenv("OLLAMA_HEALTH_TIMEOUT", "5"))
            response = requests.get(f"{self.base_url}/api/tags", timeout=health_timeout)
            response.raise_for_status()
            logger.debug(f"Successfully connected to Ollama at {self.base_url}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}.\n"
                f"Please ensure Ollama is running:\n"
                f"  - Install: https://ollama.ai/download\n"
                f"  - Run: ollama serve\n"
                f"  - Pull model: ollama pull {self.model}"
            )
        except Exception as e:
            logger.warning(f"Could not verify Ollama connection: {e}")

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
            payload = {"model": settings.ollama.model_embedding, "prompt": text}

            embed_timeout = int(os.getenv("OLLAMA_EMBED_TIMEOUT", "30"))
            response = requests.post(url, json=payload, timeout=embed_timeout)
            response.raise_for_status()

            data = response.json()
            return data.get("embedding")

        except Exception as e:
            logger.error(f"Error generating embedding with Ollama: {e}")
            return None

    async def generate(self, prompt: str, temperature: float = 0.7, model: Optional[str] = None) -> Optional[str]:
        """
        Generate text completion.

        Args:
            prompt: Input prompt
            temperature: Creativity (0-1)
            model: Optional model override

        Returns:
            Generated text or None if failed
        """
        return await self._generate_request(prompt, temperature=temperature, format=None, model=model)

    async def generate_json(
        self,
        prompt: str,
        temperature: float = 0.3,
        model: Optional[str] = None,
        schema: Optional[Any] = None,
    ) -> Optional[dict]:
        """
        Generate JSON response.

        Args:
            prompt: Input prompt
            temperature: Creativity
            model: Optional model override
            schema: Optional Pydantic model to validate response

        Returns:
            Parsed JSON dict or None if failed
        """
        # Append logic to enforce JSON if not in prompt
        json_prompt = prompt
        if "json" not in prompt.lower():
            json_prompt += "\nRespond strictly with VALID JSON."

        # If schema provided, append instruction
        # If schema provided, append robust instruction
        if schema:
            # Instead of dumping the full JSON schema (which confuses some local models),
            # we try to generate a dummy example or just use a simplified prompt.
            # Ideally, we should construct a "Example JSON" based on the schema fields.

            try:
                # Basic field extraction for a cleaner prompt
                # schema.model_fields is available in Pydantic v2
                fields = getattr(schema, "model_fields", {})
                example_dict = {}
                for name, field in fields.items():
                    # Create dummy values based on type annotation (simplified)
                    # We utilize the description if available to hint the model
                    desc = field.description or "value"
                    example_dict[name] = f"<{desc}>"

                json_prompt += f"\n\nReturn a JSON object that matches the following example structure:\n{json.dumps(example_dict, indent=2)}"
            except Exception:
                # Fallback if introspection fails
                json_prompt += f"\n\nReturn JSON object that matches this schema:\n{json.dumps(schema.model_json_schema(), indent=2)}"

        result = await self._generate_request(json_prompt, temperature=temperature, format="json", model=model)

        if not result:
            return None

        try:
            data = json.loads(result)

            # Validate with schema if provided
            if schema:
                try:
                    validated = schema.model_validate(data)
                    return validated.model_dump()
                except Exception as e:
                    logger.error(f"Schema validation failed: {e}")
                    return None

            return data

        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from Ollama: {result[:100]}...")
            return None

    async def _generate_request(
        self, prompt: str, temperature: float, format: Optional[str] = None, model: Optional[str] = None
    ) -> Optional[str]:
        """Internal method for generation request."""
        import asyncio

        try:
            url = f"{self.base_url}/api/generate"
            context_size = int(os.getenv("OLLAMA_CONTEXT_SIZE", "2048"))
            payload = {
                "model": model or self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_ctx": context_size},
            }

            if format == "json":
                payload["format"] = "json"

            # Run blocking request in thread pool
            generate_timeout = int(os.getenv("OLLAMA_GENERATE_TIMEOUT", "120"))
            def make_request():
                return requests.post(url, json=payload, timeout=generate_timeout)

            response = await asyncio.to_thread(make_request)
            response.raise_for_status()

            return response.json().get("response")

        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out. The model might be too slow or the prompt too long.")
            return None
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return None


# Lazy-initialized global client instance
class _OllamaClientProxy:
    """Proxy to lazy-load OllamaClient only when actually used."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = OllamaClient()
        return self._client

    def __getattr__(self, name):
        return getattr(self._get_client(), name)


ollama_client = _OllamaClientProxy()
