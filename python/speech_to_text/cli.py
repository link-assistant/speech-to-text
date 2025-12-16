#!/usr/bin/env python3
"""CLI tool for speech-to-text transcription.

Supports two modes:
1. One-time transcription: transcribe a single audio file
2. Server mode (--serve): Run as REST API server
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from .transcription import TranscriptionService


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="speech-to-text",
        description="Speech-to-text transcription CLI tool",
    )

    parser.add_argument("audio_file", nargs="?", help="Audio file to transcribe")
    parser.add_argument(
        "--serve", action="store_true", help="Run as REST API server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", 8000)),
        help="Port for server mode (default: 8000)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Specific provider to use (openai, groq, huggingface, etc.)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Output file for transcription result",
    )
    parser.add_argument(
        "--inference-priority",
        type=str,
        default=os.getenv(
            "INFERENCE_PRIORITY",
            "openai,groq,deepinfra,piapi,openrouter,huggingface,deepseek",
        ),
        help="Provider priority order (comma-separated)",
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default=os.getenv("WHISPER_MODEL", "whisper-large-v3"),
        help="Whisper model to use",
    )
    parser.add_argument(
        "--openai-api-key",
        type=str,
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key",
    )
    parser.add_argument(
        "--groq-api-key",
        type=str,
        default=os.getenv("GROQ_API_KEY"),
        help="Groq API key",
    )
    parser.add_argument(
        "--huggingface-api-key",
        type=str,
        default=os.getenv("HUGGINGFACE_API_KEY"),
        help="HuggingFace API key",
    )
    parser.add_argument(
        "--piapi-api-key",
        type=str,
        default=os.getenv("PIAPI_API_KEY"),
        help="PiAPI API key",
    )
    parser.add_argument(
        "--openrouter-api-key",
        type=str,
        default=os.getenv("OPENROUTER_API_KEY"),
        help="OpenRouter API key",
    )
    parser.add_argument(
        "--deepinfra-api-key",
        type=str,
        default=os.getenv("DEEPINFRA_API_KEY"),
        help="DeepInfra API key",
    )
    parser.add_argument(
        "--deepseek-api-key",
        type=str,
        default=os.getenv("DEEPSEEK_API_KEY"),
        help="DeepSeek API key",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s 0.1.0"
    )

    return parser


async def transcribe_file(args: argparse.Namespace) -> None:
    """Transcribe a single audio file."""
    if not args.audio_file:
        print("Error: Audio file path is required", file=sys.stderr)
        print("Usage: speech-to-text [options] <audio-file>", file=sys.stderr)
        print("       speech-to-text --serve [options]", file=sys.stderr)
        sys.exit(1)

    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    # Initialize service
    config = {
        "inference_priority": args.inference_priority.split(","),
        "whisper_model": args.whisper_model,
        "openai_api_key": args.openai_api_key,
        "groq_api_key": args.groq_api_key,
        "huggingface_api_key": args.huggingface_api_key,
        "piapi_api_key": args.piapi_api_key,
        "openrouter_api_key": args.openrouter_api_key,
        "deepinfra_api_key": args.deepinfra_api_key,
        "deepseek_api_key": args.deepseek_api_key,
    }

    service = TranscriptionService(config)

    if not service.providers:
        print(
            "Error: No transcription providers available. "
            "Please configure API keys.",
            file=sys.stderr,
        )
        print(
            "Set environment variables or use CLI options: "
            "--openai-api-key, --groq-api-key, etc.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.verbose:
        providers_str = ", ".join(service.get_available_providers())
        print(f"Available providers: {providers_str}")
        print(f"Transcribing: {audio_path}")
        if args.provider:
            print(f"Using provider: {args.provider}")

    try:
        result = await service.transcribe(str(audio_path), args.provider)

        if args.output:
            Path(args.output).write_text(result["text"], encoding="utf-8")
            print(f"Transcription saved to: {args.output}")
        else:
            print(result["text"])

        if args.verbose:
            print(f"\nProvider: {result.get('provider')}")
            if result.get("language"):
                print(f"Language: {result['language']}")
            if result.get("duration"):
                print(f"Duration: {result['duration']}s")

    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


def start_server(args: argparse.Namespace) -> None:
    """Start the transcription server."""
    print("Starting transcription server...")

    # Set environment variables for the server
    os.environ["PORT"] = str(args.port)
    if args.inference_priority:
        os.environ["INFERENCE_PRIORITY"] = args.inference_priority
    if args.whisper_model:
        os.environ["WHISPER_MODEL"] = args.whisper_model
    if args.openai_api_key:
        os.environ["OPENAI_API_KEY"] = args.openai_api_key
    if args.groq_api_key:
        os.environ["GROQ_API_KEY"] = args.groq_api_key
    if args.huggingface_api_key:
        os.environ["HUGGINGFACE_API_KEY"] = args.huggingface_api_key
    if args.piapi_api_key:
        os.environ["PIAPI_API_KEY"] = args.piapi_api_key
    if args.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = args.openrouter_api_key
    if args.deepinfra_api_key:
        os.environ["DEEPINFRA_API_KEY"] = args.deepinfra_api_key
    if args.deepseek_api_key:
        os.environ["DEEPSEEK_API_KEY"] = args.deepseek_api_key

    # Import and run uvicorn
    import uvicorn

    from .api import app

    uvicorn.run(app, host="0.0.0.0", port=args.port)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.serve:
        start_server(args)
    else:
        asyncio.run(transcribe_file(args))


if __name__ == "__main__":
    main()
