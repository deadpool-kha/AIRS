"""
Ollama client wrapper for AIRS.
Handles local LLM communication with retry logic.
"""

import logging
import time

import requests

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama local LLM API."""

    DEFAULT_HOST = "http://localhost:11434"
    DEFAULT_MODEL = "qwen2.5:7b"

    def __init__(self, host: str = None, model: str = None):
        self.host = host or self.DEFAULT_HOST
        self.model = model or self.DEFAULT_MODEL
        self.generate_url = f"{self.host}/api/generate"

    def generate(self, prompt: str, model: str = None, timeout: int = 60) -> str:
        """
        Generate text from Ollama with retry.

        Args:
            prompt: The prompt to send
            model: Override default model
            timeout: Request timeout in seconds

        Returns:
            Generated text string

        Raises:
            ConnectionError: If Ollama is not running
            RuntimeError: If generation fails after retries
        """
        model = model or self.model
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower = more factual for analysis
                "num_predict": 512,  # Limit token output
            },
        }

        # Retry up to 3 times
        for attempt in range(3):
            try:
                response = requests.post(
                    self.generate_url,
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()

            except requests.exceptions.ConnectionError:
                logger.error(f"Ollama not running at {self.host}. Start with: ollama serve")
                raise ConnectionError(f"Ollama not available at {self.host}")

            except requests.exceptions.Timeout:
                wait = 2 ** attempt
                logger.warning(f"Ollama timeout, retrying in {wait}s... (attempt {attempt + 1}/3)")
                time.sleep(wait)

            except Exception as e:
                logger.error(f"Ollama generation error: {e}")
                raise RuntimeError(f"LLM generation failed: {e}")

        raise RuntimeError("LLM generation failed after 3 retries")

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False