"""
Orchestrator for coordinating multiple evaluation agents
"""
import logging
import concurrent.futures
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from .config import EvaluatorConfig
from .evaluators.factory import ProviderFactory
from .evaluators.agents.hallucination_detector import HallucinationDetector
from .evaluators.agents.document_relevance import DocumentRelevanceAgent
from .evaluators.agents.completeness_checker import CompletenessChecker
from .evaluators.agents.escalation_validator import EscalationValidator
from .evaluators.agents.verification_agent import VerificationAgent

logger = logging.getLogger(__name__)


@dataclass
class ConversationData:
    """Input data for conversation evaluation"""
    session_id: str
    user_question: str
    ai_response: str
    documents: str
    escalated: bool = False
    escalation_reason: Optional[str] = None
    # Conversation history for context
    prev_user_question: Optional[str] = None
    prev_ai_response: Optional[str] = None
    turn_number: int = 1
    total_turns: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResults:
    """Complete evaluation results for one conversation"""
    session_id: str
    success: bool
    hallucination: Optional[Dict[str, Any]] = None
    document_relevance: Optional[Dict[str, Any]] = None
    completeness: Optional[Dict[str, Any]] = None
    escalation: Optional[Dict[str, Any]] = None
    verification: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to flat dictionary for DataFrame"""
        result = {
            'session_id': self.session_id,
            'success': self.success,
            'error': self.error
        }

        # Add hallucination data with prefix
        if self.hallucination:
            for key, value in self.hallucination.items():
                result[f'hall_{key}'] = value

        # Add document relevance with prefix
        if self.document_relevance:
            for key, value in self.document_relevance.items():
                result[f'doc_{key}'] = value

        # Add completeness with prefix
        if self.completeness:
            for key, value in self.completeness.items():
                result[f'comp_{key}'] = value

        # Add escalation with prefix
        if self.escalation:
            for key, value in self.escalation.items():
                result[f'esc_{key}'] = value

        # Add verification with prefix
        if self.verification:
            for key, value in self.verification.items():
                result[f'ver_{key}'] = value

        return result


class EvaluationOrchestrator:
    """
    Orchestrates multiple AI agents to evaluate conversations

    Architecture:
    - Stage 1: Run independent agents in parallel (optional)
    - Stage 2: Run verification for critical findings
    """

    def __init__(self, config: EvaluatorConfig):
        """
        Initialize orchestrator with configuration

        Args:
            config: Evaluator configuration
        """
        self.config = config
        config.validate()

        logger.info("Initializing EvaluationOrchestrator...")

        # Create providers for all agents
        providers = ProviderFactory.create_all_providers(config)

        # Initialize agents
        self.agents = {
            'hallucination': HallucinationDetector(
                providers['hallucination_detector'],
                prompt_version=config.prompt_version
            ),
            'document_relevance': DocumentRelevanceAgent(providers['document_relevance']),
            'completeness': CompletenessChecker(providers['completeness_checker']),
            'escalation': EscalationValidator(providers['escalation_validator']),
            'verification': VerificationAgent(providers['verification_agent'])
        }

        logger.info(f"Initialized {len(self.agents)} evaluation agents")

    def evaluate_conversation(
        self,
        conversation: ConversationData,
        run_verification: bool = True
    ) -> EvaluationResults:
        """
        Evaluate a single conversation using all agents

        Args:
            conversation: Conversation data to evaluate
            run_verification: Whether to run verification for critical findings

        Returns:
            Complete evaluation results
        """
        logger.info(f"Evaluating conversation: {conversation.session_id}")

        results = EvaluationResults(
            session_id=conversation.session_id,
            success=False
        )

        try:
            # Prepare common evaluation kwargs
            eval_kwargs = {
                'user_question': conversation.user_question,
                'ai_response': conversation.ai_response,
                'documents': conversation.documents,
                # Add conversation history for context
                'prev_user_question': conversation.prev_user_question,
                'prev_ai_response': conversation.prev_ai_response
            }

            # Stage 1: Run core agents
            if self.config.parallel_agents:
                # Run independent agents in parallel
                results = self._run_parallel_evaluation(conversation, eval_kwargs)
            else:
                # Run sequentially
                results = self._run_sequential_evaluation(conversation, eval_kwargs)

            # Stage 2: Verification (if needed and requested)
            if run_verification and results.hallucination:
                hall_detected = results.hallucination.get('hallucination_detected', False)
                if hall_detected:
                    logger.info("Running verification for detected hallucination...")
                    verification_result = self.agents['verification'].verify_hallucination(
                        hallucination_result=type('obj', (object,), {'data': results.hallucination}),
                        user_question=conversation.user_question,
                        ai_response=conversation.ai_response,
                        documents=conversation.documents
                    )

                    if verification_result.success:
                        results.verification = verification_result.data

            results.success = True
            logger.info(f"✅ Evaluation completed for {conversation.session_id}")

        except Exception as e:
            logger.error(f"❌ Evaluation failed for {conversation.session_id}: {e}")
            results.error = str(e)

        return results

    def _run_parallel_evaluation(
        self,
        conversation: ConversationData,
        eval_kwargs: Dict[str, Any]
    ) -> EvaluationResults:
        """Run agents in parallel"""
        results = EvaluationResults(
            session_id=conversation.session_id,
            success=False
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all independent tasks
            futures = {
                'hallucination': executor.submit(
                    self.agents['hallucination'].evaluate, **eval_kwargs
                ),
                'document_relevance': executor.submit(
                    self.agents['document_relevance'].evaluate,
                    user_question=eval_kwargs['user_question'],
                    documents=eval_kwargs['documents']
                ),
                'completeness': executor.submit(
                    self.agents['completeness'].evaluate, **eval_kwargs
                ),
                'escalation': executor.submit(
                    self.agents['escalation'].evaluate,
                    **eval_kwargs,
                    escalated=conversation.escalated,
                    escalation_reason=conversation.escalation_reason
                )
            }

            # Collect results
            for agent_name, future in futures.items():
                try:
                    result = future.result(timeout=120)  # 2 minute timeout
                    if result.success:
                        setattr(results, agent_name, result.data)
                    else:
                        logger.warning(f"{agent_name} agent failed: {result.error}")
                except Exception as e:
                    logger.error(f"{agent_name} agent raised exception: {e}")

        return results

    def _run_sequential_evaluation(
        self,
        conversation: ConversationData,
        eval_kwargs: Dict[str, Any]
    ) -> EvaluationResults:
        """Run agents sequentially"""
        results = EvaluationResults(
            session_id=conversation.session_id,
            success=False
        )

        # 1. Hallucination detection (priority)
        hall_result = self.agents['hallucination'].evaluate(**eval_kwargs)
        if hall_result.success:
            results.hallucination = hall_result.data

        # 2. Document relevance
        doc_result = self.agents['document_relevance'].evaluate(
            user_question=eval_kwargs['user_question'],
            documents=eval_kwargs['documents']
        )
        if doc_result.success:
            results.document_relevance = doc_result.data

        # 3. Completeness
        comp_result = self.agents['completeness'].evaluate(**eval_kwargs)
        if comp_result.success:
            results.completeness = comp_result.data

        # 4. Escalation validation
        esc_result = self.agents['escalation'].evaluate(
            **eval_kwargs,
            escalated=conversation.escalated,
            escalation_reason=conversation.escalation_reason
        )
        if esc_result.success:
            results.escalation = esc_result.data

        return results

    def evaluate_batch(
        self,
        conversations: list[ConversationData],
        run_verification: bool = True,
        max_workers: int = 3
    ) -> list[EvaluationResults]:
        """
        Evaluate multiple conversations in parallel

        Args:
            conversations: List of conversations to evaluate
            run_verification: Whether to run verification
            max_workers: Maximum parallel workers

        Returns:
            List of evaluation results
        """
        logger.info(f"Starting batch evaluation of {len(conversations)} conversations...")

        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.evaluate_conversation,
                    conv,
                    run_verification
                ): conv for conv in conversations
            }

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    result = future.result()
                    results.append(result)

                    if (i + 1) % 10 == 0:
                        logger.info(f"Progress: {i + 1}/{len(conversations)} completed")

                except Exception as e:
                    conv = futures[future]
                    logger.error(f"Failed to evaluate {conv.session_id}: {e}")
                    results.append(EvaluationResults(
                        session_id=conv.session_id,
                        success=False,
                        error=str(e)
                    ))

        logger.info(f"✅ Batch evaluation completed: {len(results)} results")
        return results
