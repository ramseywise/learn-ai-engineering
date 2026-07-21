"""
Base classes for evaluators
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Base class for evaluation results"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    raw_response: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            **self.data,
            'error': self.error
        }


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, model_name: str, temperature: float = 0.1, max_output_tokens: int = 4096):
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate response from LLM

        Args:
            prompt: Input prompt

        Returns:
            Generated text response
        """
        pass

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Generate and parse JSON response

        Args:
            prompt: Input prompt (should request JSON output)

        Returns:
            Parsed JSON dictionary
        """
        response = self.generate(prompt)

        try:
            # Try to extract JSON from markdown code blocks
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response[:500]}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")


class BaseAgent(ABC):
    """Abstract base class for evaluation agents"""

    def __init__(self, llm_provider: BaseLLMProvider, agent_name: str):
        self.llm = llm_provider
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")

    @abstractmethod
    def get_prompt(self, **kwargs) -> str:
        """
        Get the prompt template for this agent

        Args:
            **kwargs: Variables to fill in the prompt

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def parse_response(self, response: Dict[str, Any]) -> EvaluationResult:
        """
        Parse the LLM response into a structured result

        Args:
            response: Raw JSON response from LLM

        Returns:
            Structured evaluation result
        """
        pass

    def evaluate(self, **kwargs) -> EvaluationResult:
        """
        Run the evaluation

        Args:
            **kwargs: Input data for evaluation

        Returns:
            Evaluation result
        """
        try:
            # Get prompt
            prompt = self.get_prompt(**kwargs)

            # Generate response
            self.logger.info(f"Running {self.agent_name} evaluation...")
            response = self.llm.generate_json(prompt)

            # Parse response
            result = self.parse_response(response)
            result.raw_response = str(response)

            self.logger.info(f"{self.agent_name} completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"{self.agent_name} failed: {e}")
            return EvaluationResult(
                success=False,
                data={},
                error=str(e)
            )
