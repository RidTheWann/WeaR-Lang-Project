/**
 * Parser for WeaR Lang
 * Recursive descent parser with panic mode recovery
 */

import { Token, TokenType } from '../types/tokens';
import * as AST from '../types/ast';
import { ErrorReporter } from '../utils/error-reporter';

/**
 * Custom error for parser synchronization
 */
class ParseError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ParseError';
    }
}

export class Parser {
    private tokens: Token[];
    private current: number = 0;
    private errorReporter: ErrorReporter;

    constructor(tokens: Token[], errorReporter?: ErrorReporter) {
        this.tokens = tokens;
        this.errorReporter = errorReporter || new ErrorReporter();
    }

    /**
     * Parse all tokens into an AST
     */
    parse(): AST.Program {
        const statements: AST.Statement[] = [];

        while (!this.isAtEnd()) {
            try {
                const stmt = this.declaration();
                if (stmt) {
                    statements.push(stmt);
                }
            } catch (error) {
                if (error instanceof ParseError) {
                    this.synchronize();
                } else {
                    throw error;
                }
            }
        }

        return AST.createProgram(statements);
    }

    // ============================================================
    // Declarations
    // ============================================================

    private declaration(): AST.Statement | null {
        try {
            if (this.check(TokenType.VAR) || this.check(TokenType.CONST)) {
                return this.varDeclaration();
            }
            if (this.check(TokenType.FUNCTION)) {
                return this.functionDeclaration();
            }
            return this.statement();
        } catch (error) {
            if (error instanceof ParseError) {
                this.synchronize();
                return null;
            }
            throw error;
        }
    }

    private varDeclaration(): AST.VarDeclaration {
        const isConst = this.check(TokenType.CONST);
        const keyword = this.advance(); // consume 'var' or 'const'

        const nameToken = this.consume(TokenType.IDENTIFIER, 'a variable name');
        const identifier = AST.createIdentifier(nameToken.lexeme, nameToken.line, nameToken.column);

        let value: AST.Expression | null = null;
        if (this.match(TokenType.EQUAL)) {
            value = this.expression();
        }

        return {
            type: 'VarDeclaration',
            identifier,
            value,
            isConst,
            line: keyword.line,
            column: keyword.column,
        };
    }

    private functionDeclaration(): AST.FunctionDeclaration {
        const keyword = this.advance(); // consume 'function'

        const nameToken = this.consume(TokenType.IDENTIFIER, 'a function name');
        const name = AST.createIdentifier(nameToken.lexeme, nameToken.line, nameToken.column);

        this.consume(TokenType.LEFT_PAREN, "'('");

        const params: AST.Identifier[] = [];
        if (!this.check(TokenType.RIGHT_PAREN)) {
            do {
                const paramToken = this.consume(TokenType.IDENTIFIER, 'a parameter name');
                params.push(AST.createIdentifier(paramToken.lexeme, paramToken.line, paramToken.column));
            } while (this.match(TokenType.COMMA));
        }

        this.consume(TokenType.RIGHT_PAREN, "')'");

        const body = this.blockStatement();

        return {
            type: 'FunctionDeclaration',
            name,
            params,
            body,
            line: keyword.line,
            column: keyword.column,
        };
    }

    // ============================================================
    // Statements
    // ============================================================

    private statement(): AST.Statement {
        if (this.check(TokenType.IF)) {
            return this.ifStatement();
        }
        if (this.check(TokenType.WHILE)) {
            return this.whileStatement();
        }
        if (this.check(TokenType.RETURN)) {
            return this.returnStatement();
        }
        if (this.check(TokenType.PRINT)) {
            return this.printStatement();
        }
        if (this.check(TokenType.LEFT_BRACE)) {
            return this.blockStatement();
        }
        return this.expressionStatement();
    }

    private ifStatement(): AST.IfStatement {
        const keyword = this.advance(); // consume 'if'

        this.consume(TokenType.LEFT_PAREN, "'('");
        const condition = this.expression();
        this.consume(TokenType.RIGHT_PAREN, "')'");

        const consequent = this.blockStatement();

        let alternate: AST.BlockStatement | AST.IfStatement | null = null;
        if (this.match(TokenType.ELSE)) {
            if (this.check(TokenType.IF)) {
                alternate = this.ifStatement();
            } else {
                alternate = this.blockStatement();
            }
        }

        return {
            type: 'IfStatement',
            condition,
            consequent,
            alternate,
            line: keyword.line,
            column: keyword.column,
        };
    }

    private whileStatement(): AST.WhileStatement {
        const keyword = this.advance(); // consume 'while'

        this.consume(TokenType.LEFT_PAREN, "'('");
        const condition = this.expression();
        this.consume(TokenType.RIGHT_PAREN, "')'");

        const body = this.blockStatement();

        return {
            type: 'WhileStatement',
            condition,
            body,
            line: keyword.line,
            column: keyword.column,
        };
    }

    private returnStatement(): AST.ReturnStatement {
        const keyword = this.advance(); // consume 'return'

        let argument: AST.Expression | null = null;
        if (!this.check(TokenType.RIGHT_BRACE) && !this.isAtEnd()) {
            // Check if there's an expression on the same conceptual line
            if (!this.check(TokenType.EOF)) {
                argument = this.expression();
            }
        }

        return {
            type: 'ReturnStatement',
            argument,
            line: keyword.line,
            column: keyword.column,
        };
    }

    private printStatement(): AST.PrintStatement {
        const keyword = this.advance(); // consume 'print'
        const argument = this.expression();

        return {
            type: 'PrintStatement',
            argument,
            line: keyword.line,
            column: keyword.column,
        };
    }

    private blockStatement(): AST.BlockStatement {
        const brace = this.consume(TokenType.LEFT_BRACE, "'{'");
        const statements: AST.Statement[] = [];

        while (!this.check(TokenType.RIGHT_BRACE) && !this.isAtEnd()) {
            const stmt = this.declaration();
            if (stmt) {
                statements.push(stmt);
            }
        }

        this.consume(TokenType.RIGHT_BRACE, "'}'");

        return {
            type: 'BlockStatement',
            body: statements,
            line: brace.line,
            column: brace.column,
        };
    }

    private expressionStatement(): AST.ExpressionStatement {
        const expr = this.expression();
        return {
            type: 'ExpressionStatement',
            expression: expr,
            line: expr.line,
            column: expr.column,
        };
    }

    // ============================================================
    // Expressions (Precedence Climbing)
    // ============================================================

    private expression(): AST.Expression {
        return this.assignment();
    }

    private assignment(): AST.Expression {
        const expr = this.or();

        if (this.match(TokenType.EQUAL)) {
            const equals = this.previous();
            const value = this.assignment();

            if (expr.type === 'Identifier') {
                return {
                    type: 'AssignmentExpression',
                    assignee: expr,
                    value,
                    line: expr.line,
                    column: expr.column,
                };
            }

            this.errorReporter.reportError(
                'Invalid assignment target',
                equals.line,
                equals.column
            );
        }

        return expr;
    }

    private or(): AST.Expression {
        let expr = this.and();

        while (this.match(TokenType.OR)) {
            const operator = this.previous();
            const right = this.and();
            expr = {
                type: 'BinaryExpression',
                operator: 'or',
                left: expr,
                right,
                line: operator.line,
                column: operator.column,
            };
        }

        return expr;
    }

    private and(): AST.Expression {
        let expr = this.equality();

        while (this.match(TokenType.AND)) {
            const operator = this.previous();
            const right = this.equality();
            expr = {
                type: 'BinaryExpression',
                operator: 'and',
                left: expr,
                right,
                line: operator.line,
                column: operator.column,
            };
        }

        return expr;
    }

    private equality(): AST.Expression {
        let expr = this.comparison();

        while (this.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)) {
            const operator = this.previous();
            const right = this.comparison();
            expr = {
                type: 'BinaryExpression',
                operator: operator.lexeme,
                left: expr,
                right,
                line: operator.line,
                column: operator.column,
            };
        }

        return expr;
    }

    private comparison(): AST.Expression {
        let expr = this.term();

        while (this.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL)) {
            const operator = this.previous();
            const right = this.term();
            expr = {
                type: 'BinaryExpression',
                operator: operator.lexeme,
                left: expr,
                right,
                line: operator.line,
                column: operator.column,
            };
        }

        return expr;
    }

    private term(): AST.Expression {
        let expr = this.factor();

        while (this.match(TokenType.PLUS, TokenType.MINUS)) {
            const operator = this.previous();
            const right = this.factor();
            expr = {
                type: 'BinaryExpression',
                operator: operator.lexeme,
                left: expr,
                right,
                line: operator.line,
                column: operator.column,
            };
        }

        return expr;
    }

    private factor(): AST.Expression {
        let expr = this.unary();

        while (this.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT)) {
            const operator = this.previous();
            const right = this.unary();
            expr = {
                type: 'BinaryExpression',
                operator: operator.lexeme,
                left: expr,
                right,
                line: operator.line,
                column: operator.column,
            };
        }

        return expr;
    }

    private unary(): AST.Expression {
        if (this.match(TokenType.BANG, TokenType.MINUS)) {
            const operator = this.previous();
            const right = this.unary();
            return {
                type: 'UnaryExpression',
                operator: operator.lexeme,
                argument: right,
                line: operator.line,
                column: operator.column,
            };
        }

        return this.call();
    }

    private call(): AST.Expression {
        let expr = this.primary();

        while (true) {
            if (this.match(TokenType.LEFT_PAREN)) {
                expr = this.finishCall(expr);
            } else if (this.match(TokenType.LEFT_BRACKET)) {
                // Index access: array[index]
                const index = this.expression();
                this.consume(TokenType.RIGHT_BRACKET, "']' after index");
                expr = {
                    type: 'IndexExpression',
                    object: expr,
                    index,
                    line: expr.line,
                    column: expr.column,
                } as AST.IndexExpression;
            } else {
                break;
            }
        }

        return expr;
    }

    private finishCall(callee: AST.Expression): AST.CallExpression {
        const args: AST.Expression[] = [];

        if (!this.check(TokenType.RIGHT_PAREN)) {
            do {
                args.push(this.expression());
            } while (this.match(TokenType.COMMA));
        }

        const paren = this.consume(TokenType.RIGHT_PAREN, "')' after arguments");

        return {
            type: 'CallExpression',
            callee,
            arguments: args,
            line: callee.line,
            column: callee.column,
        };
    }

    private primary(): AST.Expression {
        if (this.match(TokenType.FALSE)) {
            const token = this.previous();
            return AST.createBooleanLiteral(false, token.line, token.column);
        }
        if (this.match(TokenType.TRUE)) {
            const token = this.previous();
            return AST.createBooleanLiteral(true, token.line, token.column);
        }
        if (this.match(TokenType.NULL)) {
            const token = this.previous();
            return AST.createNullLiteral(token.line, token.column);
        }
        if (this.match(TokenType.NUMBER)) {
            const token = this.previous();
            return AST.createNumericLiteral(token.literal as number, token.line, token.column);
        }
        if (this.match(TokenType.STRING)) {
            const token = this.previous();
            return AST.createStringLiteral(token.literal as string, token.line, token.column);
        }
        if (this.match(TokenType.IDENTIFIER)) {
            const token = this.previous();
            return AST.createIdentifier(token.lexeme, token.line, token.column);
        }
        if (this.match(TokenType.LEFT_PAREN)) {
            const expr = this.expression();
            this.consume(TokenType.RIGHT_PAREN, "')'");
            return expr;
        }
        if (this.match(TokenType.LEFT_BRACKET)) {
            // Array literal: [a, b, c]
            return this.parseArrayLiteral();
        }

        // Error handling
        const token = this.peek();
        this.errorReporter.reportUnexpectedToken(token, 'an expression');
        throw new ParseError(`Unexpected token: ${token.lexeme}`);
    }

    /**
     * Parse an array literal: [element1, element2, ...]
     */
    private parseArrayLiteral(): AST.ArrayLiteral {
        const bracket = this.previous(); // we already consumed '['
        const elements: AST.Expression[] = [];

        if (!this.check(TokenType.RIGHT_BRACKET)) {
            do {
                elements.push(this.expression());
            } while (this.match(TokenType.COMMA));
        }

        this.consume(TokenType.RIGHT_BRACKET, "']' to close array");

        return {
            type: 'ArrayLiteral',
            elements,
            line: bracket.line,
            column: bracket.column,
        };
    }

    // ============================================================
    // Panic Mode Recovery
    // ============================================================

    /**
     * Synchronize after an error by advancing to a statement boundary
     */
    private synchronize(): void {
        this.advance();

        while (!this.isAtEnd()) {
            // Check if we're at a statement boundary
            switch (this.peek().type) {
                case TokenType.FUNCTION:
                case TokenType.VAR:
                case TokenType.CONST:
                case TokenType.IF:
                case TokenType.WHILE:
                case TokenType.FOR:
                case TokenType.RETURN:
                case TokenType.PRINT:
                    return;
            }

            this.advance();
        }
    }

    // ============================================================
    // Helper Methods
    // ============================================================

    private match(...types: TokenType[]): boolean {
        for (const type of types) {
            if (this.check(type)) {
                this.advance();
                return true;
            }
        }
        return false;
    }

    private check(type: TokenType): boolean {
        if (this.isAtEnd()) return false;
        return this.peek().type === type;
    }

    private advance(): Token {
        if (!this.isAtEnd()) this.current++;
        return this.previous();
    }

    private isAtEnd(): boolean {
        return this.peek().type === TokenType.EOF;
    }

    private peek(): Token {
        return this.tokens[this.current];
    }

    private previous(): Token {
        return this.tokens[this.current - 1];
    }

    private consume(type: TokenType, expected: string): Token {
        if (this.check(type)) return this.advance();

        const token = this.peek();
        this.errorReporter.reportUnexpectedToken(token, expected);
        throw new ParseError(`Expected ${expected}`);
    }

    /**
     * Get the error reporter
     */
    getErrorReporter(): ErrorReporter {
        return this.errorReporter;
    }
}
