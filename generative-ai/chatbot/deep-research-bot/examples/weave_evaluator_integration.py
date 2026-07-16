"""Example: Adding Weave to your existing RAG evaluators.

This shows how to integrate Weave tracing and evaluation with your 
existing MCQ-based evaluation pipeline.
"""

import weave
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Option 1: Wrap your existing evaluators with @weave.op
# ---------------------------------------------------------------------------


class Evaluator(ABC):
    """Abstract base class for evaluating the correctness of generated answers."""

    @abstractmethod
    def evaluate(self, mcq: str, rag_answer: str) -> bool | dict:
        """Compare the RAG-generated answer to the correct MCQ answer."""
        pass


class DefaultEvaluator(Evaluator):
    """Evaluate the RAG answer by comparing it to the correct answer in the MCQ."""

    @weave.op  # <-- Just add this decorator to trace evaluations
    def evaluate(self, mcq: str, rag_answer: str) -> bool:
        """Extract the correct answer from the MCQ and compares it to the RAG result."""
        try:
            correct_line = next(
                line for line in mcq.splitlines() if "Richtige Antwort:" in line
            )
            correct = correct_line.split(":")[-1].strip().upper()
            actual = rag_answer.strip()[:1].upper()
            return actual == correct
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Option 2: Create a Weave Scorer that wraps your evaluator
# ---------------------------------------------------------------------------


class MCQScorer(weave.Scorer):
    """Weave Scorer that uses your existing MCQ evaluation logic."""

    name: str = "mcq_accuracy"

    @weave.op()
    def score(self, output: dict, mcq: str, expected_answer: str) -> dict:
        """
        Score the RAG output against the expected MCQ answer.

        Args:
            output: The model/agent output (from predict())
            mcq: The full MCQ question text (from dataset row)
            expected_answer: The correct answer letter (from dataset row)
        """
        rag_answer = output.get("answer", "")
        actual = rag_answer.strip()[:1].upper()
        is_correct = actual == expected_answer.upper()

        return {
            "is_correct": is_correct,
            "expected": expected_answer,
            "actual": actual,
        }


# ---------------------------------------------------------------------------
# Option 3: LLM-as-Judge Scorer (like your StructuredAnswerEvaluator)
# ---------------------------------------------------------------------------


class LLMJudgeOutput(BaseModel):
    """Structured output from LLM judge."""

    is_correct: bool = Field(description="Whether the answer is correct")
    score: float = Field(description="Score from 0.0 to 1.0")
    reasoning: str = Field(description="Explanation of the score")


class LLMJudgeScorer(weave.Scorer):
    """LLM-as-Judge scorer for more nuanced evaluation."""

    name: str = "llm_judge"
    judge_model: str = "anthropic.claude-3-5-sonnet"

    @weave.op()
    def score(self, output: dict, mcq: str, expected_answer: str) -> dict:
        """Use an LLM to judge the quality of the RAG answer."""
        import openai

        rag_answer = output.get("answer", "")

        # Call your LLM judge (this example uses OpenAI-compatible API)
        client = openai.OpenAI(base_url="your-api-gateway-url", api_key="your-api-key")

        response = client.chat.completions.create(
            model=self.judge_model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
Bewerte die RAG-Antwort im Vergleich zur Referenz-MCQ:
- Ist sie inhaltlich korrekt? -> is_correct = true/false
- Score = Gleitkommazahl von 0.0 bis 1.0
- Kurze Begründung

Reference MCQ:
{mcq}

RAG Answer:
{rag_answer}
""",
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "judge_output",
                    "schema": LLMJudgeOutput.model_json_schema(),
                },
            },
        )

        result = LLMJudgeOutput.model_validate_json(response.choices[0].message.content)

        return {
            "is_correct": result.is_correct,
            "score": result.score,
            "reasoning": result.reasoning,
        }


# ---------------------------------------------------------------------------
# Putting it all together: Run a Weave Evaluation
# ---------------------------------------------------------------------------


class RAGModel(weave.Model):
    """Wrap your RAG system as a Weave Model."""

    rag_system: any = None  # Your actual RAG system

    @weave.op()
    async def predict(self, question: str, **kwargs) -> dict:
        """Run your RAG system on the question."""
        # Call your existing RAG system here
        answer = self.rag_system.query(question)
        return {"answer": answer}


async def run_evaluation():
    """Run the full evaluation with Weave."""

    # Initialize Weave
    weave.init("your-wandb-entity/rag-evaluation")

    # Your 25 MCQ test cases
    dataset = [
        {
            "question": "Was ist die Hauptfunktion von X?",
            "mcq": "A) Option 1\nB) Option 2\nC) Option 3\nRichtige Antwort: B",
            "expected_answer": "B",
        },
        # ... more test cases
    ]

    # Your RAG model
    model = RAGModel(rag_system=your_rag_system)

    # Run evaluation with multiple scorers
    evaluation = weave.Evaluation(
        name="rag_mcq_eval_v1",
        dataset=dataset,
        scorers=[
            MCQScorer(),  # Simple accuracy
            LLMJudgeScorer(),  # LLM-as-judge for nuanced scoring
        ],
    )

    results = await evaluation.evaluate(model)
    return results


# ---------------------------------------------------------------------------
# Bonus: Using your ticket history data
# ---------------------------------------------------------------------------


def create_dataset_from_tickets(ticket_history: list[dict]) -> list[dict]:
    """
    Convert ticket history into evaluation dataset.

    Your ticket history could provide:
    - Real user questions
    - Agent responses that were marked as helpful/unhelpful
    - Resolution outcomes
    """
    dataset = []
    for ticket in ticket_history:
        dataset.append(
            {
                "question": ticket["user_question"],
                "expected_answer": ticket["resolved_answer"],  # or agent response
                "ticket_id": ticket["id"],
                "was_resolved": ticket.get("resolved", False),
                # Add any other metadata useful for evaluation
            }
        )
    return dataset


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_evaluation())
