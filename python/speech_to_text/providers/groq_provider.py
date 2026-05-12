"""Groq provider for transcription."""

from pathlib import Path
from typing import Any, Dict

from .base import BaseProvider


class GroqProvider(BaseProvider):
    """Groq Whisper transcription provider."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize Groq provider.

        Args:
            options: Configuration options
        """
        super().__init__(options)
        self.name = "groq"
        self.model = options.get("model", "whisper-large-v3")

    async def transcribe(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio using Groq API.

        Args:
            options: Dictionary containing audio_path

        Returns:
            Transcription result dictionary
        """
        try:
            from groq import AsyncGroq
        except ImportError:
            raise ImportError("groq package is required. Install with: pip install groq")

        client = AsyncGroq(api_key=self.api_key)
        audio_path = Path(options["audio_path"])

        with open(audio_path, "rb") as audio_file:
            result = await client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="verbose_json",
            )

        return {
            "text": result.text.strip(),
            "language": result.language if hasattr(result, "language") else None,
            "duration": result.duration if hasattr(result, "duration") else None,
            "provider": self.name,
        }
