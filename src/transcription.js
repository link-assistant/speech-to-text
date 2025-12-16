/**
 * Core transcription functions with decorator support.
 */

import {
  DeepInfraProvider,
  DeepSeekProvider,
  GroqProvider,
  HuggingFaceProvider,
  OpenAIProvider,
  OpenRouterProvider,
  PiAPIProvider,
} from './providers/index.js';

/**
 * Provider registry mapping names to classes.
 */
const PROVIDER_CLASSES = {
  huggingface: HuggingFaceProvider,
  openai: OpenAIProvider,
  groq: GroqProvider,
  piapi: PiAPIProvider,
  openrouter: OpenRouterProvider,
  deepinfra: DeepInfraProvider,
  deepseek: DeepSeekProvider,
};

/**
 * Create hook chain for decorating functions.
 * @param {Function} fn - Original function to decorate
 * @param {Array<Function>} hooks - Array of hook functions
 * @returns {Function} Decorated function
 */
function createHookChain(fn, hooks = []) {
  if (!hooks || hooks.length === 0) {
    return fn;
  }

  return async (options) => {
    // Run before hooks
    let modifiedOptions = options;
    for (const hook of hooks) {
      if (hook.before) {
        modifiedOptions =
          (await hook.before(modifiedOptions)) || modifiedOptions;
      }
    }

    // Execute main function
    let result = await fn(modifiedOptions);

    // Run after hooks
    for (const hook of hooks) {
      if (hook.after) {
        result = (await hook.after(result, modifiedOptions)) || result;
      }
    }

    return result;
  };
}

/**
 * Initialize transcription providers based on configuration.
 * @param {Object} options - Configuration options
 * @param {Array<string>} options.inferencePriority - Provider priority order
 * @param {string} [options.huggingfaceApiKey] - HuggingFace API key
 * @param {string} [options.openaiApiKey] - OpenAI API key
 * @param {string} [options.groqApiKey] - Groq API key
 * @param {string} [options.piapiApiKey] - PiAPI API key
 * @param {string} [options.openrouterApiKey] - OpenRouter API key
 * @param {string} [options.deepinfraApiKey] - DeepInfra API key
 * @param {string} [options.deepseekApiKey] - DeepSeek API key
 * @param {string} [options.whisperModel] - Whisper model to use
 * @returns {Array<Object>} Array of initialized provider instances
 */
export function initializeProviders(options) {
  const providers = [];

  for (const providerName of options.inferencePriority || []) {
    const ProviderClass = PROVIDER_CLASSES[providerName];
    if (!ProviderClass) {
      console.warn(`Unknown provider: ${providerName}`);
      continue;
    }

    const apiKeyMap = {
      huggingface: options.huggingfaceApiKey,
      openai: options.openaiApiKey,
      groq: options.groqApiKey,
      piapi: options.piapiApiKey,
      openrouter: options.openrouterApiKey,
      deepinfra: options.deepinfraApiKey,
      deepseek: options.deepseekApiKey,
    };

    const apiKey = apiKeyMap[providerName];
    if (!apiKey) {
      console.log(`Skipping ${providerName}: no API key provided`);
      continue;
    }

    try {
      const provider = new ProviderClass({
        apiKey,
        model: options.whisperModel || 'whisper-large-v3',
      });
      providers.push(provider);
      console.log(`Provider ${providerName} initialized`);
    } catch (error) {
      console.warn(`Failed to initialize ${providerName}:`, error.message);
    }
  }

  return providers;
}

/**
 * Get list of available provider names.
 * @param {Object} options - Configuration options
 * @param {Array<Object>} options.providers - Array of provider instances
 * @returns {Array<string>} Array of provider names
 */
export function getAvailableProviders(options) {
  return (options.providers || []).map((p) => p.name);
}

/**
 * Core transcription function.
 * @param {Object} options - Transcription options
 * @param {string} options.audioPath - Path to audio file
 * @param {Array<Object>} options.providers - Array of provider instances
 * @param {string} [options.provider] - Specific provider to use
 * @param {Array<Function>} [options.hooks] - Hook functions for decoration
 * @returns {Promise<Object>} Transcription result
 */
export async function transcribe(options) {
  const { audioPath, providers, provider: providerName, hooks = [] } = options;

  if (!providers || providers.length === 0) {
    throw new Error('No transcription providers available');
  }

  // Create decorated transcribe function if hooks are present
  const executeTranscribe = async (opts) => {
    // If specific provider requested
    if (opts.provider) {
      const provider = opts.providers.find((p) => p.name === opts.provider);
      if (!provider) {
        throw new Error(`Provider not available: ${opts.provider}`);
      }
      console.log(`Using requested provider: ${provider.name}`);
      return await provider.transcribe({ audioPath: opts.audioPath });
    }

    // Try providers in priority order
    let lastError = null;
    const failedProviders = [];
    for (const prov of opts.providers) {
      try {
        console.log(`Trying provider: ${prov.name}`);
        const result = await prov.transcribe({ audioPath: opts.audioPath });
        console.log(`Transcription successful with ${prov.name}`);
        return result;
      } catch (error) {
        console.warn(`Provider ${prov.name} failed: ${error.message}`);
        lastError = error;
        failedProviders.push({ provider: prov.name, error: error.message });
        continue;
      }
    }

    // Build informative error message
    let errorMsg = `All providers failed. Last error: ${lastError?.message}`;
    const hints = [];
    for (const { provider: prov, error } of failedProviders) {
      if (error.includes('401') || error.includes('403')) {
        hints.push(`• ${prov}: Authentication failed. Check your API key.`);
      } else if (error.includes('429')) {
        hints.push(`• ${prov}: Rate limit exceeded. Wait before retrying.`);
      }
    }

    if (hints.length > 0) {
      errorMsg += `\n\nTroubleshooting hints:\n${hints.join('\n')}`;
    }

    throw new Error(errorMsg);
  };

  // Apply hooks if provided
  const decoratedTranscribe =
    hooks.length > 0
      ? createHookChain(executeTranscribe, hooks)
      : executeTranscribe;

  return await decoratedTranscribe({
    audioPath,
    providers,
    provider: providerName,
  });
}

/**
 * TranscriptionService class wrapper for function-based API.
 */
export class TranscriptionService {
  constructor(options = {}) {
    this.config = options;
    this.providers = initializeProviders(options);
    this.hooks = options.hooks || [];
  }

  getAvailableProviders() {
    return getAvailableProviders({ providers: this.providers });
  }

  transcribe(audioPath, providerName = null) {
    return transcribe({
      audioPath,
      providers: this.providers,
      provider: providerName,
      hooks: this.hooks,
    });
  }

  /**
   * Add a hook to the transcription process.
   * @param {Object} hook - Hook object with before/after methods
   */
  addHook(hook) {
    this.hooks.push(hook);
  }

  /**
   * Remove all hooks.
   */
  clearHooks() {
    this.hooks = [];
  }
}
