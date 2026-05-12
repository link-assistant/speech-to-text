"""Core transcription functions with decorator support."""

import logging
from typing import Any, Callable, Dict, List, Optional

from .providers import (
    BaseProvider,
    DeepInfraProvider,
    DeepSeekProvider,
    GroqProvider,
    HuggingFaceProvider,
    OpenAIProvider,
    OpenRouterProvider,
    PiAPIProvider,
)

logger = logging.getLogger(__name__)

# Provider registry
PROVIDER_CLASSES = {
    "huggingface": HuggingFaceProvider,
    "openai": OpenAIProvider,
    "groq": GroqProvider,
    "piapi": PiAPIProvider,
    "openrouter": OpenRouterProvider,
    "deepinfra": DeepInfraProvider,
    "deepseek": DeepSeekProvider,
}


def create_hook_chain(fn: Callable, hooks: Optional[List[Dict[str, Callable]]] = None):
    """Create hook chain for decorating functions.

    Args:
        fn: Original function to decorate
        hooks: List of hook dictionaries with 'before' and/or 'after' keys

    Returns:
        Decorated function
    """
    if not hooks:
        return fn

    async def wrapped(options: Dict[str, Any]) -> Dict[str, Any]:
        # Run before hooks
        modified_options = options
        for hook in hooks:
            if "before" in hook and callable(hook["before"]):
                result = hook["before"](modified_options)
                if result is not None:
                    modified_options = result

        # Execute main function
        result = await fn(modified_options)

        # Run after hooks
        for hook in hooks:
            if "after" in hook and callable(hook["after"]):
                hook_result = hook["after"](result, modified_options)
                if hook_result is not None:
                    result = hook_result

        return result

    return wrapped


def initialize_providers(options: Dict[str, Any]) -> List[BaseProvider]:
    """Initialize transcription providers based on configuration.

    Args:
        options: Configuration dictionary with keys:
            - inference_priority: List of provider names
            - {provider}_api_key: API keys for each provider
            - whisper_model: Model name to use

    Returns:
        List of initialized provider instances
    """
    providers = []

    for provider_name in options.get("inference_priority", []):
        provider_class = PROVIDER_CLASSES.get(provider_name)
        if not provider_class:
            logger.warning(f"Unknown provider: {provider_name}")
            continue

        api_key_map = {
            "huggingface": options.get("huggingface_api_key"),
            "openai": options.get("openai_api_key"),
            "groq": options.get("groq_api_key"),
            "piapi": options.get("piapi_api_key"),
            "openrouter": options.get("openrouter_api_key"),
            "deepinfra": options.get("deepinfra_api_key"),
            "deepseek": options.get("deepseek_api_key"),
        }

        api_key = api_key_map.get(provider_name)
        if not api_key:
            logger.info(f"Skipping {provider_name}: no API key provided")
            continue

        try:
            provider = provider_class({
                "api_key": api_key,
                "model": options.get("whisper_model", "whisper-large-v3"),
            })
            if provider.initialize():
                providers.append(provider)
                logger.info(f"Provider {provider_name} initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize {provider_name}: {e}")

    return providers


def get_available_providers(options: Dict[str, Any]) -> List[str]:
    """Get list of available provider names.

    Args:
        options: Dictionary containing 'providers' key

    Returns:
        List of provider names
    """
    return [p.name for p in options.get("providers", [])]


async def transcribe(options: Dict[str, Any]) -> Dict[str, Any]:
    """Core transcription function.

    Args:
        options: Transcription options dictionary with keys:
            - audio_path: Path to audio file
            - providers: List of provider instances
            - provider: Optional specific provider name
            - hooks: Optional list of hook dictionaries

    Returns:
        Transcription result dictionary
    """
    audio_path = options["audio_path"]
    providers = options.get("providers", [])
    provider_name = options.get("provider")
    hooks = options.get("hooks", [])

    if not providers:
        raise ValueError("No transcription providers available")

    # Create decorated transcribe function if hooks are present
    async def execute_transcribe(opts: Dict[str, Any]) -> Dict[str, Any]:
        # If specific provider requested
        if opts.get("provider"):
            provider = next(
                (p for p in opts["providers"] if p.name == opts["provider"]), None
            )
            if not provider:
                raise ValueError(f"Provider not available: {opts['provider']}")
            logger.info(f"Using requested provider: {provider.name}")
            return await provider.transcribe({"audio_path": opts["audio_path"]})

        # Try providers in priority order
        last_error = None
        failed_providers = []
        for prov in opts["providers"]:
            try:
                logger.info(f"Trying provider: {prov.name}")
                result = await prov.transcribe({"audio_path": opts["audio_path"]})
                logger.info(f"Transcription successful with {prov.name}")
                return result
            except Exception as error:
                logger.warning(f"Provider {prov.name} failed: {error}")
                last_error = error
                failed_providers.append({"provider": prov.name, "error": str(error)})
                continue

        # Build informative error message
        error_msg = f"All providers failed. Last error: {last_error}"
        hints = []
        for failed in failed_providers:
            error_lower = failed["error"].lower()
            if "401" in failed["error"] or "403" in failed["error"]:
                hints.append(f"• {failed['provider']}: Authentication failed. Check your API key.")
            elif "429" in failed["error"]:
                hints.append(f"• {failed['provider']}: Rate limit exceeded. Wait before retrying.")

        if hints:
            error_msg += "\n\nTroubleshooting hints:\n" + "\n".join(hints)

        raise Exception(error_msg)

    # Apply hooks if provided
    decorated_transcribe = (
        create_hook_chain(execute_transcribe, hooks) if hooks else execute_transcribe
    )

    return await decorated_transcribe({
        "audio_path": audio_path,
        "providers": providers,
        "provider": provider_name,
    })


class TranscriptionService:
    """TranscriptionService class wrapper for function-based API."""

    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """Initialize the transcription service.

        Args:
            options: Configuration dictionary
        """
        self.config = options or {}
        self.providers = initialize_providers(self.config)
        self.hooks = self.config.get("hooks", [])

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [p.name for p in self.providers]

    async def transcribe(
        self, audio_path: str, provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe an audio file.

        Args:
            audio_path: Path to audio file
            provider: Optional specific provider name

        Returns:
            Transcription result dictionary
        """
        return await transcribe({
            "audio_path": audio_path,
            "providers": self.providers,
            "provider": provider,
            "hooks": self.hooks,
        })

    def add_hook(self, hook: Dict[str, Callable]) -> None:
        """Add a hook to the transcription process.

        Args:
            hook: Hook dictionary with 'before' and/or 'after' keys
        """
        self.hooks.append(hook)

    def clear_hooks(self) -> None:
        """Remove all hooks."""
        self.hooks = []
