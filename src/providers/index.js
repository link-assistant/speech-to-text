/**
 * Provider exports for transcription services.
 */

export { DeepInfraProvider } from './deepinfra.js';

/**
 * HuggingFace provider for transcription.
 */
import fs from 'node:fs';
import path from 'node:path';

export class HuggingFaceProvider {
  constructor({ apiKey, model = 'whisper-large-v3' }) {
    this.name = 'huggingface';
    this.apiKey = apiKey;
    this.model = model;

    const models = {
      'whisper-large-v3': 'openai/whisper-large-v3',
      'whisper-large-v2': 'openai/whisper-large-v2',
      'whisper-medium': 'openai/whisper-medium',
      'whisper-small': 'openai/whisper-small',
      'whisper-base': 'openai/whisper-base',
      'whisper-tiny': 'openai/whisper-tiny',
    };

    const modelId = models[model] || model;
    this.apiUrl = `https://api-inference.huggingface.co/models/${modelId}`;
  }

  async transcribe({ audioPath }) {
    const audioData = fs.readFileSync(audioPath);

    const response = await fetch(this.apiUrl, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        'Content-Type': 'application/octet-stream',
      },
      body: audioData,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`HuggingFace API error: ${response.status} - ${error}`);
    }

    const result = await response.json();
    const text = typeof result === 'string' ? result : result.text || '';

    return {
      text: text.trim(),
      provider: this.name,
    };
  }
}

/**
 * OpenAI provider for transcription.
 */
export class OpenAIProvider {
  constructor({ apiKey, model = 'whisper-1' }) {
    this.name = 'openai';
    this.apiKey = apiKey;
    this.model = model;
  }

  async transcribe({ audioPath }) {
    const { default: OpenAI, toFile } = await import('openai');
    const client = new OpenAI({ apiKey: this.apiKey });

    const audioBuffer = fs.readFileSync(audioPath);
    const audioFile = await toFile(audioBuffer, path.basename(audioPath));

    const result = await client.audio.transcriptions.create({
      model: this.model,
      file: audioFile,
      response_format: 'verbose_json',
    });

    return {
      text: result.text.trim(),
      language: result.language,
      duration: result.duration,
      provider: this.name,
    };
  }
}

/**
 * Groq provider for transcription.
 */
export class GroqProvider {
  constructor({ apiKey, model = 'whisper-large-v3' }) {
    this.name = 'groq';
    this.apiKey = apiKey;
    this.model = model;
  }

  async transcribe({ audioPath }) {
    const { default: Groq } = await import('groq-sdk');
    const client = new Groq({ apiKey: this.apiKey });

    const audioBuffer = fs.readFileSync(audioPath);
    const audioFile = new File([audioBuffer], path.basename(audioPath), {
      type: 'audio/mpeg',
    });

    const result = await client.audio.transcriptions.create({
      model: this.model,
      file: audioFile,
      response_format: 'verbose_json',
    });

    return {
      text: result.text.trim(),
      language: result.language,
      duration: result.duration,
      provider: this.name,
    };
  }
}

/**
 * Base class for OpenAI-compatible providers.
 */
export class OpenAICompatibleProvider {
  constructor({
    apiKey,
    model,
    baseUrl,
    providerName,
    modelsToTry = ['whisper-1', 'gpt-4o-transcribe', 'whisper-large-v3'],
  }) {
    this.name = providerName;
    this.apiKey = apiKey;
    this.model = model;
    this.baseUrl = baseUrl;
    this.modelsToTry = modelsToTry;
  }

  async transcribe({ audioPath }) {
    const models = this.modelsToTry.slice();
    if (!models.includes(this.model)) {
      models.unshift(this.model);
    }

    const audioBuffer = fs.readFileSync(audioPath);
    const filename = path.basename(audioPath);

    const ext = path.extname(audioPath).toLowerCase();
    const mimeTypes = {
      '.mp3': 'audio/mpeg',
      '.wav': 'audio/wav',
      '.m4a': 'audio/m4a',
      '.ogg': 'audio/ogg',
      '.flac': 'audio/flac',
      '.webm': 'audio/webm',
      '.mp4': 'audio/mp4',
      '.mpeg': 'audio/mpeg',
      '.mpga': 'audio/mpeg',
    };
    const contentType = mimeTypes[ext] || 'audio/mpeg';

    const errors = [];
    for (const modelName of models) {
      console.log(`  → Trying ${this.name} with model ${modelName}...`);

      try {
        const isGpt4oModel = modelName.startsWith('gpt-4o');
        const responseFormat = isGpt4oModel ? 'json' : 'verbose_json';

        const formData = new FormData();
        const blob = new Blob([audioBuffer], { type: contentType });
        formData.append('file', blob, filename);
        formData.append('model', modelName);
        formData.append('response_format', responseFormat);

        const response = await fetch(`${this.baseUrl}/audio/transcriptions`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
          },
          body: formData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`${response.status} ${errorText}`);
        }

        const result = await response.json();

        console.log(`  ✓ Success with ${this.name} model ${modelName}`);
        return {
          text: result.text.trim(),
          language: result.language,
          duration: result.duration,
          provider: this.name,
        };
      } catch (error) {
        const errorMsg = error.message || String(error);
        const shortError = errorMsg.substring(0, 100);
        console.warn(`  ✗ Failed with model ${modelName}: ${shortError}...`);
        errors.push({ model: modelName, error: errorMsg });

        if (modelName !== models[models.length - 1]) {
          continue;
        }
      }
    }

    const errorDetails = errors.map((e) => `${e.model}: ${e.error}`).join('; ');
    throw new Error(
      `${this.name} transcription failed with all models. Attempts: ${errorDetails}`
    );
  }
}

/**
 * PiAPI provider for transcription.
 */
export class PiAPIProvider extends OpenAICompatibleProvider {
  constructor({ apiKey, model = 'whisper-1' }) {
    super({
      apiKey,
      model,
      baseUrl: 'https://api.piapi.ai/v1',
      providerName: 'piapi',
      modelsToTry: ['whisper-1', 'gpt-4o-transcribe', 'whisper-large-v3'],
    });
  }
}

/**
 * OpenRouter provider for transcription.
 */
export class OpenRouterProvider extends OpenAICompatibleProvider {
  constructor({ apiKey, model = 'whisper-1' }) {
    super({
      apiKey,
      model,
      baseUrl: 'https://openrouter.ai/api/v1',
      providerName: 'openrouter',
      modelsToTry: ['whisper-1', 'gpt-4o-transcribe', 'whisper-large-v3'],
    });
  }
}

/**
 * DeepSeek provider for transcription.
 */
export class DeepSeekProvider extends OpenAICompatibleProvider {
  constructor({ apiKey, model = 'whisper-1' }) {
    super({
      apiKey,
      model,
      baseUrl: 'https://api.deepseek.com/v1',
      providerName: 'deepseek',
      modelsToTry: ['whisper-1', 'gpt-4o-transcribe', 'whisper-large-v3'],
    });
  }
}
