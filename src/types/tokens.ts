/**
 * Token Types for WeaR Lang
 * Defines all possible token types that the lexer can produce
 */

export enum TokenType {
    // Literals
    NUMBER = 'NUMBER',
    STRING = 'STRING',
    IDENTIFIER = 'IDENTIFIER',

    // Keywords (mapped dynamically from language config)
    VAR = 'VAR',
    CONST = 'CONST',
    FUNCTION = 'FUNCTION',
    IF = 'IF',
    ELSE = 'ELSE',
    RETURN = 'RETURN',
    PRINT = 'PRINT',
    TRUE = 'TRUE',
    FALSE = 'FALSE',
    NULL = 'NULL',
    WHILE = 'WHILE',
    FOR = 'FOR',
    AND = 'AND',
    OR = 'OR',

    // Operators
    PLUS = 'PLUS',           // +
    MINUS = 'MINUS',         // -
    STAR = 'STAR',           // *
    SLASH = 'SLASH',         // /
    PERCENT = 'PERCENT',     // %

    // Comparison
    EQUAL = 'EQUAL',         // =
    EQUAL_EQUAL = 'EQUAL_EQUAL',   // ==
    BANG = 'BANG',           // !
    BANG_EQUAL = 'BANG_EQUAL',     // !=
    LESS = 'LESS',           // <
    LESS_EQUAL = 'LESS_EQUAL',     // <=
    GREATER = 'GREATER',     // >
    GREATER_EQUAL = 'GREATER_EQUAL', // >=

    // Delimiters
    LEFT_PAREN = 'LEFT_PAREN',     // (
    RIGHT_PAREN = 'RIGHT_PAREN',   // )
    LEFT_BRACE = 'LEFT_BRACE',     // {
    RIGHT_BRACE = 'RIGHT_BRACE',   // }
    LEFT_BRACKET = 'LEFT_BRACKET', // [
    RIGHT_BRACKET = 'RIGHT_BRACKET', // ]
    COMMA = 'COMMA',         // ,
    DOT = 'DOT',             // .
    COLON = 'COLON',         // :

    // Special
    NEWLINE = 'NEWLINE',
    EOF = 'EOF',
}

/**
 * Token interface with position tracking for error messages
 */
export interface Token {
    type: TokenType;
    lexeme: string;
    literal: string | number | boolean | null;
    line: number;
    column: number;
}

/**
 * Creates a new token
 */
export function createToken(
    type: TokenType,
    lexeme: string,
    literal: string | number | boolean | null,
    line: number,
    column: number
): Token {
    return { type, lexeme, literal, line, column };
}
