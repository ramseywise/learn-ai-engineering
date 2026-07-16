"""
JSON extraction utilities for Langfuse data
"""
import json
import pandas as pd
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


def safe_json_parse(json_str: str) -> Optional[Dict]:
    """
    Safely parse JSON string

    Args:
        json_str: JSON string to parse

    Returns:
        Parsed dict or None if parsing fails
    """
    if pd.isna(json_str) or not json_str:
        return None

    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return None


def extract_sources_from_output(output_json: Dict) -> List[str]:
    """
    Extract document IDs (sources) from Langfuse output JSON

    Args:
        output_json: Parsed output JSON from Langfuse

    Returns:
        List of document IDs used in the response
    """
    sources = []

    if not output_json:
        return sources

    # Try multiple locations where sources might be stored
    locations = [
        ('sources',),
        ('structured_response', 'sources'),
        ('expert_category',),  # Sometimes stored as single ID
    ]

    for location in locations:
        try:
            value = output_json
            for key in location:
                value = value.get(key)
                if value is None:
                    break

            if value:
                if isinstance(value, list):
                    sources.extend([str(s) for s in value])
                else:
                    sources.append(str(value))
        except (AttributeError, TypeError):
            continue

    # Remove duplicates while preserving order
    return list(dict.fromkeys(sources))


def extract_user_question(output_json: Dict) -> Optional[str]:
    """
    Extract the user's question from Langfuse output

    Args:
        output_json: Parsed output JSON

    Returns:
        User question or None
    """
    if not output_json:
        return None

    # Try multiple locations
    locations = [
        ('user_question',),
        ('structured_response', 'advisor_query'),
    ]

    for location in locations:
        try:
            value = output_json
            for key in location:
                value = value.get(key)
                if value is None:
                    break
            if value:
                return str(value)
        except (AttributeError, TypeError):
            continue

    return None


def extract_ai_response(output_json: Dict) -> Optional[str]:
    """
    Extract Conecta's response from Langfuse output

    Args:
        output_json: Parsed output JSON

    Returns:
        AI response or None
    """
    if not output_json:
        return None

    # Try multiple locations
    locations = [
        ('lastMessage',),
        ('structured_response', 'answer'),
    ]

    for location in locations:
        try:
            value = output_json
            for key in location:
                value = value.get(key)
                if value is None:
                    break
            if value:
                return str(value)
        except (AttributeError, TypeError):
            continue

    return None


def extract_escalation_info(output_json: Dict) -> Dict[str, Any]:
    """
    Extract escalation-related information

    Args:
        output_json: Parsed output JSON

    Returns:
        Dictionary with escalation info
    """
    info = {
        'need_expert': False,
        'expert_category': None,
        'user_message_count': None
    }

    if not output_json:
        return info

    try:
        # Check if expert was needed
        if 'structured_response' in output_json:
            sr = output_json['structured_response']
            if 'need_expert' in sr:
                info['need_expert'] = bool(sr['need_expert'])

        # Get expert category
        if 'expert_category' in output_json:
            info['expert_category'] = str(output_json['expert_category'])

        # Get message count
        if 'user_message_count' in output_json:
            info['user_message_count'] = int(output_json['user_message_count'])
    except (TypeError, ValueError, KeyError) as e:
        logger.warning(f"Error extracting escalation info: {e}")

    return info


def process_langfuse_data(langfuse_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process Langfuse dataframe to extract all relevant information

    Args:
        langfuse_df: Raw Langfuse dataframe

    Returns:
        Processed dataframe with extracted fields
    """
    logger.info("Processing Langfuse data...")

    df = langfuse_df.copy()

    # Parse JSON fields
    df['output_parsed'] = df['output'].apply(safe_json_parse)
    df['input_parsed'] = df['input'].apply(safe_json_parse)

    # Extract fields
    df['sources'] = df['output_parsed'].apply(extract_sources_from_output)
    df['user_question'] = df['output_parsed'].apply(extract_user_question)
    df['ai_response'] = df['output_parsed'].apply(extract_ai_response)

    # Extract escalation info
    escalation_info = df['output_parsed'].apply(extract_escalation_info)
    df['need_expert'] = escalation_info.apply(lambda x: x['need_expert'])
    df['expert_category'] = escalation_info.apply(lambda x: x['expert_category'])
    df['user_message_count'] = escalation_info.apply(lambda x: x['user_message_count'])

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    logger.info(f"Extracted sources from {df['sources'].notna().sum()} traces")

    return df


def explode_sources(langfuse_df: pd.DataFrame) -> pd.DataFrame:
    """
    Explode sources to create one row per document used

    Args:
        langfuse_df: Processed Langfuse dataframe

    Returns:
        Dataframe with one row per document used in each trace
    """
    logger.info("Exploding sources to long format...")

    # Filter to rows with sources
    df_with_sources = langfuse_df[langfuse_df['sources'].str.len() > 0].copy()

    # Explode the sources list
    df_exploded = df_with_sources.explode('sources').reset_index(drop=True)

    # Rename for clarity
    df_exploded = df_exploded.rename(columns={'sources': 'document_id'})

    logger.info(f"Exploded to {len(df_exploded)} document-trace pairs")

    return df_exploded
