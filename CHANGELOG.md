# Changelog

## 0.2.0

### Minor Changes

- f54258f: Initial implementation of speech-to-text transcription microservice
  - Add library callable from JavaScript with function-based and class-based APIs
  - Add CLI tool for one-time transcription (globally installable via NPM)
  - Add CLI tool with --serve option for REST API server mode
  - Add Docker image support for containerized deployment
  - Integrate lino-arguments for configuration management
  - Implement function-based architecture with class wrapper for extensibility
  - Add hook/decorator support for before/after execution logic
  - Support multiple providers: OpenAI, Groq, HuggingFace, DeepInfra, PiAPI, OpenRouter, DeepSeek
  - Include comprehensive examples for both function-based and class-based usage

## 0.1.0

### Minor Changes

- 65d76dc: Initial template setup with complete AI-driven development pipeline

  Features:
  - Multi-runtime support for Node.js, Bun, and Deno
  - Universal testing with test-anywhere framework
  - Automated release workflow with changesets
  - GitHub Actions CI/CD pipeline with 9 test combinations
  - Code quality tools: ESLint + Prettier with Husky pre-commit hooks
  - Package manager agnostic design

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
