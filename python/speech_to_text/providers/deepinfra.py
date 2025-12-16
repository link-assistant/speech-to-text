"""DeepInfra provider for transcription."""

from pathlib import Path
from typing import Any, Dict

from .base import BaseProvider


class DeepInfraProvider(BaseProvider):
    """DeepInfra transcription provider."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize DeepInfra provider.

        Args:
            options: Configuration options
        """
        super().__init__(options)
        self.name = "deepinfra"
        self.model = options.get("model", "openai/whisper-large-v3")

    async def transcribe(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio using DeepInfra API.

        Args:
            options: Dictionary containing audio_path

        Returns:
            Transcription result dictionary
        """
        import aiohttp

        audio_path = Path(options["audio_path"])
        filename = audio_path.name

        # Determine MIME type
        ext = audio_path.suffix.lower()
        mime_types = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".m4a": "audio/m4a",
            ".ogg": "audio/ogg",
            ".flac": "audio/flac",
            ".webm": "audio/webm",
            ".mp4": "audio/mp4",
        }
        content_type = mime_types.get(ext, "audio/mpeg")

        # Create multipart form data
        data = aiohttp.FormData()
        data.add_field(
            "audio",
            open(audio_path, "rb"),
            filename=filename,
            content_type=content_type,
        )

        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.deepinfra.com/v1/inference/{self.model}",
                headers=headers,
                data=data,
            ) as response:
                if not response.ok:
                    error_text = await response.text()
                    raise Exception(
                        f"DeepInfra API error: {response.status} - {error_text}"
                    )

                result = await response.json()
                return {
                    "text": result.get("text", "").strip(),
                    "provider": self.name,
                }
