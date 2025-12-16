# Speech-to-Text Transcription Library

A comprehensive speech-to-text transcription library available in both JavaScript and Python, with support for multiple AI providers and flexible deployment options.

## Features

- **Multi-provider Support**: OpenAI, Groq, HuggingFace, DeepInfra, PiAPI, OpenRouter, DeepSeek
- **Function-based and Class-based APIs**: Choose the style that fits your needs
- **Decorator/Hook Support**: Easily extend and customize transcription logic
- **CLI Tools**: Command-line interfaces for both one-time transcriptions and server mode
- **REST API Server**: Run as a standalone service with `--serve` option
- **Docker Images**: Pre-configured containers for easy deployment
- **Single Options Argument**: All functions and methods use a single options object for easy maintenance

## Installation

### JavaScript/Node.js

```bash
npm install @link-assistant/speech-to-text
```

Global CLI install:

```bash
npm install -g @link-assistant/speech-to-text
```

### Python

```bash
pip install speech-to-text
```

## Quick Start

### JavaScript Library

```javascript
import { TranscriptionService } from '@link-assistant/speech-to-text';

const service = new TranscriptionService({
  inferencePriority: ['openai', 'groq'],
  openaiApiKey: process.env.OPENAI_API_KEY,
  groqApiKey: process.env.GROQ_API_KEY,
});

const result = await service.transcribe('./audio.mp3');
console.log(result.text);
```

### Python Library

```python
import asyncio
from speech_to_text import TranscriptionService

async def main():
    service = TranscriptionService({
        "inference_priority": ["openai", "groq"],
        "openai_api_key": "your-key",
        "groq_api_key": "your-key",
    })
    result = await service.transcribe("./audio.mp3")
    print(result["text"])

asyncio.run(main())
```

### CLI Usage

One-time transcription:

```bash
speech-to-text audio.mp3 --openai-api-key YOUR_KEY
```

Server mode:

```bash
speech-to-text --serve --port 8000
```

## Hook/Decorator Support

Both implementations support hooks for extending functionality:

```javascript
// JavaScript
const service = new TranscriptionService({
  inferencePriority: ['openai'],
  openaiApiKey: process.env.OPENAI_API_KEY,
  hooks: [
    {
      before: async (options) => {
        console.log('Starting...');
        return options;
      },
      after: async (result) => {
        console.log('Done!');
        return result;
      },
    },
  ],
});
```

```python
# Python
service = TranscriptionService({
    "inference_priority": ["openai"],
    "openai_api_key": "your-key",
    "hooks": [
        {
            "before": lambda opts: print("Starting...") or opts,
            "after": lambda res, opts: print("Done!") or res,
        },
    ],
})
```

## Configuration

### JavaScript (with lino-arguments)

The JavaScript CLI uses [lino-arguments](https://github.com/link-foundation/lino-arguments) for unified configuration. Create a `.lenv` file:

```
OPENAI_API_KEY: your-key-here
GROQ_API_KEY: your-key-here
INFERENCE_PRIORITY: openai,groq,huggingface
PORT: 8000
```

### Python (with environment variables)

```bash
export OPENAI_API_KEY=your-key
export GROQ_API_KEY=your-key
export INFERENCE_PRIORITY=openai,groq,huggingface
```

## Docker Deployment

### JavaScript

```bash
docker build -t speech-to-text-js .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key speech-to-text-js
```

### Python

```bash
cd python
docker build -t speech-to-text-py .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key speech-to-text-py
```

## REST API

When running in server mode (`--serve`), the following endpoints are available:

- `GET /health` - Health check and list available providers
- `POST /transcribe` - Upload audio file for transcription
- `GET /providers` - List available providers

Example:

```bash
curl -X POST http://localhost:8000/transcribe -F "file=@audio.mp3"
```

## Supported Providers

- **OpenAI**: Whisper API
- **Groq**: Fast Whisper inference
- **HuggingFace**: Free tier available
- **DeepInfra**: Cost-effective option
- **PiAPI**: OpenAI-compatible
- **OpenRouter**: Multi-model gateway
- **DeepSeek**: Alternative provider

## API Reference

See the [examples](./examples) directory for more usage patterns.

## Development

### JavaScript

```bash
npm install
npm test
npm run lint
npm run check
```

### Python

```bash
cd python
pip install -e ".[dev]"
pytest
```

## License

Unlicense - Public Domain

## Acknowledgments

This library was extracted from the [sales-audit-agent](https://github.com/link-assistant/sales-audit-agent) project.
