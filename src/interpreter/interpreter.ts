/**
 * Interpreter for WeaR Lang
 * Tree-walking interpreter that executes the AST
 */

import * as AST from '../types/ast';
import { Environment, RuntimeValue, WearFunction } from './environment';
import { ErrorReporter } from '../utils/error-reporter';

/**
 * Custom error for return statements (control flow)
 */
class ReturnValue extends Error {
    value: RuntimeValue;

    constructor(value: RuntimeValue) {
        super('Return');
        this.value = value;
    }
}

export class Interpreter {
    private globalEnv: Environment;
    private currentEnv: Environment;
    private errorReporter: ErrorReporter;
    private output: string[] = [];
    private outputCallback: (text: string) => void;

    constructor(errorReporter?: ErrorReporter, outputCallback?: (text: string) => void) {
        this.globalEnv = new Environment();
        this.currentEnv = this.globalEnv;
        this.errorReporter = errorReporter || new ErrorReporter();
        // Default to console.log if no callback provided (CLI compatibility)
        this.outputCallback = outputCallback || ((text: string) => console.log(text));
    }

    /**
     * Interpret a program AST
     */
    interpret(program: AST.Program): string[] {
        this.output = [];

        try {
            for (const statement of program.body) {
                this.executeStatement(statement);
            }
        } catch (error) {
            if (error instanceof Error && !(error instanceof ReturnValue)) {
                this.errorReporter.reportRuntimeError(error.message, 0, 0);
            }
        }

        return this.output;
    }

    /**
     * Execute a statement
     */
    private executeStatement(stmt: AST.Statement): void {
        switch (stmt.type) {
            case 'VarDeclaration':
                this.executeVarDeclaration(stmt);
                break;
            case 'FunctionDeclaration':
                this.executeFunctionDeclaration(stmt);
                break;
            case 'IfStatement':
                this.executeIfStatement(stmt);
                break;
            case 'WhileStatement':
                this.executeWhileStatement(stmt);
                break;
            case 'ReturnStatement':
                this.executeReturnStatement(stmt);
                break;
            case 'PrintStatement':
                this.executePrintStatement(stmt);
                break;
            case 'BlockStatement':
                this.executeBlockStatement(stmt, new Environment(this.currentEnv));
                break;
            case 'ExpressionStatement':
                this.evaluate(stmt.expression);
                break;
        }
    }

    private executeVarDeclaration(stmt: AST.VarDeclaration): void {
        const value = stmt.value ? this.evaluate(stmt.value) : null;
        this.currentEnv.define(stmt.identifier.name, value, stmt.isConst);
    }

    private executeFunctionDeclaration(stmt: AST.FunctionDeclaration): void {
        const func: WearFunction = {
            type: 'function',
            name: stmt.name.name,
            params: stmt.params.map(p => p.name),
            body: stmt.body,
            closure: this.currentEnv,
        };
        this.currentEnv.define(stmt.name.name, func);
    }

    private executeIfStatement(stmt: AST.IfStatement): void {
        const condition = this.evaluate(stmt.condition);

        if (this.isTruthy(condition)) {
            this.executeBlockStatement(stmt.consequent, new Environment(this.currentEnv));
        } else if (stmt.alternate) {
            if (stmt.alternate.type === 'IfStatement') {
                this.executeIfStatement(stmt.alternate);
            } else {
                this.executeBlockStatement(stmt.alternate, new Environment(this.currentEnv));
            }
        }
    }

    private executeWhileStatement(stmt: AST.WhileStatement): void {
        while (this.isTruthy(this.evaluate(stmt.condition))) {
            this.executeBlockStatement(stmt.body, new Environment(this.currentEnv));
        }
    }

    private executeReturnStatement(stmt: AST.ReturnStatement): void {
        const value = stmt.argument ? this.evaluate(stmt.argument) : null;
        throw new ReturnValue(value);
    }

    private executePrintStatement(stmt: AST.PrintStatement): void {
        const value = this.evaluate(stmt.argument);
        const output = this.stringify(value);
        this.output.push(output);
        this.outputCallback(output);
    }

    private executeBlockStatement(block: AST.BlockStatement, env: Environment): void {
        const previousEnv = this.currentEnv;
        this.currentEnv = env;

        try {
            for (const stmt of block.body) {
                this.executeStatement(stmt);
            }
        } finally {
            this.currentEnv = previousEnv;
        }
    }

    // ============================================================
    // Expression Evaluation
    // ============================================================

    private evaluate(expr: AST.Expression): RuntimeValue {
        switch (expr.type) {
            case 'NumericLiteral':
                return expr.value;
            case 'StringLiteral':
                return expr.value;
            case 'BooleanLiteral':
                return expr.value;
            case 'NullLiteral':
                return null;
            case 'Identifier':
                return this.currentEnv.get(expr.name);
            case 'BinaryExpression':
                return this.evaluateBinaryExpression(expr);
            case 'UnaryExpression':
                return this.evaluateUnaryExpression(expr);
            case 'CallExpression':
                return this.evaluateCallExpression(expr);
            case 'AssignmentExpression':
                return this.evaluateAssignmentExpression(expr);
            case 'ArrayLiteral':
                return this.evaluateArrayLiteral(expr);
            case 'IndexExpression':
                return this.evaluateIndexExpression(expr);
            default:
                throw new Error(`Unknown expression type: ${(expr as AST.Expression).type}`);
        }
    }

    private evaluateBinaryExpression(expr: AST.BinaryExpression): RuntimeValue {
        const left = this.evaluate(expr.left);
        const right = this.evaluate(expr.right);

        switch (expr.operator) {
            // Arithmetic
            case '+':
                if (typeof left === 'string' || typeof right === 'string') {
                    return String(left) + String(right);
                }
                return (left as number) + (right as number);
            case '-':
                return (left as number) - (right as number);
            case '*':
                return (left as number) * (right as number);
            case '/':
                if (right === 0) {
                    throw new Error('Division by zero');
                }
                return (left as number) / (right as number);
            case '%':
                return (left as number) % (right as number);

            // Comparison
            case '>':
                return (left as number) > (right as number);
            case '>=':
                return (left as number) >= (right as number);
            case '<':
                return (left as number) < (right as number);
            case '<=':
                return (left as number) <= (right as number);
            case '==':
                return left === right;
            case '!=':
                return left !== right;

            // Logical
            case 'and':
                return this.isTruthy(left) && this.isTruthy(right);
            case 'or':
                return this.isTruthy(left) || this.isTruthy(right);

            default:
                throw new Error(`Unknown operator: ${expr.operator}`);
        }
    }

    private evaluateUnaryExpression(expr: AST.UnaryExpression): RuntimeValue {
        const value = this.evaluate(expr.argument);

        switch (expr.operator) {
            case '-':
                return -(value as number);
            case '!':
                return !this.isTruthy(value);
            default:
                throw new Error(`Unknown unary operator: ${expr.operator}`);
        }
    }

    private evaluateCallExpression(expr: AST.CallExpression): RuntimeValue {
        const callee = this.evaluate(expr.callee);

        if (!callee || typeof callee !== 'object' || (callee as WearFunction).type !== 'function') {
            throw new Error('Can only call functions');
        }

        const func = callee as WearFunction;
        const args = expr.arguments.map(arg => this.evaluate(arg));

        if (args.length !== func.params.length) {
            throw new Error(
                `Function '${func.name}' expects ${func.params.length} arguments, but got ${args.length}`
            );
        }

        // Create new environment for function execution
        const funcEnv = new Environment(func.closure);
        for (let i = 0; i < func.params.length; i++) {
            funcEnv.define(func.params[i], args[i]);
        }

        try {
            this.executeBlockStatement(func.body as AST.BlockStatement, funcEnv);
        } catch (error) {
            if (error instanceof ReturnValue) {
                return error.value;
            }
            throw error;
        }

        return null;
    }

    private evaluateAssignmentExpression(expr: AST.AssignmentExpression): RuntimeValue {
        const value = this.evaluate(expr.value);
        this.currentEnv.assign(expr.assignee.name, value);
        return value;
    }

    private evaluateArrayLiteral(expr: AST.ArrayLiteral): RuntimeValue[] {
        return expr.elements.map(element => this.evaluate(element));
    }

    private evaluateIndexExpression(expr: AST.IndexExpression): RuntimeValue {
        const object = this.evaluate(expr.object);
        const index = this.evaluate(expr.index);

        if (!Array.isArray(object)) {
            throw new Error('Can only index into arrays');
        }
        if (typeof index !== 'number') {
            throw new Error('Array index must be a number');
        }
        if (index < 0 || index >= object.length) {
            throw new Error(`Array index ${index} out of bounds (array length: ${object.length})`);
        }

        return object[index];
    }

    // ============================================================
    // Helper Methods
    // ============================================================

    private isTruthy(value: RuntimeValue): boolean {
        if (value === null || value === undefined) return false;
        if (typeof value === 'boolean') return value;
        return true;
    }

    private stringify(value: RuntimeValue): string {
        if (value === null || value === undefined) return 'null';
        if (Array.isArray(value)) {
            return '[' + value.map(v => this.stringify(v)).join(', ') + ']';
        }
        if (typeof value === 'object' && (value as WearFunction).type === 'function') {
            return `<function ${(value as WearFunction).name}>`;
        }
        return String(value);
    }

    /**
     * Get collected output
     */
    getOutput(): string[] {
        return [...this.output];
    }

    /**
     * Get the error reporter
     */
    getErrorReporter(): ErrorReporter {
        return this.errorReporter;
    }

    /**
     * Reset the interpreter state
     */
    reset(): void {
        this.globalEnv = new Environment();
        this.currentEnv = this.globalEnv;
        this.output = [];
        this.errorReporter.clear();
    }
}
