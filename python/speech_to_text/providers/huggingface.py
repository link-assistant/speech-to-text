"""HuggingFace provider for transcription."""

from pathlib import Path
from typing import Any, Dict

from .base import BaseProvider


class HuggingFaceProvider(BaseProvider):
    """HuggingFace Whisper transcription provider."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize HuggingFace provider.

        Args:
            options: Configuration options
        """
        super().__init__(options)
        self.name = "huggingface"
        self.model = options.get("model", "whisper-large-v3")

        models = {
            "whisper-large-v3": "openai/whisper-large-v3",
            "whisper-large-v2": "openai/whisper-large-v2",
            "whisper-medium": "openai/whisper-medium",
            "whisper-small": "openai/whisper-small",
            "whisper-base": "openai/whisper-base",
            "whisper-tiny": "openai/whisper-tiny",
        }

        model_id = models.get(self.model, self.model)
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    async def transcribe(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio using HuggingFace API.

        Args:
            options: Dictionary containing audio_path

        Returns:
            Transcription result dictionary
        """
        import aiohttp

        audio_path = Path(options["audio_path"])

        with open(audio_path, "rb") as f:
            audio_data = f.read()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/octet-stream",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url, headers=headers, data=audio_data
            ) as response:
                if not response.ok:
                    error_text = await response.text()
                    raise Exception(
                        f"HuggingFace API error: {response.status} - {error_text}"
                    )

                result = await response.json()
                text = result if isinstance(result, str) else result.get("text", "")

                return {
                    "text": text.strip(),
                    "provider": self.name,
                }
