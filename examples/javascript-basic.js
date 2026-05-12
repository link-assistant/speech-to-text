/**
 * Basic JavaScript example - Function-based API
 *
 * Run with: node examples/javascript-basic.js
 */

import { transcribe, initializeProviders } from '../src/index.js';

async function main() {
  // Initialize providers with configuration
  const providers = initializeProviders({
    inferencePriority: ['openai', 'groq'],
    openaiApiKey: process.env.OPENAI_API_KEY,
    groqApiKey: process.env.GROQ_API_KEY,
    whisperModel: 'whisper-large-v3',
  });

  // Transcribe an audio file
  const result = await transcribe({
    audioPath: './path/to/audio.mp3',
    providers,
  });

  console.log('Transcription:', result.text);
  console.log('Provider:', result.provider);
  if (result.language) {
    console.log('Language:', result.language);
  }
}

main().catch(console.error);
