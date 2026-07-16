"""
Visualization utilities for hallucination analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any

def create_comparison_table(analysis_df: pd.DataFrame) -> str:
    """
    Create a side-by-side comparison table of hallucination vs clean cases
    """

    hall_df = analysis_df[analysis_df['has_hallucination'] == True]
    clean_df = analysis_df[analysis_df['has_hallucination'] == False]

    if len(hall_df) == 0:
        return "No hallucinations detected in sample."

    metrics = {
        'Count': (len(hall_df), len(clean_df)),
        'Avg Doc Length': (hall_df['avg_doc_length'].mean(), clean_df['avg_doc_length'].mean()),
        'Avg # Docs': (hall_df['doc_count'].mean(), clean_df['doc_count'].mean()),
        'Avg Question Length': (hall_df['q_length'].mean(), clean_df['q_length'].mean()),
        'Avg Response Length': (hall_df['r_length'].mean(), clean_df['r_length'].mean()),
        'Avg Doc Relevance': (hall_df['doc_relevance_score'].mean(), clean_df['doc_relevance_score'].mean()),
        'Docs Have Answer %': (hall_df['doc_has_answer'].sum()/len(hall_df)*100, clean_df['doc_has_answer'].sum()/len(clean_df)*100),
        'Vague Question %': (hall_df['q_is_vague'].sum()/len(hall_df)*100, clean_df['q_is_vague'].sum()/len(clean_df)*100),
    }

    # Build table
    lines = []
    lines.append("="*100)
    lines.append(f"{'METRIC':<30} | {'HALLUCINATION CASES':>20} | {'CLEAN CASES':>20} | {'DIFFERENCE':>15}")
    lines.append("="*100)

    for metric, (hall_val, clean_val) in metrics.items():
        if metric == 'Count':
            diff_str = f"{hall_val/(hall_val+clean_val)*100:.1f}%"
        elif clean_val > 0:
            diff_pct = ((hall_val - clean_val) / clean_val) * 100
            diff_str = f"{diff_pct:+.1f}%"
        else:
            diff_str = "N/A"

        # Format values
        if 'Length' in metric or 'Doc Relevance' in metric or '# Docs' in metric:
            hall_str = f"{hall_val:,.1f}"
            clean_str = f"{clean_val:,.1f}"
        elif '%' in metric:
            hall_str = f"{hall_val:.1f}%"
            clean_str = f"{clean_val:.1f}%"
        else:
            hall_str = f"{hall_val:.0f}"
            clean_str = f"{clean_val:.0f}"

        lines.append(f"{metric:<30} | {hall_str:>20} | {clean_str:>20} | {diff_str:>15}")

    lines.append("="*100)

    return "\n".join(lines)


def find_interesting_cases(analysis_df: pd.DataFrame, category: str = 'all') -> pd.DataFrame:
    """
    Find interesting hallucination cases based on category

    Categories:
    - 'all': All hallucinations
    - 'severe': Major/critical only
    - 'long_docs': Hallucinations with long documents
    - 'short_docs': Hallucinations with short documents
    - 'vague_questions': Hallucinations with vague questions
    - 'clear_questions': Hallucinations with clear questions
    - 'has_answer': Documents had the answer but still hallucinated
    - 'no_answer': Documents didn't have answer
    """

    hall_df = analysis_df[analysis_df['has_hallucination'] == True].copy()

    if len(hall_df) == 0:
        return pd.DataFrame()

    if category == 'all':
        return hall_df

    elif category == 'severe':
        return hall_df[hall_df['severity'].isin(['major', 'critical'])]

    elif category == 'long_docs':
        median_doc_length = analysis_df['avg_doc_length'].median()
        return hall_df[hall_df['avg_doc_length'] > median_doc_length]

    elif category == 'short_docs':
        median_doc_length = analysis_df['avg_doc_length'].median()
        return hall_df[hall_df['avg_doc_length'] <= median_doc_length]

    elif category == 'vague_questions':
        return hall_df[hall_df['q_is_vague'] == True]

    elif category == 'clear_questions':
        return hall_df[hall_df['q_is_vague'] == False]

    elif category == 'has_answer':
        return hall_df[hall_df['doc_has_answer'] == True]

    elif category == 'no_answer':
        return hall_df[hall_df['doc_has_answer'] == False]

    else:
        return hall_df


def print_case_comparison(row1: pd.Series, row2: pd.Series):
    """
    Print side-by-side comparison of two cases
    """

    print("\n" + "="*100)
    print("CASE COMPARISON")
    print("="*100)
    print()

    print(f"{'METRIC':<30} | {'CASE 1':>30} | {'CASE 2':>30}")
    print("-"*100)
    print(f"{'Hallucination':<30} | {str(row1['has_hallucination']):>30} | {str(row2['has_hallucination']):>30}")
    print(f"{'Severity':<30} | {row1['severity']:>30} | {row2['severity']:>30}")
    print(f"{'Grounding Ratio':<30} | {row1['grounding_ratio']*100:>29.0f}% | {row2['grounding_ratio']*100:>29.0f}%")
    print(f"{'Document Count':<30} | {row1['doc_count']:>30.0f} | {row2['doc_count']:>30.0f}")
    print(f"{'Avg Document Length':<30} | {row1['avg_doc_length']:>29,.0f} | {row2['avg_doc_length']:>29,.0f}")
    print(f"{'Question Length':<30} | {row1['q_length']:>30.0f} | {row2['q_length']:>30.0f}")
    print(f"{'Response Length':<30} | {row1['r_length']:>30.0f} | {row2['r_length']:>30.0f}")
    print(f"{'Doc Relevance Score':<30} | {row1['doc_relevance_score']:>30.0f} | {row2['doc_relevance_score']:>30.0f}")
    print()

    print("CASE 1 QUESTION:")
    print(row1['user_question'][:200] + "..." if len(row1['user_question']) > 200 else row1['user_question'])
    print()

    print("CASE 2 QUESTION:")
    print(row2['user_question'][:200] + "..." if len(row2['user_question']) > 200 else row2['user_question'])
    print()


def generate_hypothesis_tests(analysis_df: pd.DataFrame) -> List[str]:
    """
    Generate hypotheses about what causes hallucinations based on the data
    """

    hall_df = analysis_df[analysis_df['has_hallucination'] == True]
    clean_df = analysis_df[analysis_df['has_hallucination'] == False]

    if len(hall_df) == 0:
        return ["No hallucinations detected - cannot generate hypotheses."]

    hypotheses = []

    # Test: Document length
    hall_doc_len = hall_df['avg_doc_length'].mean()
    clean_doc_len = clean_df['avg_doc_length'].mean()

    if hall_doc_len > clean_doc_len * 1.3:
        hypotheses.append(
            f"📚 LONGER DOCUMENTS → MORE HALLUCINATIONS\n"
            f"   Hallucination cases have {(hall_doc_len/clean_doc_len - 1)*100:.0f}% longer documents on average.\n"
            f"   Hypothesis: Conecta struggles to parse long documents accurately."
        )
    elif hall_doc_len < clean_doc_len * 0.7:
        hypotheses.append(
            f"📄 SHORTER DOCUMENTS → MORE HALLUCINATIONS\n"
            f"   Hallucination cases have {(1 - hall_doc_len/clean_doc_len)*100:.0f}% shorter documents on average.\n"
            f"   Hypothesis: Insufficient information forces Conecta to fill gaps with invented details."
        )

    # Test: Document count
    hall_doc_count = hall_df['doc_count'].mean()
    clean_doc_count = clean_df['doc_count'].mean()

    if hall_doc_count > clean_doc_count * 1.2:
        hypotheses.append(
            f"📚 TOO MANY DOCUMENTS → CONFUSION\n"
            f"   Hallucination cases have {hall_doc_count:.1f} docs vs {clean_doc_count:.1f} for clean cases.\n"
            f"   Hypothesis: Multiple documents cause information mixing or confusion."
        )
    elif hall_doc_count < clean_doc_count * 0.8:
        hypotheses.append(
            f"📄 TOO FEW DOCUMENTS → INSUFFICIENT INFO\n"
            f"   Hallucination cases have {hall_doc_count:.1f} docs vs {clean_doc_count:.1f} for clean cases.\n"
            f"   Hypothesis: Retrieval system isn't finding enough relevant documents."
        )

    # Test: Document relevance
    hall_rel = hall_df['doc_relevance_score'].mean()
    clean_rel = clean_df['doc_relevance_score'].mean()

    if hall_rel < clean_rel - 0.5:
        hypotheses.append(
            f"🎯 POOR DOCUMENT RETRIEVAL → HALLUCINATIONS\n"
            f"   Hallucination cases have relevance score {hall_rel:.1f}/5 vs {clean_rel:.1f}/5 for clean cases.\n"
            f"   Hypothesis: When retrieval fails, Conecta invents information instead of admitting uncertainty."
        )

    # Test: Document has answer
    hall_has_answer_pct = hall_df['doc_has_answer'].sum() / len(hall_df) * 100
    clean_has_answer_pct = clean_df['doc_has_answer'].sum() / len(clean_df) * 100

    if hall_has_answer_pct > 50:
        hypotheses.append(
            f"⚠️  HALLUCINATING DESPITE HAVING THE ANSWER!\n"
            f"   {hall_has_answer_pct:.0f}% of hallucination cases had the answer in documents.\n"
            f"   Hypothesis: This is a CRITICAL issue - Conecta is adding false details even when correct info is available."
        )
    else:
        hypotheses.append(
            f"ℹ️  MISSING INFORMATION → HALLUCINATIONS\n"
            f"   Only {hall_has_answer_pct:.0f}% of hallucination cases had the answer in documents.\n"
            f"   Hypothesis: Hallucinations primarily occur when information is missing (expected behavior)."
        )

    # Test: Question clarity
    hall_vague_pct = hall_df['q_is_vague'].sum() / len(hall_df) * 100
    clean_vague_pct = clean_df['q_is_vague'].sum() / len(clean_df) * 100

    if hall_vague_pct > clean_vague_pct + 20:
        hypotheses.append(
            f"❓ VAGUE QUESTIONS → HALLUCINATIONS\n"
            f"   {hall_vague_pct:.0f}% of hallucination cases vs {clean_vague_pct:.0f}% of clean cases had vague questions.\n"
            f"   Hypothesis: Conecta fills in gaps when user question is too general."
        )

    # Test: Response length
    hall_resp_len = hall_df['r_length'].mean()
    clean_resp_len = clean_df['r_length'].mean()

    if hall_resp_len > clean_resp_len * 1.2:
        hypotheses.append(
            f"📝 LONGER RESPONSES → MORE HALLUCINATIONS\n"
            f"   Hallucination cases have {(hall_resp_len/clean_resp_len - 1)*100:.0f}% longer responses.\n"
            f"   Hypothesis: Conecta adds false details when trying to be overly comprehensive."
        )

    if len(hypotheses) == 0:
        hypotheses.append("✅ No clear patterns detected. Hallucinations may be random or require larger sample size.")

    return hypotheses
