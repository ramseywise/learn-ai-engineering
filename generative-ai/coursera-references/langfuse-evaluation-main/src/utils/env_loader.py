"""
Environment variable loader utility
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def load_environment():
    """
    Load environment variables from .env file

    Searches for .env file in:
    1. Current directory
    2. Parent directory (project root)
    """
    if not DOTENV_AVAILABLE:
        print("⚠️  python-dotenv not installed. Using system environment variables only.")
        print("   Install with: pip install python-dotenv")
        return

    # Try to find .env file
    current_dir = Path.cwd()
    env_paths = [
        current_dir / '.env',
        current_dir.parent / '.env',
        Path(__file__).parent.parent.parent / '.env'  # Project root
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Loaded environment from: {env_path}")
            return

    print("⚠️  No .env file found. Using system environment variables.")
    print(f"   Create .env file at: {current_dir}")


def get_api_key(provider: str = "gemini") -> str:
    """
    Get API key from environment

    Args:
        provider: 'gemini' or 'vertex'

    Returns:
        API key or empty string
    """
    if provider.lower() == "gemini":
        key = os.getenv('GEMINI_API_KEY', '')
        if not key:
            print("❌ GEMINI_API_KEY not set!")
            print("   1. Copy .env.example to .env")
            print("   2. Add your Gemini API key")
            print("   3. Get key from: https://makersuite.google.com/app/apikey")
        return key

    elif provider.lower() == "vertex":
        project_id = os.getenv('VERTEX_PROJECT_ID', '')
        if not project_id:
            print("❌ VERTEX_PROJECT_ID not set!")
            print("   1. Copy .env.example to .env")
            print("   2. Add your GCP project ID")
        return project_id

    else:
        raise ValueError(f"Unknown provider: {provider}")


def validate_environment():
    """
    Validate that required environment variables are set

    Returns:
        True if valid, False otherwise
    """
    gemini_key = os.getenv('GEMINI_API_KEY')
    vertex_project = os.getenv('VERTEX_PROJECT_ID')

    if not gemini_key and not vertex_project:
        print("❌ No API credentials found!")
        print("")
        print("Please set up your credentials:")
        print("1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print("")
        print("2. Edit .env and add your API key:")
        print("   For Gemini: GEMINI_API_KEY=your-key-here")
        print("   For Vertex: VERTEX_PROJECT_ID=your-project-id")
        print("")
        return False

    if gemini_key:
        print(f"✅ Gemini API key found: {gemini_key[:10]}...")

    if vertex_project:
        print(f"✅ Vertex project ID found: {vertex_project}")

    return True
