"""OpenAI provider for transcription."""

from pathlib import Path
from typing import Any, Dict

from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI Whisper transcription provider."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize OpenAI provider.

        Args:
            options: Configuration options
        """
        super().__init__(options)
        self.name = "openai"
        self.model = options.get("model", "whisper-1")

    async def transcribe(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper API.

        Args:
            options: Dictionary containing audio_path

        Returns:
            Transcription result dictionary
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

        client = AsyncOpenAI(api_key=self.api_key)
        audio_path = Path(options["audio_path"])

        with open(audio_path, "rb") as audio_file:
            result = await client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="verbose_json",
            )

        return {
            "text": result.text.strip(),
            "language": result.language,
            "duration": result.duration,
            "provider": self.name,
        }
