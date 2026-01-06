/**
 * WeaR Lang - Main Entry Point
 * A polyglot programming language friendly for beginners but powerful for professionals
 */

export { Token, TokenType, createToken } from './types/tokens';
export { LanguageConfig, KeywordMap, createReversedKeywordMap } from './types/config';
export * from './types/ast';

export { Lexer, tokenize } from './lexer/lexer';
export { Parser } from './parser/parser';
export { Interpreter } from './interpreter/interpreter';
export { Environment, RuntimeValue, WearFunction } from './interpreter/environment';
export { ErrorReporter, WearError } from './utils/error-reporter';
export { getLanguageConfig, getAvailableLanguages, registerLanguage, getDefaultLanguage } from './languages/loader';

import { Lexer } from './lexer/lexer';
import { Parser } from './parser/parser';
import { Interpreter } from './interpreter/interpreter';
import { ErrorReporter } from './utils/error-reporter';
import { LanguageConfig } from './types/config';
import { getLanguageConfig } from './languages/loader';

/**
 * Execution result interface
 */
export interface ExecutionResult {
  output: string[];
  errors: string[];
  success: boolean;
}

/**
 * WeaR Lang Runtime
 * High-level API for running WeaR code
 */
export class WearLang {
  private config: LanguageConfig;
  private errorReporter: ErrorReporter;
  private outputCallback: (text: string) => void;

  constructor(languageCode: string = 'en', outputCallback?: (text: string) => void) {
    this.config = getLanguageConfig(languageCode);
    this.errorReporter = new ErrorReporter();
    // Default to console.log if no callback provided (CLI compatibility)
    this.outputCallback = outputCallback || ((text: string) => console.log(text));
  }

  /**
   * Run WeaR source code
   */
  run(source: string): ExecutionResult {
    this.errorReporter.clear();
    this.errorReporter.setSource(source);

    // Create interpreter with output callback
    const interpreter = new Interpreter(this.errorReporter, this.outputCallback);

    // Tokenize
    const lexer = new Lexer(source, this.config, this.errorReporter);
    const tokens = lexer.tokenize();

    if (this.errorReporter.hasErrors()) {
      return {
        output: [],
        errors: [this.errorReporter.getFormattedErrors()],
        success: false,
      };
    }

    // Parse
    const parser = new Parser(tokens, this.errorReporter);
    const ast = parser.parse();

    if (this.errorReporter.hasErrors()) {
      return {
        output: [],
        errors: [this.errorReporter.getFormattedErrors()],
        success: false,
      };
    }

    // Interpret
    const output = interpreter.interpret(ast);

    if (this.errorReporter.hasErrors()) {
      return {
        output,
        errors: [this.errorReporter.getFormattedErrors()],
        success: false,
      };
    }

    return {
      output,
      errors: [],
      success: true,
    };
  }

  /**
   * Set a custom output callback (for browser use)
   */
  setOutputCallback(callback: (text: string) => void): void {
    this.outputCallback = callback;
  }

  /**
   * Change the language configuration
   */
  setLanguage(languageCode: string): void {
    this.config = getLanguageConfig(languageCode);
  }

  /**
   * Get current language name
   */
  getLanguageName(): string {
    return this.config.name;
  }
}

/**
 * Convenience function to run WeaR code
 */
export function run(source: string, languageCode: string = 'en'): string[] {
  const wear = new WearLang(languageCode);
  const result = wear.run(source);

  if (!result.success) {
    console.error(result.errors.join('\n'));
    return [];
  }

  return result.output;
}