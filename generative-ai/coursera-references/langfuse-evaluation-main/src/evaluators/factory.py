"""
Factory for creating LLM providers
"""
import logging
from typing import Optional

from ..config import EvaluatorConfig, ProviderType, ModelType
from .base import BaseLLMProvider
from .providers.gemini_provider import GeminiProvider
from .providers.vertex_provider import VertexProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating LLM providers"""

    @staticmethod
    def create_provider(
        config: EvaluatorConfig,
        model_type: ModelType
    ) -> BaseLLMProvider:
        """
        Create an LLM provider based on configuration

        Args:
            config: Evaluator configuration
            model_type: Type of model (FLASH or PRO)

        Returns:
            Configured LLM provider
        """
        model_name = config.get_model_name(model_type)

        if config.provider == ProviderType.GEMINI:
            if not config.gemini_api_key:
                raise ValueError("Gemini API key not provided")

            logger.info(f"Creating Gemini provider with model: {model_name}")
            return GeminiProvider(
                api_key=config.gemini_api_key,
                model_name=model_name,
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                max_retries=config.max_retries,
                timeout=config.api_timeout
            )

        elif config.provider == ProviderType.VERTEX:
            if not config.vertex_project_id:
                raise ValueError("Vertex project ID not provided")

            logger.info(f"Creating Vertex AI provider with model: {model_name}")
            return VertexProvider(
                project_id=config.vertex_project_id,
                location=config.vertex_location,
                model_name=model_name,
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                max_retries=config.max_retries
            )

        else:
            raise ValueError(f"Unknown provider type: {config.provider}")

    @staticmethod
    def create_all_providers(config: EvaluatorConfig) -> dict:
        """
        Create all providers needed for the evaluation system

        Args:
            config: Evaluator configuration

        Returns:
            Dictionary mapping agent names to their providers
        """
        providers = {}

        # Create Flash provider (for simple tasks)
        flash_provider = ProviderFactory.create_provider(config, ModelType.FLASH)

        # Create Pro provider (for critical tasks)
        pro_provider = ProviderFactory.create_provider(config, ModelType.PRO)

        # Assign providers to agents based on config
        providers['document_relevance'] = flash_provider if config.document_relevance_model == ModelType.FLASH else pro_provider
        providers['hallucination_detector'] = flash_provider if config.hallucination_detector_model == ModelType.FLASH else pro_provider
        providers['completeness_checker'] = flash_provider if config.completeness_checker_model == ModelType.FLASH else pro_provider
        providers['escalation_validator'] = flash_provider if config.escalation_validator_model == ModelType.FLASH else pro_provider
        providers['verification_agent'] = flash_provider if config.verification_agent_model == ModelType.FLASH else pro_provider

        logger.info(f"Created {len(set(providers.values()))} unique providers for {len(providers)} agents")

        return providers
