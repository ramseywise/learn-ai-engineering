"""
Verification Agent
Secondary verification for critical findings (especially hallucinations)
"""
import logging
from typing import Dict, Any

from ..base import BaseAgent, BaseLLMProvider, EvaluationResult
from ...utils.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class VerificationAgent(BaseAgent):
    """Agent that provides secondary verification of critical findings"""

    def __init__(self, llm_provider: BaseLLMProvider):
        super().__init__(llm_provider, "VerificationAgent")

    def get_prompt(
        self,
        original_finding: Dict[str, Any],
        user_question: str,
        ai_response: str,
        documents: str,
        **kwargs
    ) -> str:
        """Get the verification prompt"""
        template = PromptTemplates.verification_agent()

        return template.format(
            original_finding=str(original_finding),
            user_question=user_question,
            ai_response=ai_response,
            documents=documents
        )

    def parse_response(self, response: Dict[str, Any]) -> EvaluationResult:
        """Parse verification response"""
        try:
            data = {
                'verified': response.get('verified', False),
                'severity_adjustment': response.get('severity_adjustment', 'none'),
                'new_severity': response.get('new_severity', 'none'),
                'explanation': response.get('explanation', ''),
                'final_recommendation': response.get('final_recommendation', 'review')
            }

            return EvaluationResult(success=True, data=data)

        except Exception as e:
            self.logger.error(f"Failed to parse verification response: {e}")
            return EvaluationResult(success=False, data={}, error=str(e))

    def verify_hallucination(
        self,
        hallucination_result: EvaluationResult,
        user_question: str,
        ai_response: str,
        documents: str
    ) -> EvaluationResult:
        """
        Convenience method to verify a hallucination finding

        Args:
            hallucination_result: Original hallucination detection result
            user_question: User's question
            ai_response: AI's response
            documents: Documents used

        Returns:
            Verification result
        """
        return self.evaluate(
            original_finding=hallucination_result.data,
            user_question=user_question,
            ai_response=ai_response,
            documents=documents
        )
