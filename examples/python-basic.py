"""
Basic Python example - Function-based API

Run with: python examples/python-basic.py
"""

import asyncio
import os

from python.speech_to_text import transcribe, initialize_providers


async def main():
    # Initialize providers with configuration
    providers = initialize_providers({
        "inference_priority": ["openai", "groq"],
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "whisper_model": "whisper-large-v3",
    })

    # Transcribe an audio file
    result = await transcribe({
        "audio_path": "./path/to/audio.mp3",
        "providers": providers,
    })

    print(f"Transcription: {result['text']}")
    print(f"Provider: {result['provider']}")
    if result.get("language"):
        print(f"Language: {result['language']}")


if __name__ == "__main__":
    asyncio.run(main())
