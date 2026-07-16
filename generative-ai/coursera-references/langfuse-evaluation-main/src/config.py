"""
Configuration for Conecta Evaluation System
"""
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProviderType(Enum):
    """AI Provider types"""
    GEMINI = "gemini"
    VERTEX = "vertex"


class ModelType(Enum):
    """Model types for different tasks"""
    FLASH = "flash"  # Fast, cheap - for simple tasks
    PRO = "pro"      # Powerful, expensive - for critical tasks


@dataclass
class EvaluatorConfig:
    """Configuration for the evaluation system"""

    # Provider selection
    provider: ProviderType = ProviderType.GEMINI

    # API Keys
    gemini_api_key: Optional[str] = None
    vertex_project_id: Optional[str] = None
    vertex_location: str = "us-central1"

    # Model configurations
    flash_model_name: str = "gemini-2.0-flash-exp"
    pro_model_name: str = "gemini-1.5-pro"  # Use gemini-1.5-pro (without -002 suffix)

    # Agent assignments (which model for each agent)
    document_relevance_model: ModelType = ModelType.FLASH
    hallucination_detector_model: ModelType = ModelType.PRO  # Critical task
    completeness_checker_model: ModelType = ModelType.FLASH
    escalation_validator_model: ModelType = ModelType.FLASH
    verification_agent_model: ModelType = ModelType.PRO  # Critical task

    # Model parameters
    temperature: float = 0.1  # Low temperature for consistent evaluations
    max_output_tokens: int = 4096

    # Rate limiting and timeouts
    requests_per_minute: int = 60
    max_retries: int = 3
    api_timeout: int = 120  # Timeout for API calls in seconds (2 minutes)

    # Evaluation thresholds
    hallucination_verification_threshold: str = "minor"  # Verify all hallucinations
    parallel_agents: bool = True  # Run independent agents in parallel

    # A/B Testing
    prompt_version: str = "v1"  # "v1" (lenient) or "v2" (strict)

    # File paths
    data_dir: str = "."
    output_dir: str = "./results"

    def __post_init__(self):
        """Load API keys from environment if not provided"""
        if self.gemini_api_key is None:
            self.gemini_api_key = os.getenv('GEMINI_API_KEY')

        if self.vertex_project_id is None:
            self.vertex_project_id = os.getenv('VERTEX_PROJECT_ID')

    def get_model_name(self, model_type: ModelType) -> str:
        """Get the actual model name for a model type"""
        if model_type == ModelType.FLASH:
            return self.flash_model_name
        elif model_type == ModelType.PRO:
            return self.pro_model_name
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def validate(self) -> bool:
        """Validate configuration"""
        if self.provider == ProviderType.GEMINI and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY must be set for Gemini provider")

        if self.provider == ProviderType.VERTEX and not self.vertex_project_id:
            raise ValueError("VERTEX_PROJECT_ID must be set for Vertex provider")

        return True


# Default configuration
DEFAULT_CONFIG = EvaluatorConfig()
