/**
 * Lexer for WeaR Lang
 * Tokenizes source code with support for dynamic keyword mapping
 */

import { Token, TokenType, createToken } from '../types/tokens';
import { LanguageConfig, KeywordMap, createReversedKeywordMap } from '../types/config';
import { ErrorReporter } from '../utils/error-reporter';

/**
 * Maps canonical keyword names to token types
 */
const KEYWORD_TO_TOKEN: Record<keyof KeywordMap, TokenType> = {
    var: TokenType.VAR,
    const: TokenType.CONST,
    function: TokenType.FUNCTION,
    return: TokenType.RETURN,
    if: TokenType.IF,
    else: TokenType.ELSE,
    while: TokenType.WHILE,
    for: TokenType.FOR,
    and: TokenType.AND,
    or: TokenType.OR,
    print: TokenType.PRINT,
    true: TokenType.TRUE,
    false: TokenType.FALSE,
    null: TokenType.NULL,
};

export class Lexer {
    private source: string;
    private tokens: Token[] = [];
    private start: number = 0;
    private current: number = 0;
    private line: number = 1;
    private column: number = 1;
    private lineStart: number = 0;

    private keywordMap: Map<string, keyof KeywordMap>;
    private errorReporter: ErrorReporter;

    constructor(source: string, config: LanguageConfig, errorReporter?: ErrorReporter) {
        this.source = source;
        this.keywordMap = createReversedKeywordMap(config);
        this.errorReporter = errorReporter || new ErrorReporter();
        this.errorReporter.setSource(source);
    }

    /**
     * Tokenize the entire source code
     */
    tokenize(): Token[] {
        while (!this.isAtEnd()) {
            this.start = this.current;
            this.scanToken();
        }

        // Add EOF token
        this.tokens.push(createToken(
            TokenType.EOF,
            '',
            null,
            this.line,
            this.column
        ));

        return this.tokens;
    }

    /**
     * Scan a single token
     */
    private scanToken(): void {
        const char = this.advance();

        switch (char) {
            // Single-character tokens
            case '(': this.addToken(TokenType.LEFT_PAREN); break;
            case ')': this.addToken(TokenType.RIGHT_PAREN); break;
            case '{': this.addToken(TokenType.LEFT_BRACE); break;
            case '}': this.addToken(TokenType.RIGHT_BRACE); break;
            case '[': this.addToken(TokenType.LEFT_BRACKET); break;
            case ']': this.addToken(TokenType.RIGHT_BRACKET); break;
            case ',': this.addToken(TokenType.COMMA); break;
            case '.': this.addToken(TokenType.DOT); break;
            case ':': this.addToken(TokenType.COLON); break;
            case '+': this.addToken(TokenType.PLUS); break;
            case '-': this.addToken(TokenType.MINUS); break;
            case '*': this.addToken(TokenType.STAR); break;
            case '%': this.addToken(TokenType.PERCENT); break;

            // Two-character tokens
            case '!':
                this.addToken(this.match('=') ? TokenType.BANG_EQUAL : TokenType.BANG);
                break;
            case '=':
                this.addToken(this.match('=') ? TokenType.EQUAL_EQUAL : TokenType.EQUAL);
                break;
            case '<':
                this.addToken(this.match('=') ? TokenType.LESS_EQUAL : TokenType.LESS);
                break;
            case '>':
                this.addToken(this.match('=') ? TokenType.GREATER_EQUAL : TokenType.GREATER);
                break;

            // Slash (could be division or comment)
            case '/':
                if (this.match('/')) {
                    // Single-line comment - skip to end of line
                    while (this.peek() !== '\n' && !this.isAtEnd()) {
                        this.advance();
                    }
                } else {
                    this.addToken(TokenType.SLASH);
                }
                break;

            // Whitespace
            case ' ':
            case '\r':
            case '\t':
                // Ignore whitespace
                break;

            // Newline
            case '\n':
                this.line++;
                this.lineStart = this.current;
                this.column = 1;
                break;

            // String literals
            case '"':
                this.scanString();
                break;

            default:
                if (this.isDigit(char)) {
                    this.scanNumber();
                } else if (this.isAlpha(char)) {
                    this.scanIdentifier();
                } else {
                    this.errorReporter.reportError(
                        `Unexpected character: '${char}'`,
                        this.line,
                        this.getColumn(this.start)
                    );
                }
        }
    }

    /**
     * Scan a string literal
     */
    private scanString(): void {
        const startLine = this.line;
        const startColumn = this.getColumn(this.start);

        while (this.peek() !== '"' && !this.isAtEnd()) {
            if (this.peek() === '\n') {
                this.line++;
                this.lineStart = this.current + 1;
            }
            this.advance();
        }

        if (this.isAtEnd()) {
            this.errorReporter.reportError(
                'Unterminated string',
                startLine,
                startColumn,
                'a closing "',
                'end of file'
            );
            return;
        }

        // Consume the closing "
        this.advance();

        // Extract the string value (without quotes)
        const value = this.source.substring(this.start + 1, this.current - 1);
        this.addToken(TokenType.STRING, value);
    }

    /**
     * Scan a number literal
     */
    private scanNumber(): void {
        while (this.isDigit(this.peek())) {
            this.advance();
        }

        // Look for decimal part
        if (this.peek() === '.' && this.isDigit(this.peekNext())) {
            // Consume the '.'
            this.advance();

            while (this.isDigit(this.peek())) {
                this.advance();
            }
        }

        const value = parseFloat(this.source.substring(this.start, this.current));
        this.addToken(TokenType.NUMBER, value);
    }

    /**
     * Scan an identifier or keyword
     */
    private scanIdentifier(): void {
        while (this.isAlphaNumeric(this.peek())) {
            this.advance();
        }

        const text = this.source.substring(this.start, this.current);

        // Check if it's a keyword
        const canonical = this.keywordMap.get(text);
        if (canonical) {
            const tokenType = KEYWORD_TO_TOKEN[canonical];

            // Handle literal keywords
            if (tokenType === TokenType.TRUE) {
                this.addToken(tokenType, true);
            } else if (tokenType === TokenType.FALSE) {
                this.addToken(tokenType, false);
            } else if (tokenType === TokenType.NULL) {
                this.addToken(tokenType, null);
            } else {
                this.addToken(tokenType);
            }
        } else {
            this.addToken(TokenType.IDENTIFIER);
        }
    }

    // ============================================================
    // Helper Methods
    // ============================================================

    private isAtEnd(): boolean {
        return this.current >= this.source.length;
    }

    private advance(): string {
        const char = this.source.charAt(this.current);
        this.current++;
        this.column++;
        return char;
    }

    private peek(): string {
        if (this.isAtEnd()) return '\0';
        return this.source.charAt(this.current);
    }

    private peekNext(): string {
        if (this.current + 1 >= this.source.length) return '\0';
        return this.source.charAt(this.current + 1);
    }

    private match(expected: string): boolean {
        if (this.isAtEnd()) return false;
        if (this.source.charAt(this.current) !== expected) return false;
        this.current++;
        this.column++;
        return true;
    }

    private isDigit(char: string): boolean {
        return char >= '0' && char <= '9';
    }

    private isAlpha(char: string): boolean {
        return (char >= 'a' && char <= 'z') ||
            (char >= 'A' && char <= 'Z') ||
            char === '_';
    }

    private isAlphaNumeric(char: string): boolean {
        return this.isAlpha(char) || this.isDigit(char);
    }

    private getColumn(position: number): number {
        return position - this.lineStart + 1;
    }

    private addToken(type: TokenType, literal: string | number | boolean | null = null): void {
        const lexeme = this.source.substring(this.start, this.current);
        this.tokens.push(createToken(
            type,
            lexeme,
            literal,
            this.line,
            this.getColumn(this.start)
        ));
    }

    /**
     * Get the error reporter
     */
    getErrorReporter(): ErrorReporter {
        return this.errorReporter;
    }
}

/**
 * Convenience function to tokenize source code
 */
export function tokenize(source: string, config: LanguageConfig): Token[] {
    const lexer = new Lexer(source, config);
    return lexer.tokenize();
}
