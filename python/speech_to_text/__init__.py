"""
Speech-to-text transcription library.

This library provides both function-based and class-based APIs for
audio transcription using multiple AI providers (OpenAI, Groq, HuggingFace, etc.).

Example (Function-based API):
    >>> from speech_to_text import transcribe, initialize_providers
    >>> providers = initialize_providers({
    ...     'inference_priority': ['openai', 'groq'],
    ...     'openai_api_key': 'your-key',
    ...     'groq_api_key': 'your-key',
    ... })
    >>> result = transcribe({'audio_path': './audio.mp3', 'providers': providers})
    >>> print(result['text'])

Example (Class-based API):
    >>> from speech_to_text import TranscriptionService
    >>> service = TranscriptionService({
    ...     'inference_priority': ['openai', 'groq'],
    ...     'openai_api_key': 'your-key',
    ...     'groq_api_key': 'your-key',
    ... })
    >>> result = service.transcribe('./audio.mp3')
    >>> print(result['text'])

Example (With hooks/decorators):
    >>> service = TranscriptionService({
    ...     'inference_priority': ['openai'],
    ...     'openai_api_key': 'your-key',
    ...     'hooks': [
    ...         {
    ...             'before': lambda opts: print('Starting...') or opts,
    ...             'after': lambda res, opts: print('Done!') or res,
    ...         },
    ...     ],
    ... })
"""

from .transcription import (
    TranscriptionService,
    get_available_providers,
    initialize_providers,
    transcribe,
)

__all__ = [
    "TranscriptionService",
    "transcribe",
    "initialize_providers",
    "get_available_providers",
]

__version__ = "0.1.0"
