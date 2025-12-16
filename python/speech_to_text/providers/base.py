"""Base provider class for transcription services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProvider(ABC):
    """Base class for transcription providers."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize the provider.

        Args:
            options: Configuration options including api_key and model
        """
        self.name: str = "base"
        self.api_key: Optional[str] = options.get("api_key")
        self.model: str = options.get("model", "whisper-large-v3")

    def initialize(self) -> bool:
        """Check if provider can be initialized.

        Returns:
            True if provider is ready, False otherwise
        """
        return self.api_key is not None

    @abstractmethod
    async def transcribe(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe an audio file.

        Args:
            options: Transcription options including audio_path

        Returns:
            Dictionary with transcription results
        """
        pass
