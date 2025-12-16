/**
 * JavaScript example with class-based API and hooks
 *
 * Run with: node examples/javascript-class.js
 */

import { TranscriptionService } from '../src/index.js';

async function main() {
  // Create service with hooks for logging
  const service = new TranscriptionService({
    inferencePriority: ['openai', 'groq'],
    openaiApiKey: process.env.OPENAI_API_KEY,
    groqApiKey: process.env.GROQ_API_KEY,
    hooks: [
      {
        before: (options) => {
          console.log(`Starting transcription of ${options.audioPath}...`);
          return options;
        },
        after: (result) => {
          console.log('Transcription completed!');
          return result;
        },
      },
    ],
  });

  // Check available providers
  console.log('Available providers:', service.getAvailableProviders());

  // Transcribe an audio file
  const result = await service.transcribe('./path/to/audio.mp3');

  console.log('Transcription:', result.text);
  console.log('Provider:', result.provider);
}

main().catch(console.error);
