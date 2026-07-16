"""
Completeness Checker Agent
Evaluates if Conecta's response is complete given available documents
"""
import logging
from typing import Dict, Any

from ..base import BaseAgent, BaseLLMProvider, EvaluationResult
from ...utils.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class CompletenessChecker(BaseAgent):
    """Agent that checks if response is complete"""

    def __init__(self, llm_provider: BaseLLMProvider):
        super().__init__(llm_provider, "CompletenessChecker")

    def get_prompt(
        self,
        user_question: str,
        ai_response: str,
        documents: str,
        **kwargs
    ) -> str:
        """Get the completeness checking prompt"""
        template = PromptTemplates.completeness_checker()

        return template.format(
            user_question=user_question,
            ai_response=ai_response,
            documents=documents
        )

    def parse_response(self, response: Dict[str, Any]) -> EvaluationResult:
        """Parse completeness response"""
        try:
            data = {
                'completeness_score': int(response.get('completeness_score', 0)),
                'used_all_relevant_info': response.get('used_all_relevant_info', False),
                'missing_information': response.get('missing_information', []),
                'unnecessary_clarification': response.get('unnecessary_clarification', False),
                'explanation': response.get('explanation', '')
            }

            return EvaluationResult(success=True, data=data)

        except Exception as e:
            self.logger.error(f"Failed to parse completeness response: {e}")
            return EvaluationResult(success=False, data={}, error=str(e))
