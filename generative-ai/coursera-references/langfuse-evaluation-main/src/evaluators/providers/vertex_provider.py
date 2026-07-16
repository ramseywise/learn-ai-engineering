"""
Vertex AI provider implementation
"""
import time
import logging
from typing import Optional

try:
    from vertexai.preview.generative_models import GenerativeModel
    import vertexai
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False
    logging.warning("Vertex AI SDK not installed. Install with: pip install google-cloud-aiplatform")

from ..base import BaseLLMProvider

logger = logging.getLogger(__name__)


class VertexProvider(BaseLLMProvider):
    """Vertex AI provider"""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.1,
        max_output_tokens: int = 4096,
        max_retries: int = 3
    ):
        if not VERTEX_AVAILABLE:
            raise ImportError("google-cloud-aiplatform package not installed")

        super().__init__(model_name, temperature, max_output_tokens)

        self.project_id = project_id
        self.location = location
        self.max_retries = max_retries

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Initialize model
        self.model = GenerativeModel(model_name)

        logger.info(f"Initialized Vertex AI provider with model: {model_name}")
        logger.info(f"Project: {project_id}, Location: {location}")

    def generate(self, prompt: str) -> str:
        """
        Generate response from Vertex AI

        Args:
            prompt: Input prompt

        Returns:
            Generated text
        """
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': self.temperature,
                        'max_output_tokens': self.max_output_tokens,
                    }
                )

                # Check for valid response
                if not response.text:
                    logger.warning(f"Empty response from Vertex AI (attempt {attempt + 1})")
                    continue

                return response.text

            except Exception as e:
                logger.warning(f"Vertex AI error (attempt {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

        raise RuntimeError(f"Failed to get response from Vertex AI after {self.max_retries} attempts")
