/**
 * Speech-to-text transcription library.
 *
 * This library provides both function-based and class-based APIs for
 * audio transcription using multiple AI providers (OpenAI, Groq, HuggingFace, etc.).
 *
 * @example Function-based API
 * ```js
 * import { transcribe, initializeProviders } from '@link-assistant/speech-to-text';
 *
 * const providers = initializeProviders({
 *   inferencePriority: ['openai', 'groq'],
 *   openaiApiKey: process.env.OPENAI_API_KEY,
 *   groqApiKey: process.env.GROQ_API_KEY,
 * });
 *
 * const result = await transcribe({
 *   audioPath: './audio.mp3',
 *   providers,
 * });
 * console.log(result.text);
 * ```
 *
 * @example Class-based API
 * ```js
 * import { TranscriptionService } from '@link-assistant/speech-to-text';
 *
 * const service = new TranscriptionService({
 *   inferencePriority: ['openai', 'groq'],
 *   openaiApiKey: process.env.OPENAI_API_KEY,
 *   groqApiKey: process.env.GROQ_API_KEY,
 * });
 *
 * const result = await service.transcribe('./audio.mp3');
 * console.log(result.text);
 * ```
 *
 * @example With hooks/decorators
 * ```js
 * const service = new TranscriptionService({
 *   inferencePriority: ['openai'],
 *   openaiApiKey: process.env.OPENAI_API_KEY,
 *   hooks: [
 *     {
 *       before: async (options) => {
 *         console.log('Starting transcription...');
 *         return options;
 *       },
 *       after: async (result) => {
 *         console.log('Transcription completed!');
 *         return result;
 *       },
 *     },
 *   ],
 * });
 * ```
 */

// Core transcription functions
export {
  getAvailableProviders,
  initializeProviders,
  transcribe,
  TranscriptionService,
} from './transcription.js';

// Server functions
export { createApp, startServer } from './server.js';

// Provider classes (for advanced usage)
export {
  DeepInfraProvider,
  DeepSeekProvider,
  GroqProvider,
  HuggingFaceProvider,
  OpenAIProvider,
  OpenRouterProvider,
  PiAPIProvider,
} from './providers/index.js';
