"""
Helper functions for analyzing and visualizing evaluation results
"""
import pandas as pd
from typing import Dict, Any, List
import textwrap


def wrap_text(text: str, width: int = 100) -> str:
    """Wrap text to specified width"""
    if not text or pd.isna(text):
        return "N/A"
    return "\n".join(textwrap.wrap(str(text), width=width))


def print_section_header(title: str, char: str = "="):
    """Print formatted section header"""
    print("\n" + char * 100)
    print(f" {title}")
    print(char * 100)


def display_conversation_detail(
    conversation_data: Dict[str, Any],
    evaluation_result: Dict[str, Any],
    show_documents: bool = False,
    show_evidence: bool = True
):
    """
    Display detailed analysis of a single conversation evaluation

    Args:
        conversation_data: Original conversation data
        evaluation_result: Evaluation results from orchestrator
        show_documents: Whether to show full documents
        show_evidence: Whether to show hallucination evidence
    """
    print_section_header(f"CONVERSATION: {conversation_data.get('sessionId', 'Unknown')[:40]}")

    # USER QUESTION
    print("\n📝 USER QUESTION:")
    print("-" * 100)
    question = conversation_data.get('user_question', 'N/A')
    print(wrap_text(question, 100))

    # AI RESPONSE
    print("\n🤖 CONECTA'S RESPONSE:")
    print("-" * 100)
    response = conversation_data.get('ai_response', 'N/A')
    print(wrap_text(response, 100))

    # DOCUMENTS (optional)
    if show_documents:
        print("\n📚 DOCUMENTS USED:")
        print("-" * 100)
        docs = conversation_data.get('all_documents', 'N/A')
        print(wrap_text(docs[:800], 100) + "..." if len(str(docs)) > 800 else wrap_text(docs, 100))

    # EVALUATION RESULTS
    print_section_header("EVALUATION RESULTS", "=")

    if not evaluation_result.get('success'):
        print(f"\n❌ Evaluation failed: {evaluation_result.get('error', 'Unknown error')}")
        return

    # 1. HALLUCINATION ANALYSIS (PRIORITY)
    print("\n🚨 HALLUCINATION DETECTION (CRITICAL)")
    print("-" * 100)

    hall_data = evaluation_result.get('hallucination', {})
    if hall_data:
        detected = hall_data.get('hallucination_detected', False)
        severity = hall_data.get('severity', 'unknown')
        hall_type = hall_data.get('hallucination_type', 'unknown')
        confidence = hall_data.get('confidence', 0.0)

        # Color-coded status
        status_icon = "🔴" if detected else "✅"
        severity_emoji = {
            'critical': '🔥',
            'major': '🔴',
            'minor': '🟡',
            'none': '✅'
        }.get(severity, '❓')

        print(f"{status_icon} Hallucination Detected: {detected}")
        print(f"{severity_emoji} Severity: {severity.upper()}")
        print(f"   Type: {hall_type}")
        print(f"   Confidence: {confidence:.1%}")

        # Claims analysis
        total_claims = hall_data.get('total_claims', 0)
        grounded = hall_data.get('grounded_claims', 0)
        hallucinated = hall_data.get('hallucinated_claims', 0)
        grounding_ratio = hall_data.get('grounding_ratio', 0.0)

        print(f"\n📊 Claims Analysis:")
        print(f"   Total claims examined: {total_claims}")
        print(f"   ✅ Grounded in documents: {grounded} ({grounding_ratio:.1%})")
        print(f"   ❌ Hallucinated/Unsupported: {hallucinated}")

        # Overall assessment
        assessment = hall_data.get('overall_assessment', 'N/A')
        print(f"\n💭 AI Evaluator's Assessment:")
        print(wrap_text(assessment, 95))

        # Evidence (if hallucination detected)
        if detected and show_evidence:
            evidence = hall_data.get('evidence', [])
            hallucinated_claims = hall_data.get('hallucinated_claim_details', [])

            if hallucinated_claims:
                print(f"\n🔍 HALLUCINATED CLAIMS (Evidence):")
                print("-" * 100)
                for i, claim_evidence in enumerate(hallucinated_claims, 1):
                    claim = claim_evidence.get('claim', 'N/A')
                    doc_support = claim_evidence.get('document_support', 'NOT FOUND')
                    explanation = claim_evidence.get('explanation', 'N/A')

                    print(f"\n   Claim #{i}:")
                    print(f"   📌 Statement: {wrap_text(claim, 90)}")
                    print(f"   📄 Document Support: {doc_support}")
                    print(f"   💡 Explanation: {wrap_text(explanation, 90)}")
    else:
        print("⚠️  No hallucination data available")

    # 2. DOCUMENT RELEVANCE
    print("\n\n🔍 DOCUMENT RELEVANCE")
    print("-" * 100)

    doc_data = evaluation_result.get('document_relevance', {})
    if doc_data:
        relevance_score = doc_data.get('relevance_score', 0)
        has_answer = doc_data.get('has_answer', False)

        # Score visualization
        score_bar = "█" * relevance_score + "░" * (5 - relevance_score)
        print(f"   Score: [{score_bar}] {relevance_score}/5")
        print(f"   Documents contain answer: {'✅ Yes' if has_answer else '❌ No'}")

        missing = doc_data.get('missing_information', [])
        if missing and len(missing) > 0:
            print(f"\n   ⚠️  Missing Information:")
            for item in missing[:3]:
                print(f"      • {item}")

        explanation = doc_data.get('explanation', 'N/A')
        print(f"\n   💭 Explanation: {wrap_text(explanation, 90)}")
    else:
        print("⚠️  No document relevance data available")

    # 3. COMPLETENESS
    print("\n\n✅ COMPLETENESS CHECK")
    print("-" * 100)

    comp_data = evaluation_result.get('completeness', {})
    if comp_data:
        comp_score = comp_data.get('completeness_score', 0)
        used_all = comp_data.get('used_all_relevant_info', False)
        unnecessary_clarif = comp_data.get('unnecessary_clarification', False)

        # Score visualization
        score_bar = "█" * comp_score + "░" * (5 - comp_score)
        print(f"   Score: [{score_bar}] {comp_score}/5")
        print(f"   Used all relevant info: {'✅ Yes' if used_all else '❌ No'}")

        if unnecessary_clarif:
            print(f"   🔴 UNNECESSARY CLARIFICATION DETECTED")
            print(f"      → Conecta asked for clarification when answer was in documents!")

        missing_info = comp_data.get('missing_information', [])
        if missing_info and len(missing_info) > 0:
            print(f"\n   ⚠️  Information NOT included in response:")
            for item in missing_info[:3]:
                print(f"      • {item}")

        explanation = comp_data.get('explanation', 'N/A')
        print(f"\n   💭 Explanation: {wrap_text(explanation, 90)}")
    else:
        print("⚠️  No completeness data available")

    # 4. ESCALATION VALIDATION
    print("\n\n🎯 ESCALATION VALIDATION")
    print("-" * 100)

    esc_data = evaluation_result.get('escalation', {})
    if esc_data:
        appropriate = esc_data.get('escalation_appropriate', False)
        should_have = esc_data.get('should_have_escalated', False)

        escalated = conversation_data.get('escalated', False) or conversation_data.get('need_expert', False)

        print(f"   Actually escalated: {'✅ Yes' if escalated else '❌ No'}")
        print(f"   Escalation was appropriate: {'✅ Yes' if appropriate else '❌ No'}")
        print(f"   Should have escalated: {'✅ Yes' if should_have else '❌ No'}")

        # Determine if this was a mistake
        if escalated and not appropriate:
            print(f"\n   🔴 UNNECESSARY ESCALATION - Could have been handled by Conecta!")
        elif not escalated and should_have:
            print(f"\n   🔴 MISSED ESCALATION - Should have escalated to expert!")

        reason = esc_data.get('reason', 'N/A')
        print(f"\n   💭 Reason: {wrap_text(reason, 90)}")

        alternative = esc_data.get('alternative_action', '')
        if alternative and alternative != 'N/A':
            print(f"\n   💡 Alternative action: {wrap_text(alternative, 90)}")
    else:
        print("⚠️  No escalation data available")

    # 5. VERIFICATION (if present)
    ver_data = evaluation_result.get('verification', {})
    if ver_data:
        print("\n\n🔬 SECONDARY VERIFICATION (Critical Finding)")
        print("-" * 100)

        verified = ver_data.get('verified', False)
        new_severity = ver_data.get('new_severity', 'none')
        recommendation = ver_data.get('final_recommendation', 'review')

        print(f"   Verified: {'✅ Confirmed' if verified else '❌ Rejected'}")
        print(f"   Adjusted severity: {new_severity}")
        print(f"   Final recommendation: {recommendation.upper()}")

        explanation = ver_data.get('explanation', 'N/A')
        print(f"\n   💭 Verification explanation: {wrap_text(explanation, 90)}")

    print("\n" + "=" * 100 + "\n")


def create_evaluation_summary_table(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create summary table from evaluation results

    Args:
        results: List of evaluation result dictionaries

    Returns:
        DataFrame with summary metrics
    """
    summary_data = []

    for result in results:
        if not result.get('success'):
            continue

        hall = result.get('hallucination', {})
        doc = result.get('document_relevance', {})
        comp = result.get('completeness', {})

        summary_data.append({
            'session_id': result.get('session_id', 'unknown')[:20],
            'hallucination': '🔴' if hall.get('hallucination_detected') else '✅',
            'severity': hall.get('severity', 'none'),
            'grounding': f"{hall.get('grounding_ratio', 0):.0%}",
            'doc_score': f"{doc.get('relevance_score', 0)}/5",
            'comp_score': f"{comp.get('completeness_score', 0)}/5",
            'unnecessary_clarif': '🔴' if comp.get('unnecessary_clarification') else '✅'
        })

    return pd.DataFrame(summary_data)


def analyze_evaluation_quality(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the quality of evaluations themselves

    Args:
        results: List of evaluation result dictionaries

    Returns:
        Dictionary with quality metrics
    """
    successful = [r for r in results if r.get('success')]

    if not successful:
        return {'error': 'No successful evaluations'}

    # Extract hallucination data
    hallucinations = [r.get('hallucination', {}) for r in successful]

    # Confidence distribution
    confidences = [h.get('confidence', 0) for h in hallucinations]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    # Detection consistency
    detected = [h.get('hallucination_detected', False) for h in hallucinations]
    detection_rate = sum(detected) / len(detected) if detected else 0

    # Severity distribution
    severities = [h.get('severity', 'none') for h in hallucinations]
    severity_dist = pd.Series(severities).value_counts().to_dict()

    # Claims analysis
    total_claims = [h.get('total_claims', 0) for h in hallucinations]
    avg_claims = sum(total_claims) / len(total_claims) if total_claims else 0

    # Grounding ratios
    grounding = [h.get('grounding_ratio', 0) for h in hallucinations]
    avg_grounding = sum(grounding) / len(grounding) if grounding else 0

    return {
        'total_evaluations': len(results),
        'successful': len(successful),
        'failed': len(results) - len(successful),
        'avg_confidence': avg_confidence,
        'detection_rate': detection_rate,
        'severity_distribution': severity_dist,
        'avg_claims_per_response': avg_claims,
        'avg_grounding_ratio': avg_grounding
    }


def print_quality_report(quality_metrics: Dict[str, Any]):
    """Print formatted quality report"""
    print_section_header("EVALUATION QUALITY REPORT", "=")

    print(f"\n📊 Overall Statistics:")
    print(f"   Total evaluations: {quality_metrics.get('total_evaluations', 0)}")
    print(f"   ✅ Successful: {quality_metrics.get('successful', 0)}")
    print(f"   ❌ Failed: {quality_metrics.get('failed', 0)}")

    print(f"\n🎯 Detection Metrics:")
    print(f"   Average confidence: {quality_metrics.get('avg_confidence', 0):.1%}")
    print(f"   Detection rate: {quality_metrics.get('detection_rate', 0):.1%}")
    print(f"   Average claims per response: {quality_metrics.get('avg_claims_per_response', 0):.1f}")
    print(f"   Average grounding ratio: {quality_metrics.get('avg_grounding_ratio', 0):.1%}")

    print(f"\n📈 Severity Distribution:")
    severity_dist = quality_metrics.get('severity_distribution', {})
    for severity, count in severity_dist.items():
        emoji = {'none': '✅', 'minor': '🟡', 'major': '🔴', 'critical': '🔥'}.get(severity, '❓')
        print(f"   {emoji} {severity.upper()}: {count}")

    print("\n" + "=" * 100 + "\n")
