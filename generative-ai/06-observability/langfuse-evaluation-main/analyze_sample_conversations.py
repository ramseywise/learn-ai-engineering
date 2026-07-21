#!/usr/bin/env python3
"""
Analyze 10 Sample Conversations - Detailed Evaluation Examples

This script runs the multi-agent evaluation system on 10 conversations
and displays detailed results to help you understand how the AI evaluators work.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.config import EvaluatorConfig, ProviderType, ModelType
from src.data.loader import load_all_data
from src.etl.merger import merge_all_datasets, enrich_with_documents, create_conversation_summary
from src.orchestrator import EvaluationOrchestrator, ConversationData
from src.utils.analysis_helpers import (
    display_conversation_detail,
    create_evaluation_summary_table,
    analyze_evaluation_quality,
    print_quality_report,
    print_section_header
)
from src.utils.env_loader import load_environment, validate_environment

import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(levelname)s - %(message)s'
)

def main():
    print("=" * 100)
    print(" 🔍 CONECTA EVALUATION SYSTEM - SAMPLE ANALYSIS")
    print(" Analyzing 10 conversations to understand AI evaluator performance")
    print("=" * 100)
    print()

    # Load environment
    print("📋 Step 1: Loading environment...")
    load_environment()

    if not validate_environment():
        print("\n❌ Environment not configured. Please set up your .env file.")
        return

    print("✅ Environment loaded")
    print()

    # Configure
    print("📋 Step 2: Configuring evaluation system...")
    config = EvaluatorConfig(
        provider=ProviderType.GEMINI,
        gemini_api_key=os.getenv('GEMINI_API_KEY'),
        hallucination_detector_model=ModelType.PRO,
        verification_agent_model=ModelType.PRO,
        parallel_agents=True
    )

    print(f"✅ Using {config.provider.value}")
    print(f"   Hallucination Detector: {config.get_model_name(config.hallucination_detector_model)}")
    print()

    # Load data
    print("📋 Step 3: Loading and processing data...")
    data = load_all_data(data_dir=".")

    # Merge datasets
    analysis_df = merge_all_datasets(data)
    print(f"✅ Loaded {len(analysis_df)} Langfuse traces")

    # Enrich with documents
    enriched_df = enrich_with_documents(analysis_df, data['knowledge_base'])
    print(f"✅ Enriched with document content")

    # Create conversation summary
    conversation_df = create_conversation_summary(enriched_df)
    print(f"✅ Created {len(conversation_df)} conversation summaries")
    print()

    # Select 10 sample conversations
    # Try to get a diverse sample
    sample_size = min(10, len(conversation_df))
    sample_df = conversation_df.head(sample_size).copy()

    print(f"📋 Step 4: Analyzing {sample_size} sample conversations...")
    print(f"💰 Estimated cost: ~${sample_size * 0.0037:.2f}")
    print()

    # Initialize orchestrator
    orchestrator = EvaluationOrchestrator(config)

    # Prepare conversations
    conversations = []
    for idx, row in sample_df.iterrows():
        conv = ConversationData(
            session_id=row['sessionId'],
            user_question=row['user_question'],
            ai_response=row['ai_response'],
            documents=row['all_documents'],
            escalated=row.get('need_expert', False)
        )
        conversations.append(conv)

    # Evaluate conversations
    print("🤖 Running AI evaluations...")
    print("   This will take 2-3 minutes...")
    print()

    results = []
    for i, conv in enumerate(conversations, 1):
        print(f"   Evaluating conversation {i}/{len(conversations)}... ", end="", flush=True)

        try:
            result = orchestrator.evaluate_conversation(conv, run_verification=True)
            results.append(result)
            print("✅")
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    print()
    print(f"✅ Completed {len(results)} evaluations")
    print()

    # Convert results
    results_dicts = [r.to_dict() for r in results]

    # Display summary table
    print_section_header("QUICK SUMMARY TABLE", "=")
    summary_table = create_evaluation_summary_table(results_dicts)
    print(summary_table.to_string(index=False))
    print()

    # Quality report
    quality_metrics = analyze_evaluation_quality(results_dicts)
    print_quality_report(quality_metrics)

    # Ask user which conversations to examine in detail
    print_section_header("DETAILED EXAMINATION", "=")
    print()
    print("Now let's examine individual conversations in detail.")
    print("This will show you exactly what the AI evaluators detected.")
    print()

    # Display detailed analysis for each conversation
    for i, (conv_data, result_dict) in enumerate(zip(sample_df.to_dict('records'), results_dicts), 1):
        print(f"\n{'=' * 100}")
        print(f" CONVERSATION {i}/{len(results)}")
        print(f"{'=' * 100}")

        # Check if this is interesting (has hallucination or issues)
        is_interesting = False
        if result_dict.get('success'):
            hall = result_dict.get('hallucination', {})
            comp = result_dict.get('completeness', {})

            is_interesting = (
                hall.get('hallucination_detected', False) or
                comp.get('unnecessary_clarification', False) or
                hall.get('grounding_ratio', 1.0) < 0.8
            )

        # Mark interesting cases
        if is_interesting:
            print("⚠️  INTERESTING CASE - Issues detected!")

        display_conversation_detail(
            conversation_data=conv_data,
            evaluation_result=result_dict,
            show_documents=False,  # Don't show full docs by default
            show_evidence=True  # Show hallucination evidence
        )

        # Pause between conversations for readability
        if i < len(results):
            input("\n>>> Press Enter to see next conversation... ")

    # Final summary
    print_section_header("ANALYSIS COMPLETE", "=")
    print()
    print("📊 Summary:")
    print(f"   Evaluated: {len(results)} conversations")
    print(f"   Hallucinations detected: {sum(1 for r in results_dicts if r.get('hallucination', {}).get('hallucination_detected', False))}")
    print(f"   Unnecessary clarifications: {sum(1 for r in results_dicts if r.get('completeness', {}).get('unnecessary_clarification', False))}")
    print()
    print("💡 Next steps:")
    print("   1. Review the evaluations above")
    print("   2. Adjust evaluation prompts if needed (src/utils/prompt_templates.py)")
    print("   3. Run full analysis in Jupyter notebook")
    print()
    print("📓 For full analysis, run:")
    print("   jupyter notebook notebooks/conecta_hallucination_analysis.ipynb")
    print()


if __name__ == "__main__":
    main()
