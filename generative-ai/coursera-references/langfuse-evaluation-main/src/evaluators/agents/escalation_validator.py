"""
Escalation Validator Agent
Validates if the decision to escalate to human expert was appropriate
"""
import logging
from typing import Dict, Any, Optional

from ..base import BaseAgent, BaseLLMProvider, EvaluationResult
from ...utils.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class EscalationValidator(BaseAgent):
    """Agent that validates escalation decisions"""

    def __init__(self, llm_provider: BaseLLMProvider):
        super().__init__(llm_provider, "EscalationValidator")

    def get_prompt(
        self,
        user_question: str,
        ai_response: str,
        documents: str,
        escalated: bool = False,
        escalation_reason: Optional[str] = None,
        **kwargs
    ) -> str:
        """Get the escalation validation prompt"""
        template = PromptTemplates.escalation_validator()

        return template.format(
            user_question=user_question,
            ai_response=ai_response,
            documents=documents,
            escalated=escalated,
            escalation_reason=escalation_reason or "Not specified"
        )

    def parse_response(self, response: Dict[str, Any]) -> EvaluationResult:
        """Parse escalation validation response"""
        try:
            data = {
                'escalation_appropriate': response.get('escalation_appropriate', False),
                'should_have_escalated': response.get('should_have_escalated', False),
                'reason': response.get('reason', ''),
                'alternative_action': response.get('alternative_action', '')
            }

            return EvaluationResult(success=True, data=data)

        except Exception as e:
            self.logger.error(f"Failed to parse escalation validation response: {e}")
            return EvaluationResult(success=False, data={}, error=str(e))
