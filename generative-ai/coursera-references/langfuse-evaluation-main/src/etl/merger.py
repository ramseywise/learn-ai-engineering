"""
Data merging utilities for Conecta analysis
"""
import pandas as pd
from typing import Dict, Tuple
import logging

from .json_extractor import process_langfuse_data, explode_sources

logger = logging.getLogger(__name__)


def link_langfuse_to_conversations(
    conversations_df: pd.DataFrame,
    langfuse_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Attempt to link Langfuse sessionId to conversation IDs

    Strategy:
    1. Try direct mapping if column exists
    2. Use timestamp + email correlation
    3. Manual mapping table if provided

    Args:
        conversations_df: Main conversations dataframe
        langfuse_df: Langfuse traces dataframe

    Returns:
        Tuple of (linked conversations, unlinked langfuse traces)
    """
    logger.info("Attempting to link Langfuse data to conversations...")

    # Process langfuse data first
    langfuse_processed = process_langfuse_data(langfuse_df)

    # Create a mapping attempt using timestamps and user info
    # This is heuristic-based since we don't have a direct foreign key

    # For now, we'll create a conversation-level analysis for langfuse traces
    # that are complete (have question, answer, and sources)
    complete_traces = langfuse_processed[
        langfuse_processed['user_question'].notna() &
        langfuse_processed['ai_response'].notna() &
        (langfuse_processed['sources'].str.len() > 0)
    ].copy()

    logger.info(f"Found {len(complete_traces)} complete Langfuse traces")

    # Sort by timestamp to get conversation order
    complete_traces = complete_traces.sort_values(['sessionId', 'timestamp'])

    # Add previous turn information for context
    complete_traces['prev_user_question'] = complete_traces.groupby('sessionId')['user_question'].shift(1)
    complete_traces['prev_ai_response'] = complete_traces.groupby('sessionId')['ai_response'].shift(1)
    complete_traces['turn_number'] = complete_traces.groupby('sessionId').cumcount() + 1
    complete_traces['total_turns'] = complete_traces.groupby('sessionId')['sessionId'].transform('count')

    # Group by sessionId to get conversation-level data
    conversation_langfuse = complete_traces.groupby('sessionId').agg({
        'id': 'first',  # trace ID
        'timestamp': 'first',
        'user_question': 'last',  # Last question in session
        'ai_response': 'last',  # Last response
        'prev_user_question': 'last',  # Previous user question (for context)
        'prev_ai_response': 'last',  # Previous AI response (for context)
        'turn_number': 'last',  # Which turn is this (1, 2, 3...)
        'total_turns': 'last',  # Total turns in session
        'sources': lambda x: list(set([s for sublist in x for s in sublist])),  # All unique sources
        'need_expert': 'any',  # Did any interaction need expert?
        'expert_category': 'last',
        'totalCost': 'sum',
        'inputTokens': 'sum',
        'outputTokens': 'sum'
    }).reset_index()

    logger.info(f"Aggregated to {len(conversation_langfuse)} conversations")
    logger.info(f"Multi-turn conversations: {(conversation_langfuse['total_turns'] > 1).sum()}")

    return complete_traces, conversation_langfuse


def merge_all_datasets(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merge all datasets into a unified analysis dataframe

    Merging strategy:
    1. Start with conversations (File 1)
    2. Left join with Genesys expert data (File 2) on fk_tbl_conversaciones_conecta2
    3. Process and aggregate Langfuse data (File 3)
    4. Explode sources and join with knowledge base (File 4)

    Args:
        data: Dictionary with all loaded dataframes

    Returns:
        Merged dataframe ready for analysis
    """
    logger.info("Starting data merge process...")

    conversations = data['conversations'].copy()
    genesys = data['genesys'].copy()
    langfuse = data['langfuse'].copy()
    kb = data['knowledge_base'].copy()

    # Step 1: Link Langfuse to conversations
    langfuse_traces, langfuse_conversations = link_langfuse_to_conversations(
        conversations, langfuse
    )

    # Step 2: For analysis, we'll focus on Langfuse traces with complete data
    # since they have the most detailed information
    analysis_df = langfuse_traces.copy()

    # Step 3: Add expert escalation info if available
    # Note: This requires matching sessionId to fk_tbl_conversaciones_conecta2
    # For now, we'll keep them separate and join in the notebook if mapping is available

    logger.info(f"Created analysis dataset with {len(analysis_df)} interactions")

    return analysis_df


def enrich_with_documents(
    analysis_df: pd.DataFrame,
    kb_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Enrich analysis dataframe with actual document content

    Args:
        analysis_df: Main analysis dataframe
        kb_df: Knowledge base dataframe

    Returns:
        Enriched dataframe with document content
    """
    logger.info("Enriching with document content...")

    # Explode sources to get one row per document
    df_exploded = explode_sources(analysis_df)

    # Convert document_id to same type as KB id
    df_exploded['document_id'] = pd.to_numeric(
        df_exploded['document_id'],
        errors='coerce'
    )

    # Prepare KB data
    kb_clean = kb_df[['idtbl_pregunta', 'titulo', 'respuesta', 'keywords_rag']].copy()
    kb_clean = kb_clean.rename(columns={
        'idtbl_pregunta': 'document_id',
        'titulo': 'doc_title',
        'respuesta': 'doc_content',
        'keywords_rag': 'doc_keywords'
    })

    # Join with knowledge base
    enriched = df_exploded.merge(
        kb_clean,
        on='document_id',
        how='left'
    )

    logger.info(f"Enriched {len(enriched)} document-interaction pairs")

    # Count how many documents were successfully matched
    matched = enriched['doc_content'].notna().sum()
    logger.info(f"Successfully matched {matched}/{len(enriched)} documents ({matched/len(enriched)*100:.1f}%)")

    return enriched


def create_conversation_summary(enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create conversation-level summary aggregating all documents used

    Args:
        enriched_df: Exploded dataframe with document content

    Returns:
        Conversation-level dataframe for evaluation
    """
    logger.info("Creating conversation-level summary...")

    # Group by sessionId and aggregate
    summary = enriched_df.groupby('sessionId').agg({
        'id': 'first',
        'timestamp': 'first',
        'user_question': 'first',
        'ai_response': 'first',
        'prev_user_question': 'first',  # Conversation history
        'prev_ai_response': 'first',  # Conversation history
        'turn_number': 'first',  # Which turn in conversation
        'total_turns': 'first',  # Total turns
        'need_expert': 'first',
        'expert_category': 'first',
        'document_id': list,
        'doc_title': list,
        'doc_content': list,
        'doc_keywords': list,
        'totalCost': 'first',
        'inputTokens': 'first',
        'outputTokens': 'first'
    }).reset_index()

    # Concatenate all document content into a single "sources" text
    summary['all_documents'] = summary.apply(
        lambda row: '\n\n---\n\n'.join([
            f"Documento {doc_id}: {title}\n{content}"
            for doc_id, title, content in zip(
                row['document_id'],
                row['doc_title'],
                row['doc_content']
            )
            if pd.notna(content)
        ]),
        axis=1
    )

    logger.info(f"Created summary for {len(summary)} conversations")

    return summary
