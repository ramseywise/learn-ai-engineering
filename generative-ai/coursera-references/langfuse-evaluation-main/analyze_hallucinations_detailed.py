#!/usr/bin/env python3
"""
Deep Hallucination Analysis - Find patterns and root causes

This script:
1. Evaluates sample conversations
2. Identifies ALL cases with hallucinations (including minor)
3. Analyzes correlations with document length, question quality, etc.
4. Shows detailed examples for manual validation
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Import evaluation system
from src.data.loader import load_all_data
from src.etl.json_extractor import extract_langfuse_data
from src.etl.merger import merge_conversations, enrich_with_documents, create_conversation_summary
from src.models import ConversationData
from src.orchestrator import EvaluationOrchestrator
from src.config import EvaluatorConfig

def calculate_text_metrics(text: str) -> Dict[str, Any]:
    """Calculate various metrics about text quality and complexity"""
    if not text or pd.isna(text):
        return {
            'length': 0,
            'word_count': 0,
            'avg_word_length': 0,
            'sentence_count': 0,
            'has_question_mark': False,
            'is_vague': True
        }

    words = text.split()
    sentences = text.split('.')

    return {
        'length': len(text),
        'word_count': len(words),
        'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
        'sentence_count': len([s for s in sentences if s.strip()]),
        'has_question_mark': '?' in text,
        'is_vague': len(words) < 5  # Very short questions tend to be vague
    }

def analyze_hallucination_patterns(
    conversations: List[ConversationData],
    results: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Analyze patterns in hallucinations vs clean responses
    Returns DataFrame with detailed metrics and correlations
    """

    analysis_rows = []

    for conv, result in zip(conversations, results):
        if not result.get('success'):
            continue

        hall = result.get('hallucination', {})
        doc_rel = result.get('document_relevance', {})
        comp = result.get('completeness', {})

        # Question metrics
        q_metrics = calculate_text_metrics(conv.user_question)

        # Response metrics
        r_metrics = calculate_text_metrics(conv.ai_response)

        # Document metrics
        total_doc_length = sum(len(str(d)) for d in conv.documents) if conv.documents else 0
        doc_count = len(conv.documents) if conv.documents else 0
        avg_doc_length = total_doc_length / doc_count if doc_count > 0 else 0

        # Hallucination info
        has_hallucination = hall.get('hallucination_detected', False)
        severity = hall.get('severity', 'none')
        grounding_ratio = hall.get('grounding_ratio', 1.0)

        row = {
            # Identifiers
            'session_id': conv.session_id,

            # Hallucination status
            'has_hallucination': has_hallucination,
            'severity': severity,
            'grounding_ratio': grounding_ratio,
            'hallucination_type': hall.get('hallucination_type', 'none'),

            # Question characteristics
            'q_length': q_metrics['length'],
            'q_word_count': q_metrics['word_count'],
            'q_is_vague': q_metrics['is_vague'],
            'q_has_question_mark': q_metrics['has_question_mark'],

            # Response characteristics
            'r_length': r_metrics['length'],
            'r_word_count': r_metrics['word_count'],

            # Document characteristics
            'doc_count': doc_count,
            'total_doc_length': total_doc_length,
            'avg_doc_length': avg_doc_length,
            'doc_has_answer': doc_rel.get('has_answer', False),
            'doc_relevance_score': doc_rel.get('relevance_score', 0),

            # Other factors
            'unnecessary_clarification': comp.get('unnecessary_clarification', False),
            'completeness_score': comp.get('completeness_score', 0),

            # For detailed examination
            'user_question': conv.user_question,
            'ai_response': conv.ai_response,
            'evidence': hall.get('evidence', []),
            'reasoning': hall.get('reasoning', ''),
        }

        analysis_rows.append(row)

    return pd.DataFrame(analysis_rows)

def print_correlation_analysis(df: pd.DataFrame):
    """Print correlation analysis between hallucinations and various factors"""

    print("\n" + "="*100)
    print("CORRELATION ANALYSIS: What Causes Hallucinations?")
    print("="*100)
    print()

    # Split into hallucination vs clean
    hall_df = df[df['has_hallucination'] == True]
    clean_df = df[df['has_hallucination'] == False]

    if len(hall_df) == 0:
        print("✅ No hallucinations detected in sample!")
        return

    print(f"📊 Sample Size:")
    print(f"   Total conversations: {len(df)}")
    print(f"   With hallucinations: {len(hall_df)} ({len(hall_df)/len(df)*100:.1f}%)")
    print(f"   Clean responses: {len(clean_df)} ({len(clean_df)/len(df)*100:.1f}%)")
    print()

    # Severity breakdown
    print(f"🔍 Hallucination Severity:")
    severity_counts = hall_df['severity'].value_counts()
    for severity, count in severity_counts.items():
        print(f"   {severity.upper()}: {count} cases")
    print()

    # Factor comparison
    factors = [
        ('Document Length', 'avg_doc_length'),
        ('Number of Documents', 'doc_count'),
        ('Question Length', 'q_length'),
        ('Response Length', 'r_length'),
        ('Document Relevance Score', 'doc_relevance_score'),
        ('Completeness Score', 'completeness_score'),
    ]

    print("📈 FACTOR COMPARISON (Hallucination vs Clean):")
    print()

    for label, col in factors:
        if col not in df.columns:
            continue

        hall_avg = hall_df[col].mean() if len(hall_df) > 0 else 0
        clean_avg = clean_df[col].mean() if len(clean_df) > 0 else 0

        if clean_avg > 0:
            diff_pct = ((hall_avg - clean_avg) / clean_avg) * 100
        else:
            diff_pct = 0

        indicator = "🔴" if abs(diff_pct) > 20 else "🟡" if abs(diff_pct) > 10 else "✅"

        print(f"{indicator} {label}:")
        print(f"   Hallucination cases: {hall_avg:.1f}")
        print(f"   Clean cases: {clean_avg:.1f}")
        print(f"   Difference: {diff_pct:+.1f}%")
        print()

    # Boolean factor comparison
    bool_factors = [
        ('Vague Question', 'q_is_vague'),
        ('Documents Have Answer', 'doc_has_answer'),
        ('Unnecessary Clarification', 'unnecessary_clarification'),
    ]

    print("🔍 BOOLEAN FACTOR ANALYSIS:")
    print()

    for label, col in bool_factors:
        if col not in df.columns:
            continue

        hall_pct = (hall_df[col].sum() / len(hall_df) * 100) if len(hall_df) > 0 else 0
        clean_pct = (clean_df[col].sum() / len(clean_df) * 100) if len(clean_df) > 0 else 0

        diff = hall_pct - clean_pct
        indicator = "🔴" if abs(diff) > 20 else "🟡" if abs(diff) > 10 else "✅"

        print(f"{indicator} {label}:")
        print(f"   In hallucination cases: {hall_pct:.1f}%")
        print(f"   In clean cases: {clean_pct:.1f}%")
        print(f"   Difference: {diff:+.1f} percentage points")
        print()

def display_hallucination_example(
    row: pd.Series,
    example_num: int,
    total: int
):
    """Display a detailed hallucination example for manual validation"""

    print("\n" + "="*100)
    print(f"HALLUCINATION EXAMPLE {example_num}/{total}")
    print(f"Severity: {row['severity'].upper()} | Grounding: {row['grounding_ratio']*100:.0f}%")
    print("="*100)
    print()

    # Context metrics
    print("📊 CONTEXT METRICS:")
    print(f"   Documents provided: {row['doc_count']}")
    print(f"   Total document length: {row['total_doc_length']:,} chars")
    print(f"   Document relevance: {row['doc_relevance_score']}/5")
    print(f"   Documents have answer: {'✅ Yes' if row['doc_has_answer'] else '❌ No'}")
    print(f"   Question length: {row['q_word_count']} words")
    print(f"   Response length: {row['r_word_count']} words")
    print()

    # User question
    print("❓ USER QUESTION:")
    print("─" * 100)
    print(row['user_question'])
    print()

    # Conecta's response
    print("🤖 CONECTA'S RESPONSE:")
    print("─" * 100)
    print(row['ai_response'])
    print()

    # Hallucination details
    print(f"🚨 HALLUCINATION DETECTED ({row['severity'].upper()}):")
    print("─" * 100)
    print()

    print(f"📊 Grounding Ratio: {row['grounding_ratio']*100:.0f}% of claims supported")
    print(f"🏷️  Type: {row['hallucination_type']}")
    print()

    if row['reasoning']:
        print("💭 AI EVALUATOR'S REASONING:")
        print(row['reasoning'])
        print()

    # Evidence
    if row['evidence'] and len(row['evidence']) > 0:
        print("🔍 SPECIFIC HALLUCINATED CLAIMS:")
        print()

        for i, ev in enumerate(row['evidence'], 1):
            if isinstance(ev, dict):
                claim = ev.get('claim', 'Unknown claim')
                explanation = ev.get('explanation', 'No explanation')

                print(f"   Claim #{i}:")
                print(f"   📌 Statement: \"{claim}\"")
                print(f"   💡 Issue: {explanation}")
                print()
            elif isinstance(ev, str):
                print(f"   • {ev}")
                print()

    print("─" * 100)
    print("❓ VALIDATION QUESTION: Is this actually a hallucination, or is the evaluator being too strict?")
    print("─" * 100)
    print()

def main():
    print("="*100)
    print("DEEP HALLUCINATION ANALYSIS")
    print("="*100)
    print()
    print("This analysis will help you understand:")
    print("  1. What causes Conecta to hallucinate")
    print("  2. Patterns in hallucination cases")
    print("  3. Whether the AI evaluator is accurate or too strict")
    print()

    # Configuration
    config = EvaluatorConfig()
    config.flash_model_name = "gemini-2.0-flash-exp"
    config.validate()

    # Load data
    print("📂 Loading data...")
    data_files = load_all_data()
    conversations_df = data_files['conversations']
    langfuse_df = data_files['langfuse']
    kb_df = data_files['knowledge_base']

    print(f"   ✅ Loaded {len(conversations_df):,} conversations")
    print(f"   ✅ Loaded {len(langfuse_df):,} Langfuse traces")
    print(f"   ✅ Loaded {len(kb_df):,} knowledge base documents")
    print()

    # ETL Pipeline
    print("🔄 Running ETL pipeline...")
    langfuse_analysis = extract_langfuse_data(langfuse_df)
    merged_df = merge_conversations(conversations_df, langfuse_analysis)
    enriched_df = enrich_with_documents(merged_df, kb_df)
    conversation_df = create_conversation_summary(enriched_df)

    print(f"   ✅ Created {len(conversation_df):,} conversation summaries")
    print()

    # Sample selection - get diverse sample
    sample_size = min(50, len(conversation_df))  # Larger sample for pattern detection

    print(f"📊 Selecting {sample_size} conversations for analysis...")
    print("   (Diverse sample across conversation types)")
    print()

    # Try to get diverse sample
    sample_indices = np.linspace(0, len(conversation_df)-1, sample_size, dtype=int)
    sample_df = conversation_df.iloc[sample_indices].copy()

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

    # Evaluate
    print("🤖 Evaluating conversations with AI evaluators...")
    print(f"   Sample size: {len(conversations)}")
    print(f"   Estimated time: ~{len(conversations) * 3} seconds")
    print(f"   Estimated cost: ~${len(conversations) * 0.001:.3f}")
    print()

    orchestrator = EvaluationOrchestrator(config)
    results = []

    for i, conv in enumerate(conversations, 1):
        print(f"   [{i}/{len(conversations)}] {conv.session_id[:30]}... ", end="", flush=True)

        try:
            result = orchestrator.evaluate_conversation(conv, run_verification=True)
            results.append(result.to_dict())
            print("✅")
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            continue

    print()
    print(f"✅ Completed {len(results)} evaluations")
    print()

    # Analyze patterns
    print("📊 Analyzing hallucination patterns...")
    analysis_df = analyze_hallucination_patterns(conversations, results)

    # Print correlation analysis
    print_correlation_analysis(analysis_df)

    # Show detailed examples
    hallucination_cases = analysis_df[analysis_df['has_hallucination'] == True].copy()

    if len(hallucination_cases) > 0:
        print("\n" + "="*100)
        print("DETAILED HALLUCINATION EXAMPLES")
        print("="*100)
        print()
        print(f"Found {len(hallucination_cases)} cases with hallucinations")
        print("Showing up to 10 examples for manual validation...")
        print()

        # Sort by severity (critical > major > minor)
        severity_order = {'critical': 0, 'major': 1, 'minor': 2, 'none': 3}
        hallucination_cases['severity_rank'] = hallucination_cases['severity'].map(severity_order)
        hallucination_cases = hallucination_cases.sort_values('severity_rank')

        # Show up to 10 examples
        examples_to_show = min(10, len(hallucination_cases))

        for i, (idx, row) in enumerate(hallucination_cases.head(examples_to_show).iterrows(), 1):
            display_hallucination_example(row, i, examples_to_show)

            if i < examples_to_show:
                input("Press Enter to see next example...")

        # Summary statistics by severity
        print("\n" + "="*100)
        print("HALLUCINATION SUMMARY BY SEVERITY")
        print("="*100)
        print()

        for severity in ['critical', 'major', 'minor']:
            sev_cases = hallucination_cases[hallucination_cases['severity'] == severity]

            if len(sev_cases) > 0:
                print(f"{severity.upper()}: {len(sev_cases)} cases")
                print(f"  Avg document length: {sev_cases['avg_doc_length'].mean():,.0f} chars")
                print(f"  Avg documents provided: {sev_cases['doc_count'].mean():.1f}")
                print(f"  Avg grounding ratio: {sev_cases['grounding_ratio'].mean()*100:.0f}%")
                print(f"  Documents had answer: {sev_cases['doc_has_answer'].sum()}/{len(sev_cases)}")
                print()

        # Save detailed results
        output_file = "hallucination_analysis_detailed.csv"
        analysis_df.to_csv(output_file, index=False)
        print(f"💾 Saved detailed analysis to: {output_file}")
        print()

    else:
        print("\n✅ No hallucinations detected in this sample!")
        print("   Either Conecta is performing very well, or the sample size is too small.")
        print("   Try increasing sample_size or running on more conversations.")
        print()

    print("="*100)
    print("ANALYSIS COMPLETE")
    print("="*100)

if __name__ == "__main__":
    main()
