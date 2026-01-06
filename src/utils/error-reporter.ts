/**
 * Friendly Error Reporter for WeaR Lang
 * Generates user-friendly error messages with context
 */

import { Token, TokenType } from '../types/tokens';

export interface WearError {
    message: string;
    line: number;
    column: number;
    friendlyMessage: string;
    sourceSnippet?: string;
}

/**
 * Error Reporter class for collecting and formatting errors
 */
export class ErrorReporter {
    private errors: WearError[] = [];
    private source: string = '';
    private sourceLines: string[] = [];

    /**
     * Set the source code for snippet extraction
     */
    setSource(source: string): void {
        this.source = source;
        this.sourceLines = source.split('\n');
    }

    /**
     * Report an error with a friendly message
     */
    reportError(
        message: string,
        line: number,
        column: number,
        expected?: string,
        found?: string
    ): void {
        let friendlyMessage = `❌ I found an error on line ${line}`;

        if (column > 0) {
            friendlyMessage += `, column ${column}`;
        }
        friendlyMessage += '.\n';

        if (expected && found) {
            friendlyMessage += `   I was expecting ${expected}, but found '${found}' instead.\n`;
        } else if (expected) {
            friendlyMessage += `   I was expecting ${expected}.\n`;
        } else {
            friendlyMessage += `   ${message}\n`;
        }

        // Add source snippet if available
        let sourceSnippet: string | undefined;
        if (this.sourceLines.length >= line && line > 0) {
            const sourceLine = this.sourceLines[line - 1];
            sourceSnippet = `\n   ${line} | ${sourceLine}\n`;

            // Add pointer to the error column
            if (column > 0) {
                const padding = ' '.repeat(String(line).length + 3 + column - 1);
                sourceSnippet += `${padding}^\n`;
            }
        }

        const error: WearError = {
            message,
            line,
            column,
            friendlyMessage: friendlyMessage + (sourceSnippet || ''),
            sourceSnippet
        };

        this.errors.push(error);
    }

    /**
     * Report an unexpected token error
     */
    reportUnexpectedToken(token: Token, expected?: string): void {
        const found = token.type === TokenType.EOF ? 'end of file' : token.lexeme;
        this.reportError(
            `Unexpected token: ${token.lexeme}`,
            token.line,
            token.column,
            expected,
            found
        );
    }

    /**
     * Report a syntax error
     */
    reportSyntaxError(message: string, line: number, column: number): void {
        this.reportError(message, line, column);
    }

    /**
     * Report a runtime error
     */
    reportRuntimeError(message: string, line: number, column: number): void {
        const friendlyMessage =
            `🔥 Runtime error on line ${line}:\n` +
            `   ${message}\n`;

        this.errors.push({
            message,
            line,
            column,
            friendlyMessage
        });
    }

    /**
     * Check if there are any errors
     */
    hasErrors(): boolean {
        return this.errors.length > 0;
    }

    /**
     * Get all collected errors
     */
    getErrors(): WearError[] {
        return [...this.errors];
    }

    /**
     * Get all error messages formatted for display
     */
    getFormattedErrors(): string {
        return this.errors.map(e => e.friendlyMessage).join('\n');
    }

    /**
     * Clear all errors
     */
    clear(): void {
        this.errors = [];
    }

    /**
     * Get error count
     */
    count(): number {
        return this.errors.length;
    }
}

// Singleton instance for convenient usage
export const errorReporter = new ErrorReporter();
