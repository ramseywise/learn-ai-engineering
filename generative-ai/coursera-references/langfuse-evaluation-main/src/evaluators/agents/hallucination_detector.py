"""
Hallucination Detector Agent - CRITICAL
This is the most important agent for detecting when Conecta makes up information
"""
import logging
from typing import Dict, Any, List

from ..base import BaseAgent, BaseLLMProvider, EvaluationResult
from ...utils.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class HallucinationDetector(BaseAgent):
    """
    Agent specialized in detecting hallucinations in AI responses

    This agent is CRITICAL because hallucinations can lead to:
    - Incorrect information given to customers
    - Compliance violations
    - Financial losses
    - Reputation damage
    """

    def __init__(self, llm_provider: BaseLLMProvider, prompt_version: str = "v1"):
        super().__init__(llm_provider, "HallucinationDetector")
        self.prompt_version = prompt_version

    def get_prompt(
        self,
        user_question: str,
        ai_response: str,
        documents: str,
        **kwargs
    ) -> str:
        """
        Get the hallucination detection prompt

        Args:
            user_question: User's original question
            ai_response: Conecta's response
            documents: All documents used (concatenated)
            **kwargs: Additional context (prev_user_question, prev_ai_response)

        Returns:
            Formatted prompt
        """
        template = PromptTemplates.hallucination_detector(version=self.prompt_version)

        # Build conversation history context
        conversation_history = ""
        prev_user = kwargs.get('prev_user_question')
        prev_ai = kwargs.get('prev_ai_response')

        if prev_user and prev_ai:
            conversation_history = f"""
**PREVIOUS TURN (for context):**
User: {prev_user}
Conecta: {prev_ai}
"""

        return template.format(
            conversation_history=conversation_history,
            user_question=user_question,
            ai_response=ai_response,
            documents=documents
        )

    def parse_response(self, response: Dict[str, Any]) -> EvaluationResult:
        """
        Parse hallucination detection response

        Args:
            response: Raw JSON response from LLM

        Returns:
            Structured evaluation result
        """
        try:
            # Extract key fields
            hallucination_detected = response.get('hallucination_detected', False)
            severity = response.get('severity', 'none')
            hallucination_type = response.get('hallucination_type', 'none')
            evidence = response.get('evidence', [])
            overall_assessment = response.get('overall_assessment', '')
            confidence = float(response.get('confidence', 0.0))

            # Count grounded vs hallucinated claims
            grounded_claims = [e for e in evidence if e.get('status') == 'grounded']
            hallucinated_claims = [e for e in evidence if e.get('status') == 'hallucination']

            # Calculate metrics
            total_claims = len(evidence)
            grounded_count = len(grounded_claims)
            hallucinated_count = len(hallucinated_claims)

            grounding_ratio = grounded_count / total_claims if total_claims > 0 else 0.0

            # VALIDATION: Override LLM's hallucination_detected if evidence contradicts it
            # The LLM sometimes returns inconsistent JSON (hallucination_detected=true but 0 hallucinated claims)
            if hallucinated_count == 0:
                # No hallucinated claims found -> override to False
                hallucination_detected = False
                severity = 'none'
                hallucination_type = 'none'
            elif hallucinated_count > 0 and not hallucination_detected:
                # Found hallucinations but LLM said false -> override to True
                hallucination_detected = True
                # Keep the severity/type from LLM if they make sense, otherwise set default
                if severity == 'none':
                    severity = 'minor'  # Default to minor if not specified
                if hallucination_type == 'none':
                    hallucination_type = 'fabrication'  # Default type

            # Determine severity score (for aggregation)
            severity_scores = {
                'none': 0,
                'minor': 1,
                'major': 2,
                'critical': 3
            }
            severity_score = severity_scores.get(severity, 0)

            # Build result data
            data = {
                'hallucination_detected': hallucination_detected,
                'severity': severity,
                'severity_score': severity_score,
                'hallucination_type': hallucination_type,
                'total_claims': total_claims,
                'grounded_claims': grounded_count,
                'hallucinated_claims': hallucinated_count,
                'grounding_ratio': grounding_ratio,
                'confidence': confidence,
                'overall_assessment': overall_assessment,
                'evidence': evidence,
                'hallucinated_claim_details': hallucinated_claims,
                'grounded_claim_details': grounded_claims
            }

            # Log critical findings
            if hallucination_detected and severity in ['major', 'critical']:
                self.logger.warning(
                    f"🚨 {severity.upper()} hallucination detected! "
                    f"Type: {hallucination_type}, "
                    f"Claims: {hallucinated_count}/{total_claims}"
                )

            return EvaluationResult(
                success=True,
                data=data
            )

        except Exception as e:
            self.logger.error(f"Failed to parse hallucination detector response: {e}")
            return EvaluationResult(
                success=False,
                data={},
                error=str(e)
            )

    def needs_verification(self, result: EvaluationResult) -> bool:
        """
        Determine if this result needs secondary verification

        Args:
            result: Hallucination detection result

        Returns:
            True if verification needed
        """
        if not result.success:
            return False

        # Verify all detected hallucinations (even minor ones)
        return result.data.get('hallucination_detected', False)
