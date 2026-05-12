"""FastAPI application for the transcription service."""

import logging
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from .transcription import TranscriptionService

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Transcription Service",
    description="Audio transcription service using multiple inference providers",
    version="0.1.0",
)

# Global service instance
_service: Optional[TranscriptionService] = None


def get_service() -> TranscriptionService:
    """Get or create the transcription service instance."""
    global _service
    if _service is None:
        # Load from environment variables
        config = {
            "inference_priority": os.getenv(
                "INFERENCE_PRIORITY",
                "openai,groq,deepinfra,piapi,openrouter,huggingface,deepseek",
            ).split(","),
            "whisper_model": os.getenv("WHISPER_MODEL", "whisper-large-v3"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "groq_api_key": os.getenv("GROQ_API_KEY"),
            "huggingface_api_key": os.getenv("HUGGINGFACE_API_KEY"),
            "piapi_api_key": os.getenv("PIAPI_API_KEY"),
            "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
            "deepinfra_api_key": os.getenv("DEEPINFRA_API_KEY"),
            "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
        }
        _service = TranscriptionService(config)
    return _service


class TranscriptionResponse(BaseModel):
    """Response model for transcription results."""

    text: str
    subtitles: Optional[str] = None
    language: Optional[str] = None
    provider: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    providers: list


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    service = get_service()
    return HealthResponse(
        status="ok",
        providers=service.get_available_providers(),
    )


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_endpoint(
    file: UploadFile = File(...),
    provider: Optional[str] = Query(None, description="Specific provider to use"),
):
    """Transcribe an audio file.

    Upload an audio file and receive the transcription.
    Supported formats: mp3, wav, mp4, m4a, ogg, flac, etc.
    """
    service = get_service()

    if not service.providers:
        raise HTTPException(
            status_code=503,
            detail="No transcription providers available. Check API key configuration.",
        )

    # Save uploaded file to temp location
    suffix = os.path.splitext(file.filename)[1] if file.filename else ".mp3"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await service.transcribe(tmp_path, provider)
        return TranscriptionResponse(
            text=result.get("text", ""),
            subtitles=result.get("subtitles"),
            language=result.get("language"),
            provider=result.get("provider"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Transcription failed")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.get("/providers")
async def list_providers():
    """List available transcription providers."""
    service = get_service()
    return {"providers": service.get_available_providers()}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return app


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
