"""
Python example with class-based API and hooks

Run with: python examples/python-class.py
"""

import asyncio
import os

from python.speech_to_text import TranscriptionService


async def main():
    # Create service with hooks for logging
    service = TranscriptionService({
        "inference_priority": ["openai", "groq"],
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "hooks": [
            {
                "before": lambda opts: print(f"Starting transcription of {opts['audio_path']}...") or opts,
                "after": lambda res, opts: print("Transcription completed!") or res,
            },
        ],
    })

    # Check available providers
    print(f"Available providers: {service.get_available_providers()}")

    # Transcribe an audio file
    result = await service.transcribe("./path/to/audio.mp3")

    print(f"Transcription: {result['text']}")
    print(f"Provider: {result['provider']}")


if __name__ == "__main__":
    asyncio.run(main())
