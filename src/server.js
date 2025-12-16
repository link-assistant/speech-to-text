/**
 * Express server for the transcription service.
 */

import cors from 'cors';
import express from 'express';
import fs from 'node:fs';
import multer from 'multer';
import os from 'node:os';
import { TranscriptionService } from './transcription.js';

/**
 * Create Express app with transcription endpoints.
 * @param {Object} options - Server configuration options
 * @param {Object} options.config - Transcription service configuration
 * @param {Array<Function>} [options.hooks] - Hooks for transcription process
 * @returns {Object} Express app instance
 */
export function createApp(options = {}) {
  const app = express();
  const upload = multer({ dest: os.tmpdir() });

  // Middleware
  app.use(cors());
  app.use(express.json());

  // Initialize service
  const config = { ...options.config, hooks: options.hooks || [] };
  const service = new TranscriptionService(config);

  /**
   * Health check endpoint.
   */
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      providers: service.getAvailableProviders(),
    });
  });

  /**
   * List available providers.
   */
  app.get('/providers', (req, res) => {
    res.json({
      providers: service.getAvailableProviders(),
    });
  });

  /**
   * Transcribe an audio file.
   */
  app.post('/transcribe', upload.single('file'), async (req, res) => {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    if (service.providers.length === 0) {
      return res.status(503).json({
        error:
          'No transcription providers available. Check API key configuration.',
      });
    }

    const provider = req.query.provider || null;

    try {
      const result = await service.transcribe(req.file.path, provider);

      res.json({
        text: result.text,
        subtitles: result.subtitles || null,
        language: result.language || null,
        provider: result.provider,
      });
    } catch (error) {
      console.error('Transcription failed:', error);
      res.status(500).json({ error: error.message });
    } finally {
      // Clean up temp file
      try {
        fs.unlinkSync(req.file.path);
      } catch (_e) {
        // Ignore cleanup errors
      }
    }
  });

  return app;
}

/**
 * Start the transcription server.
 * @param {Object} options - Server options
 * @param {number} [options.port=8000] - Port to listen on
 * @param {Object} options.config - Transcription service configuration
 * @param {Array<Function>} [options.hooks] - Hooks for transcription process
 * @returns {Object} HTTP server instance
 */
export function startServer(options = {}) {
  const port = options.port || 8000;
  const app = createApp(options);

  return app.listen(port, () => {
    console.log(`Transcription service listening on port ${port}`);
    const service = new TranscriptionService(options.config);
    console.log(
      `Available providers: ${service.getAvailableProviders().join(', ') || 'none'}`
    );
  });
}

export default { createApp, startServer };
