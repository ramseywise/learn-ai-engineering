"""
Document Relevance Checker Agent
Evaluates if retrieved documents are relevant to the user's question
"""
import logging
from typing import Dict, Any

from ..base import BaseAgent, BaseLLMProvider, EvaluationResult
from ...utils.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class DocumentRelevanceAgent(BaseAgent):
    """Agent that checks if documents are relevant to answer the question"""

    def __init__(self, llm_provider: BaseLLMProvider):
        super().__init__(llm_provider, "DocumentRelevanceAgent")

    def get_prompt(
        self,
        user_question: str,
        documents: str,
        **kwargs
    ) -> str:
        """
        Get the document relevance prompt

        Args:
            user_question: User's question
            documents: Documents retrieved
            **kwargs: Additional context

        Returns:
            Formatted prompt
        """
        template = PromptTemplates.document_relevance()

        return template.format(
            user_question=user_question,
            documents=documents
        )

    def parse_response(self, response: Dict[str, Any]) -> EvaluationResult:
        """
        Parse document relevance response

        Args:
            response: Raw JSON response

        Returns:
            Structured result
        """
        try:
            data = {
                'relevance_score': int(response.get('relevance_score', 0)),
                'has_answer': response.get('has_answer', False),
                'missing_information': response.get('missing_information', []),
                'relevant_documents': response.get('relevant_documents', []),
                'irrelevant_documents': response.get('irrelevant_documents', []),
                'explanation': response.get('explanation', '')
            }

            return EvaluationResult(success=True, data=data)

        except Exception as e:
            self.logger.error(f"Failed to parse document relevance response: {e}")
            return EvaluationResult(success=False, data={}, error=str(e))
