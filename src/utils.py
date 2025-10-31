"""
Utility functions for pretty printing and status messages
"""
from typing import Optional


def print_status(message: str, status: str = "info", icon: Optional[str] = None):
    """Print colored status message"""
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "progress": "🔄",
    }
    
    selected_icon = icon or icons.get(status, "•")
    print(f"{selected_icon} [{status.upper()}] {message}")


def print_llm_provider_info(provider_name: str, model: str = ""):
    """Print LLM provider information"""
    print(f"🤖 Using LLM provider: {provider_name}")
    if model:
        print(f"   Model: {model}")


def print_llm_fallback_info(failed_providers: list, active_provider: str):
    """Print LLM fallback information"""
    if failed_providers:
        print(f"⚠️  LLM providers failed: {', '.join(failed_providers)}")
        print(f"🔄 Using fallback provider: {active_provider}")
