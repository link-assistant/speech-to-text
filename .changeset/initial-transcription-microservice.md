---
'@link-assistant/speech-to-text': minor
---

Initial implementation of speech-to-text transcription microservice

- Add library callable from JavaScript with function-based and class-based APIs
- Add CLI tool for one-time transcription (globally installable via NPM)
- Add CLI tool with --serve option for REST API server mode
- Add Docker image support for containerized deployment
- Integrate lino-arguments for configuration management
- Implement function-based architecture with class wrapper for extensibility
- Add hook/decorator support for before/after execution logic
- Support multiple providers: OpenAI, Groq, HuggingFace, DeepInfra, PiAPI, OpenRouter, DeepSeek
- Include comprehensive examples for both function-based and class-based usage
