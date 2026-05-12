/**
 * Basic tests for speech-to-text library
 */

import { describe, it, expect } from 'test-anywhere';
import {
  initializeProviders,
  getAvailableProviders,
  TranscriptionService,
} from '../src/index.js';

describe('initializeProviders', () => {
  it('should return empty array when no API keys provided', () => {
    const providers = initializeProviders({});
    expect(Array.isArray(providers)).toBe(true);
    expect(providers.length).toBe(0);
  });

  it('should create provider when API key is provided with priority', () => {
    const providers = initializeProviders({
      inferencePriority: ['openai'],
      openaiApiKey: 'test-key',
    });
    expect(Array.isArray(providers)).toBe(true);
    expect(providers.length).toBe(1);
    expect(providers[0].name).toBe('openai');
  });

  it('should respect inference priority order', () => {
    const providers = initializeProviders({
      inferencePriority: ['groq', 'openai'],
      openaiApiKey: 'test-key',
      groqApiKey: 'test-key',
    });
    expect(Array.isArray(providers)).toBe(true);
    expect(providers.length).toBe(2);
    expect(providers[0].name).toBe('groq');
    expect(providers[1].name).toBe('openai');
  });
});

describe('getAvailableProviders', () => {
  it('should return empty array when no providers initialized', () => {
    const providers = initializeProviders({});
    const available = getAvailableProviders({ providers });
    expect(Array.isArray(available)).toBe(true);
    expect(available.length).toBe(0);
  });

  it('should return provider names when providers initialized', () => {
    const providers = initializeProviders({
      inferencePriority: ['openai', 'groq'],
      openaiApiKey: 'test-key',
      groqApiKey: 'test-key',
    });
    const available = getAvailableProviders({ providers });
    expect(Array.isArray(available)).toBe(true);
    expect(available.length).toBe(2);
    expect(available.includes('openai')).toBe(true);
    expect(available.includes('groq')).toBe(true);
  });
});

describe('TranscriptionService', () => {
  it('should create instance with empty config', () => {
    const service = new TranscriptionService({});
    expect(service instanceof TranscriptionService).toBe(true);
    expect(Array.isArray(service.providers)).toBe(true);
    expect(service.providers.length).toBe(0);
  });

  it('should create instance with providers', () => {
    const service = new TranscriptionService({
      inferencePriority: ['openai'],
      openaiApiKey: 'test-key',
    });
    expect(service instanceof TranscriptionService).toBe(true);
    expect(Array.isArray(service.providers)).toBe(true);
    expect(service.providers.length).toBe(1);
  });

  it('should support adding hooks', () => {
    const service = new TranscriptionService({
      inferencePriority: ['openai'],
      openaiApiKey: 'test-key',
    });
    service.addHook({
      before: async (options) => options,
      after: async (result) => result,
    });
    expect(Array.isArray(service.hooks)).toBe(true);
    expect(service.hooks.length).toBe(1);
  });

  it('should support clearing hooks', () => {
    const service = new TranscriptionService({
      inferencePriority: ['openai'],
      openaiApiKey: 'test-key',
    });
    service.addHook({
      before: async (options) => options,
    });
    service.clearHooks();
    expect(Array.isArray(service.hooks)).toBe(true);
    expect(service.hooks.length).toBe(0);
  });

  it('should return available providers', () => {
    const service = new TranscriptionService({
      inferencePriority: ['openai', 'groq'],
      openaiApiKey: 'test-key',
      groqApiKey: 'test-key',
    });
    const available = service.getAvailableProviders();
    expect(Array.isArray(available)).toBe(true);
    expect(available.length).toBe(2);
  });
});
