"""
Gemini API provider implementation
"""
import time
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. Install with: pip install google-generativeai")

from ..base import BaseLLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Gemini API provider"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.1,
        max_output_tokens: int = 4096,
        max_retries: int = 3,
        timeout: int = 120  # 2 minutes default timeout
    ):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")

        super().__init__(model_name, temperature, max_output_tokens)

        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                'temperature': temperature,
                'max_output_tokens': max_output_tokens,
            }
        )

        logger.info(f"Initialized Gemini provider with model: {model_name}")

    def generate(self, prompt: str) -> str:
        """
        Generate response from Gemini

        Args:
            prompt: Input prompt

        Returns:
            Generated text
        """
        for attempt in range(self.max_retries):
            try:
                # Wrap API call with timeout
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self.model.generate_content, prompt)
                    try:
                        response = future.result(timeout=self.timeout)
                    except FuturesTimeoutError:
                        logger.warning(f"Gemini API timeout after {self.timeout}s (attempt {attempt + 1}/{self.max_retries})")
                        if attempt < self.max_retries - 1:
                            wait_time = 2 ** attempt
                            logger.info(f"Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise TimeoutError(f"Gemini API timed out after {self.timeout} seconds")

                # Check for safety blocks
                if not response.text:
                    logger.warning(f"Empty response from Gemini (attempt {attempt + 1})")
                    if hasattr(response, 'prompt_feedback'):
                        logger.warning(f"Prompt feedback: {response.prompt_feedback}")
                    continue

                return response.text

            except TimeoutError:
                raise  # Re-raise timeout errors
            except Exception as e:
                logger.warning(f"Gemini API error (attempt {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

        raise RuntimeError(f"Failed to get response from Gemini after {self.max_retries} attempts")
