/**
 * DeepInfra provider for speech-to-text transcription.
 */

import fs from 'fs';
import path from 'path';

export class DeepInfraProvider {
  constructor({ apiKey, model = 'openai/whisper-large-v3' }) {
    this.name = 'deepinfra';
    this.apiKey = apiKey;
    this.model = model;
  }

  async transcribe({ audioPath }) {
    const audioData = fs.readFileSync(audioPath);
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

    const formData = new FormData();
    const blob = new Blob([audioData], { type: contentType });
    formData.append('audio', blob, filename);

    const response = await fetch(
      `https://api.deepinfra.com/v1/inference/${this.model}`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `DeepInfra API error: ${response.status} - ${errorText}`
      );
    }

    const result = await response.json();
    return {
      text: result.text?.trim() || '',
      provider: this.name,
    };
  }
}
