"""OpenAI-compatible providers for transcription."""

from pathlib import Path
from typing import Any, Dict, List

from .base import BaseProvider


class OpenAICompatibleProvider(BaseProvider):
    """Base class for OpenAI-compatible transcription providers."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize OpenAI-compatible provider.

        Args:
            options: Configuration options
        """
        super().__init__(options)
        self.base_url = options.get("base_url", "")
        self.provider_name = options.get("provider_name", "openai-compatible")
        self.models_to_try = options.get(
            "models_to_try", ["whisper-1", "gpt-4o-transcribe", "whisper-large-v3"]
        )
        self.name = self.provider_name

    async def transcribe(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio using OpenAI-compatible API.

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

        # Try each model
        models = self.models_to_try.copy()
        if self.model not in models:
            models.insert(0, self.model)

        errors = []
        for model_name in models:
            print(f"  → Trying {self.name} with model {model_name}...")

            try:
                # Determine response format
                is_gpt4o = model_name.startswith("gpt-4o")
                response_format = "json" if is_gpt4o else "verbose_json"

                # Create form data
                data = aiohttp.FormData()
                data.add_field(
                    "file",
                    open(audio_path, "rb"),
                    filename=filename,
                    content_type=content_type,
                )
                data.add_field("model", model_name)
                data.add_field("response_format", response_format)

                headers = {"Authorization": f"Bearer {self.api_key}"}

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/audio/transcriptions",
                        headers=headers,
                        data=data,
                    ) as response:
                        if not response.ok:
                            error_text = await response.text()
                            raise Exception(f"{response.status} {error_text}")

                        result = await response.json()
                        print(f"  ✓ Success with {self.name} model {model_name}")

                        return {
                            "text": result.get("text", "").strip(),
                            "language": result.get("language"),
                            "duration": result.get("duration"),
                            "provider": self.name,
                        }

            except Exception as error:
                error_msg = str(error)[:100]
                print(f"  ✗ Failed with model {model_name}: {error_msg}...")
                errors.append({"model": model_name, "error": str(error)})

                if model_name != models[-1]:
                    continue

        # All models failed
        error_details = "; ".join([f"{e['model']}: {e['error']}" for e in errors])
        raise Exception(
            f"{self.name} transcription failed with all models. Attempts: {error_details}"
        )


class PiAPIProvider(OpenAICompatibleProvider):
    """PiAPI transcription provider."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize PiAPI provider."""
        options["base_url"] = "https://api.piapi.ai/v1"
        options["provider_name"] = "piapi"
        options["models_to_try"] = ["whisper-1", "gpt-4o-transcribe", "whisper-large-v3"]
        super().__init__(options)


class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter transcription provider."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize OpenRouter provider."""
        options["base_url"] = "https://openrouter.ai/api/v1"
        options["provider_name"] = "openrouter"
        options["models_to_try"] = ["whisper-1", "gpt-4o-transcribe", "whisper-large-v3"]
        super().__init__(options)


class DeepSeekProvider(OpenAICompatibleProvider):
    """DeepSeek transcription provider."""

    def __init__(self, options: Dict[str, Any]):
        """Initialize DeepSeek provider."""
        options["base_url"] = "https://api.deepseek.com/v1"
        options["provider_name"] = "deepseek"
        options["models_to_try"] = ["whisper-1", "gpt-4o-transcribe", "whisper-large-v3"]
        super().__init__(options)
