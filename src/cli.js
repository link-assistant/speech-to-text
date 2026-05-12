#!/usr/bin/env node

/**
 * CLI tool for speech-to-text transcription.
 *
 * Supports two modes:
 * 1. One-time transcription: transcribe a single audio file
 * 2. Server mode (--serve): Run as REST API server
 */

import fs from 'node:fs';
import { makeConfig } from 'lino-arguments';
import { TranscriptionService } from './transcription.js';
import { startServer } from './server.js';

/**
 * Main CLI function.
 */
async function main() {
  const config = makeConfig({
    yargs: ({ yargs, getenv }) =>
      yargs
        .scriptName('speech-to-text')
        .usage('$0 [options] <audio-file>')
        .option('serve', {
          type: 'boolean',
          description: 'Run as REST API server',
          default: false,
        })
        .option('port', {
          type: 'number',
          description: 'Port for server mode',
          default: getenv('PORT', 8000),
        })
        .option('provider', {
          type: 'string',
          description:
            'Specific provider to use (openai, groq, huggingface, etc.)',
          default: null,
        })
        .option('output', {
          type: 'string',
          alias: 'o',
          description: 'Output file for transcription result',
          default: null,
        })
        .option('inference-priority', {
          type: 'array',
          description: 'Provider priority order',
          default: getenv('INFERENCE_PRIORITY', [
            'openai',
            'groq',
            'deepinfra',
            'piapi',
            'openrouter',
            'huggingface',
            'deepseek',
          ]),
        })
        .option('whisper-model', {
          type: 'string',
          description: 'Whisper model to use',
          default: getenv('WHISPER_MODEL', 'whisper-large-v3'),
        })
        .option('openai-api-key', {
          type: 'string',
          description: 'OpenAI API key',
          default: getenv('OPENAI_API_KEY'),
        })
        .option('groq-api-key', {
          type: 'string',
          description: 'Groq API key',
          default: getenv('GROQ_API_KEY'),
        })
        .option('huggingface-api-key', {
          type: 'string',
          description: 'HuggingFace API key',
          default: getenv('HUGGINGFACE_API_KEY'),
        })
        .option('piapi-api-key', {
          type: 'string',
          description: 'PiAPI API key',
          default: getenv('PIAPI_API_KEY'),
        })
        .option('openrouter-api-key', {
          type: 'string',
          description: 'OpenRouter API key',
          default: getenv('OPENROUTER_API_KEY'),
        })
        .option('deepinfra-api-key', {
          type: 'string',
          description: 'DeepInfra API key',
          default: getenv('DEEPINFRA_API_KEY'),
        })
        .option('deepseek-api-key', {
          type: 'string',
          description: 'DeepSeek API key',
          default: getenv('DEEPSEEK_API_KEY'),
        })
        .option('verbose', {
          type: 'boolean',
          alias: 'v',
          description: 'Enable verbose logging',
          default: false,
        })
        .help()
        .alias('help', 'h')
        .version()
        .alias('version', 'V'),
  });

  // Server mode
  if (config.serve) {
    console.log('Starting transcription server...');
    startServer({
      port: config.port,
      config: {
        inferencePriority: config.inferencePriority,
        whisperModel: config.whisperModel,
        openaiApiKey: config.openaiApiKey,
        groqApiKey: config.groqApiKey,
        huggingfaceApiKey: config.huggingfaceApiKey,
        piapiApiKey: config.piapiApiKey,
        openrouterApiKey: config.openrouterApiKey,
        deepinfraApiKey: config.deepinfraApiKey,
        deepseekApiKey: config.deepseekApiKey,
      },
    });
    return;
  }

  // One-time transcription mode
  const audioFile = config._[0];
  if (!audioFile) {
    console.error('Error: Audio file path is required');
    console.error('Usage: speech-to-text [options] <audio-file>');
    console.error('       speech-to-text --serve [options]');
    process.exit(1);
  }

  if (!fs.existsSync(audioFile)) {
    console.error(`Error: File not found: ${audioFile}`);
    process.exit(1);
  }

  // Initialize service
  const service = new TranscriptionService({
    inferencePriority: config.inferencePriority,
    whisperModel: config.whisperModel,
    openaiApiKey: config.openaiApiKey,
    groqApiKey: config.groqApiKey,
    huggingfaceApiKey: config.huggingfaceApiKey,
    piapiApiKey: config.piapiApiKey,
    openrouterApiKey: config.openrouterApiKey,
    deepinfraApiKey: config.deepinfraApiKey,
    deepseekApiKey: config.deepseekApiKey,
  });

  if (service.providers.length === 0) {
    console.error(
      'Error: No transcription providers available. Please configure API keys.'
    );
    console.error(
      'Set environment variables or use CLI options: --openai-api-key, --groq-api-key, etc.'
    );
    process.exit(1);
  }

  if (config.verbose) {
    console.log(
      `Available providers: ${service.getAvailableProviders().join(', ')}`
    );
    console.log(`Transcribing: ${audioFile}`);
    if (config.provider) {
      console.log(`Using provider: ${config.provider}`);
    }
  }

  try {
    const result = await service.transcribe(audioFile, config.provider);

    if (config.output) {
      fs.writeFileSync(config.output, result.text, 'utf8');
      console.log(`Transcription saved to: ${config.output}`);
    } else {
      console.log(result.text);
    }

    if (config.verbose) {
      console.log(`\nProvider: ${result.provider}`);
      if (result.language) {
        console.log(`Language: ${result.language}`);
      }
      if (result.duration) {
        console.log(`Duration: ${result.duration}s`);
      }
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error(`Fatal error: ${error.message}`);
  if (error.stack) {
    console.error(error.stack);
  }
  process.exit(1);
});
