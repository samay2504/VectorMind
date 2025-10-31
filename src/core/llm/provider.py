"""
LLM Provider System with Multiple Fallbacks
Handles HuggingFace, Google Gemini, OpenAI, and Groq with robust error handling
Adapted from the provided llm_provider.py with tracing and metadata support
"""

import logging
import os
import time
import uuid
from typing import Any, Dict, Optional, Union

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not available, continue without it

# Import pretty printing utilities
try:
    from src.utils import print_llm_fallback_info, print_llm_provider_info, print_status
except ImportError:
    # Fallback for direct execution
    def print_status(message, status="info", icon=None):
        print(f"[{status.upper()}] {message}")

    def print_llm_provider_info(provider_name, model=""):
        print(f"Using LLM provider: {provider_name}")
        if model:
            print(f"Model: {model}")

    def print_llm_fallback_info(failed_providers, active_provider):
        if failed_providers:
            print(f"LLM providers failed: {', '.join(failed_providers)}")
            print(f"Using fallback provider: {active_provider}")


# Import all possible LLM providers
try:
    from langchain_huggingface import HuggingFaceEndpoint

    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI

    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_groq import ChatGroq

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from huggingface_hub import HfApi

    HF_API_AVAILABLE = True
except ImportError:
    HF_API_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMProvider:
    """Robust LLM provider with multiple fallback options and traceability."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_provider = None
        self.current_model = None
        self.llm = None
        self._setup_llm()

    def _setup_llm(self):
        """Setup LLM with fallback chain based on configuration."""
        # Get provider preference from config or use default
        provider_preference = self.config.get(
            "provider_preference",
            ["google_genai", "groq", "huggingface", "openai", "fallback"],
        )

        # Map provider names to their functions
        provider_map = {
            "huggingface": ("HuggingFace", self._try_huggingface),
            "google_genai": ("Google Gemini", self._try_google_genai),
            "groq": ("Groq", self._try_groq),
            "openai": ("OpenAI", self._try_openai),
            "fallback": ("Fallback", self._create_fallback_llm),
        }

        # Build provider list based on preference
        providers = []
        for provider_name in provider_preference:
            if provider_name in provider_map:
                providers.append(provider_map[provider_name])

        # Add any missing providers at the end
        for provider_name, provider_func in provider_map.items():
            if provider_name not in provider_preference:
                providers.append(provider_func)

        failed_providers = []

        for provider_name, provider_func in providers:
            try:
                print_status(f"Testing {provider_name} provider...", "progress")
                self.llm = provider_func()
                if self.llm:
                    print_status(f"Successfully initialized {provider_name}", "success")
                    print_llm_provider_info(
                        provider_name, getattr(self.llm, "model_name", self.current_model or "")
                    )
                    return
            except Exception as e:
                error_msg = str(e)
                failed_providers.append(provider_name)

                # Handle specific error types
                if "quota" in error_msg.lower() or "429" in error_msg or "rate" in error_msg.lower():
                    print_status(f"{provider_name} quota/rate limit exceeded", "warning")
                elif "not set" in error_msg.lower():
                    print_status(f"{provider_name} API key not configured", "warning")
                elif "not available" in error_msg.lower():
                    print_status(f"{provider_name} package not installed", "warning")
                elif "all" in error_msg.lower() and "failed" in error_msg.lower():
                    print_status(f"{provider_name} models unavailable", "warning")
                elif "token" in error_msg.lower() and "permissions" in error_msg.lower():
                    print_status(f"{provider_name} token lacks permissions", "warning")
                else:
                    print_status(f"{provider_name} initialization failed", "error")

                logger.warning(f"{provider_name} failed: {e}")
                continue

        # If all providers fail, create fallback
        self.llm = self._create_fallback_llm()
        print_status("All LLM providers failed, using fallback mode", "warning")
        print_llm_fallback_info(failed_providers, "Fallback")

    def _test_huggingface_token(self) -> bool:
        """Test if HuggingFace token has proper permissions."""
        if not HF_API_AVAILABLE:
            return False

        try:
            api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if not api_key:
                return False

            api = HfApi(token=api_key)
            # Test with a simple API call
            list(api.list_models(author="bigcode", limit=1))
            logger.info("HuggingFace token validated successfully")
            return True
        except Exception as e:
            logger.warning(f"HuggingFace token validation failed: {e}")
            return False

    def _try_huggingface(self):
        """Try to initialize HuggingFace LLM."""
        if not HUGGINGFACE_AVAILABLE:
            raise ImportError("langchain_huggingface not available")

        api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not api_key:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN not set")

        # Test token permissions
        if not self._test_huggingface_token():
            raise ValueError("HuggingFace token lacks proper permissions")

        # Try multiple HuggingFace models in order of preference
        models_to_try = [
            "microsoft/DialoGPT-medium",
            "gpt2",
            "facebook/opt-350m",
            "bigscience/bloom-560m",
        ]

        temperature = self.config.get("temperature", 0.1)

        for model_name in models_to_try:
            try:
                print_status(f"Trying HuggingFace model: {model_name}", "progress")
                llm = HuggingFaceEndpoint(
                    repo_id=model_name,
                    huggingfacehub_api_token=api_key,
                    task="text-generation",
                    temperature=temperature,
                )
                # Test the connection
                test_response = llm.invoke("Test")
                if test_response:
                    self.current_provider = f"huggingface_{model_name}"
                    self.current_model = model_name
                    return llm
            except Exception as e:
                logger.warning(f"HuggingFace model {model_name} failed: {e}")
                continue
        raise ValueError("All HuggingFace models failed")

    def _try_google_genai(self):
        """Try to initialize Google Gemini LLM."""
        if not GOOGLE_GENAI_AVAILABLE:
            raise ImportError("langchain_google_genai not available")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        try:
            models_to_try = [
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-pro",
            ]

            for model in models_to_try:
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=model,
                        google_api_key=api_key,
                        temperature=self.config.get("temperature", 0.1),
                        max_retries=0,
                    )

                    # Test the connection
                    test_response = llm.invoke("Test")
                    if test_response:
                        self.current_provider = f"google_genai_{model}"
                        self.current_model = model
                        return llm
                except Exception as test_error:
                    error_str = str(test_error)
                    if (
                        "429" in error_str
                        or "quota" in error_str.lower()
                        or "rate" in error_str.lower()
                        or "ResourceExhausted" in error_str
                    ):
                        logger.warning(
                            f"Google Gemini quota exceeded for {model}, skipping all Google models"
                        )
                        raise ValueError(f"Google Gemini quota exceeded: {test_error}")
                    else:
                        logger.warning(f"Google Gemini test failed for {model}: {test_error}")
                        continue

            raise ValueError("All Google Gemini models failed")

        except Exception as e:
            logger.error(f"Google Gemini initialization failed: {e}")
            raise

    def _try_openai(self):
        """Try to initialize OpenAI LLM."""
        if not OPENAI_AVAILABLE:
            raise ImportError("langchain_openai not available")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")

        try:
            models_to_try = ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

            for model in models_to_try:
                try:
                    llm = ChatOpenAI(
                        model=model,
                        openai_api_key=api_key,
                        temperature=self.config.get("temperature", 0.1),
                    )

                    # Test the connection
                    test_response = llm.invoke("Test")
                    if test_response:
                        self.current_provider = f"openai_{model}"
                        self.current_model = model
                        return llm
                except Exception as test_error:
                    logger.warning(f"OpenAI test failed for {model}: {test_error}")
                    continue

            raise ValueError("All OpenAI models failed")

        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
            raise

    def _try_groq(self):
        """Try to initialize Groq LLM."""
        if not GROQ_AVAILABLE:
            raise ImportError("langchain_groq not available")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set")

        logger.info("Groq API key found, attempting Groq models...")

        try:
            models_to_try = [
                "llama-3.1-8b-instant",
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768",
            ]

            for model in models_to_try:
                try:
                    llm = ChatGroq(
                        model=model,
                        groq_api_key=api_key,
                        temperature=self.config.get("temperature", 0.1),
                    )

                    # Test the connection
                    test_response = llm.invoke("Test")
                    if test_response:
                        self.current_provider = f"groq_{model}"
                        self.current_model = model
                        logger.info(f"Groq model {model} initialized successfully")
                        return llm
                except Exception as test_error:
                    logger.warning(f"Groq test failed for {model}: {test_error}")
                    continue

            raise ValueError("All Groq models failed")

        except Exception as e:
            logger.error(f"Groq initialization failed: {e}")
            raise

    def _create_fallback_llm(self):
        """Create a fallback LLM for when all providers fail."""

        class FallbackLLM:
            def __init__(self):
                self.name = "fallback_llm"
                self.model_name = "fallback_static_analysis"
                self.current_provider = "fallback"

            def invoke(self, prompt):
                if "code review" in prompt.lower():
                    return {
                        "content": "Fallback static analysis mode: Performing basic code analysis without LLM."
                    }
                elif "security" in prompt.lower():
                    return {
                        "content": "Fallback security analysis: Checking for common security patterns."
                    }
                elif "performance" in prompt.lower():
                    return {
                        "content": "Fallback performance analysis: Identifying basic performance issues."
                    }
                else:
                    return {
                        "content": "Fallback analysis mode: Using static code analysis techniques."
                    }

        fallback_llm = FallbackLLM()
        self.current_provider = "fallback"
        self.current_model = "fallback_static_analysis"
        return fallback_llm

    def invoke(
        self, prompt: str, trace_id: Optional[str] = None
    ) -> Dict[str, Union[str, Dict[str, Any]]]:
        """
        Invoke the LLM with a prompt and return response with metadata.

        Args:
            prompt: The input prompt
            trace_id: Optional trace ID for tracking

        Returns:
            Dictionary with 'content' and 'metadata' keys
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        start_time = time.time()

        try:
            response = self.llm.invoke(prompt)

            # Handle different response formats
            if isinstance(response, dict):
                content = (
                    response.get("content")
                    or response.get("text")
                    or str(response)
                )
            elif isinstance(response, str):
                content = response
            else:
                # Try to get content from response object
                content = (
                    getattr(response, "content", None)
                    or getattr(response, "text", None)
                    or str(response)
                )

            latency_ms = (time.time() - start_time) * 1000

            metadata = {
                "trace_id": trace_id,
                "provider": self.current_provider,
                "model": self.current_model,
                "latency_ms": round(latency_ms, 2),
                "timestamp": time.time(),
                "fallback_mode": self.current_provider == "fallback",
            }

            return {"content": content, "metadata": metadata}

        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            latency_ms = (time.time() - start_time) * 1000

            # Return error with metadata
            return {
                "content": None,
                "metadata": {
                    "trace_id": trace_id,
                    "provider": self.current_provider,
                    "model": self.current_model,
                    "latency_ms": round(latency_ms, 2),
                    "timestamp": time.time(),
                    "error": str(e),
                    "fallback_mode": self.current_provider == "fallback",
                },
            }

    @property
    def name(self):
        """Get the name of the current LLM provider."""
        if hasattr(self.llm, "name"):
            return self.llm.name
        return self.current_provider or "unknown"

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current LLM provider."""
        return {
            "provider": self.current_provider,
            "model": self.current_model,
            "available": self.llm is not None,
            "fallback_mode": self.current_provider == "fallback",
        }


def create_llm_provider(config: Dict[str, Any]) -> LLMProvider:
    """Factory function to create LLM provider."""
    return LLMProvider(config)
