#!/usr/bin/env python3
"""
A/B Testing Script for Prompt Comparison
Tests v1 (lenient) vs v2 (strict) prompts on same conversation set
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.config import EvaluatorConfig, ProviderType
from src.orchestrator import EvaluationOrchestrator, ConversationData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_test_conversations(limit: int = 20) -> List[ConversationData]:
    """
    Load conversations for testing

    Args:
        limit: Number of conversations to test

    Returns:
        List of ConversationData objects
    """
    from src.etl.merger import load_all_data, merge_all_datasets, enrich_with_documents, create_conversation_summary

    logger.info(f"Loading {limit} test conversations...")

    # Load data
    data = load_all_data(data_dir=".")
    analysis_df = merge_all_datasets(data)
    enriched_df = enrich_with_documents(analysis_df, data['knowledge_base'])
    conversation_df = create_conversation_summary(enriched_df)

    # Sample conversations
    test_df = conversation_df.head(limit)

    conversations = []
    for _, row in test_df.iterrows():
        conv = ConversationData(
            session_id=row['sessionId'],
            user_question=row['user_question'],
            ai_response=row['ai_response'],
            documents=row.get('documents', ''),
            escalated=row.get('need_expert', False),
            escalation_reason=row.get('expert_category', None),
            prev_user_question=row.get('prev_user_question'),
            prev_ai_response=row.get('prev_ai_response'),
            turn_number=int(row.get('turn_number', 1)),
            total_turns=int(row.get('total_turns', 1))
        )
        conversations.append(conv)

    logger.info(f"Loaded {len(conversations)} conversations")
    return conversations


def run_ab_test(conversations: List[ConversationData]) -> Dict[str, Any]:
    """
    Run A/B test comparing v1 (lenient) vs v2 (strict) prompts

    Args:
        conversations: List of conversations to evaluate

    Returns:
        Dictionary with results from both versions
    """
    # Configure API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable must be set")

    results = {
        'v1_lenient': [],
        'v2_strict': [],
        'metadata': {
            'test_date': datetime.now().isoformat(),
            'conversation_count': len(conversations),
            'conversations_tested': [c.session_id for c in conversations]
        }
    }

    # Test V1 (Lenient)
    logger.info("=" * 80)
    logger.info("TESTING V1 (LENIENT PROMPT)")
    logger.info("=" * 80)

    config_v1 = EvaluatorConfig(
        provider=ProviderType.GEMINI,
        gemini_api_key=api_key,
        prompt_version="v1",
        parallel_agents=True
    )

    orchestrator_v1 = EvaluationOrchestrator(config_v1)

    for i, conv in enumerate(conversations, 1):
        logger.info(f"V1: Evaluating conversation {i}/{len(conversations)}: {conv.session_id}")
        try:
            result = orchestrator_v1.evaluate_conversation(conv, run_verification=False)
            results['v1_lenient'].append(result.to_dict())
            logger.info(f"V1: ✅ Completed {conv.session_id}")
        except Exception as e:
            logger.error(f"V1: ❌ Error on {conv.session_id}: {e}")
            results['v1_lenient'].append({
                'session_id': conv.session_id,
                'success': False,
                'error': str(e)
            })

    # Test V2 (Strict)
    logger.info("=" * 80)
    logger.info("TESTING V2 (STRICT PROMPT)")
    logger.info("=" * 80)

    config_v2 = EvaluatorConfig(
        provider=ProviderType.GEMINI,
        gemini_api_key=api_key,
        prompt_version="v2",
        parallel_agents=True
    )

    orchestrator_v2 = EvaluationOrchestrator(config_v2)

    for i, conv in enumerate(conversations, 1):
        logger.info(f"V2: Evaluating conversation {i}/{len(conversations)}: {conv.session_id}")
        try:
            result = orchestrator_v2.evaluate_conversation(conv, run_verification=False)
            results['v2_strict'].append(result.to_dict())
            logger.info(f"V2: ✅ Completed {conv.session_id}")
        except Exception as e:
            logger.error(f"V2: ❌ Error on {conv.session_id}: {e}")
            results['v2_strict'].append({
                'session_id': conv.session_id,
                'success': False,
                'error': str(e)
            })

    return results


def save_results(results: Dict[str, Any], output_dir: str = "./ab_test_results"):
    """
    Save A/B test results to files

    Args:
        results: Test results
        output_dir: Directory to save results
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save full results as JSON
    json_path = os.path.join(output_dir, f"ab_test_full_{timestamp}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved full results: {json_path}")

    # Save v1 results as CSV
    df_v1 = pd.DataFrame(results['v1_lenient'])
    csv_v1 = os.path.join(output_dir, f"ab_test_v1_lenient_{timestamp}.csv")
    df_v1.to_csv(csv_v1, index=False)
    logger.info(f"✅ Saved V1 results: {csv_v1}")

    # Save v2 results as CSV
    df_v2 = pd.DataFrame(results['v2_strict'])
    csv_v2 = os.path.join(output_dir, f"ab_test_v2_strict_{timestamp}.csv")
    df_v2.to_csv(csv_v2, index=False)
    logger.info(f"✅ Saved V2 results: {csv_v2}")

    return json_path, csv_v1, csv_v2


def print_summary(results: Dict[str, Any]):
    """
    Print comparison summary

    Args:
        results: Test results
    """
    df_v1 = pd.DataFrame(results['v1_lenient'])
    df_v2 = pd.DataFrame(results['v2_strict'])

    print("\n" + "=" * 80)
    print("A/B TEST SUMMARY")
    print("=" * 80)

    print(f"\nConversations tested: {results['metadata']['conversation_count']}")

    # V1 Summary
    print("\n📊 V1 (LENIENT PROMPT):")
    print(f"   Success rate: {df_v1['success'].mean()*100:.1f}%")
    if 'hall_hallucination_detected' in df_v1.columns:
        hall_rate_v1 = df_v1['hall_hallucination_detected'].sum() / len(df_v1) * 100
        print(f"   Hallucination rate: {hall_rate_v1:.1f}% ({df_v1['hall_hallucination_detected'].sum()}/{len(df_v1)})")

        # Severity breakdown
        if 'hall_severity' in df_v1.columns:
            severity_counts = df_v1['hall_severity'].value_counts()
            print(f"   Severity breakdown:")
            for severity, count in severity_counts.items():
                if severity != 'none':
                    print(f"      {severity}: {count}")

    # V2 Summary
    print("\n📊 V2 (STRICT PROMPT):")
    print(f"   Success rate: {df_v2['success'].mean()*100:.1f}%")
    if 'hall_hallucination_detected' in df_v2.columns:
        hall_rate_v2 = df_v2['hall_hallucination_detected'].sum() / len(df_v2) * 100
        print(f"   Hallucination rate: {hall_rate_v2:.1f}% ({df_v2['hall_hallucination_detected'].sum()}/{len(df_v2)})")

        # Severity breakdown
        if 'hall_severity' in df_v2.columns:
            severity_counts = df_v2['hall_severity'].value_counts()
            print(f"   Severity breakdown:")
            for severity, count in severity_counts.items():
                if severity != 'none':
                    print(f"      {severity}: {count}")

    # Comparison
    print("\n🔍 COMPARISON:")
    if 'hall_hallucination_detected' in df_v1.columns and 'hall_hallucination_detected' in df_v2.columns:
        diff = hall_rate_v2 - hall_rate_v1
        print(f"   Hallucination rate difference: {diff:+.1f}%")
        if diff > 10:
            print(f"   → V2 is SIGNIFICANTLY stricter (+{diff:.1f}%)")
        elif diff > 5:
            print(f"   → V2 is moderately stricter (+{diff:.1f}%)")
        elif abs(diff) <= 5:
            print(f"   → Similar strictness (±{abs(diff):.1f}%)")
        else:
            print(f"   → V2 is more lenient ({diff:.1f}%)")

    print("\n" + "=" * 80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="A/B test prompt versions")
    parser.add_argument('--limit', type=int, default=20, help="Number of conversations to test")
    parser.add_argument('--output-dir', default="./ab_test_results", help="Output directory")

    args = parser.parse_args()

    try:
        # Load conversations
        conversations = load_test_conversations(limit=args.limit)

        # Run A/B test
        results = run_ab_test(conversations)

        # Save results
        save_results(results, output_dir=args.output_dir)

        # Print summary
        print_summary(results)

        logger.info("✅ A/B test completed successfully")

    except Exception as e:
        logger.error(f"❌ A/B test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
