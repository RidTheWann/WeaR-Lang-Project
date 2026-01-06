/**
 * Language Configuration Loader for WeaR Lang
 * Loads language configurations from JSON files
 */

import { LanguageConfig } from '../types/config';
import enConfig from './en.json';
import idConfig from './id.json';

// Available language configurations
const languages: Map<string, LanguageConfig> = new Map([
    ['en', enConfig as LanguageConfig],
    ['id', idConfig as LanguageConfig]
]);

/**
 * Get a language configuration by code
 */
export function getLanguageConfig(code: string): LanguageConfig {
    const config = languages.get(code.toLowerCase());
    if (!config) {
        throw new Error(`Language configuration not found for code: ${code}. Available: ${Array.from(languages.keys()).join(', ')}`);
    }
    return config;
}

/**
 * Get all available language codes
 */
export function getAvailableLanguages(): string[] {
    return Array.from(languages.keys());
}

/**
 * Register a custom language configuration
 */
export function registerLanguage(config: LanguageConfig): void {
    languages.set(config.code.toLowerCase(), config);
}

/**
 * Get default language (English)
 */
export function getDefaultLanguage(): LanguageConfig {
    return enConfig as LanguageConfig;
}
