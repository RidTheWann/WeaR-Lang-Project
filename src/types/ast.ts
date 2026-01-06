/**
 * Abstract Syntax Tree (AST) Node Definitions for WeaR Lang
 * All node types are strictly typed with TypeScript interfaces
 */

// ============================================================
// Base Types
// ============================================================

export type NodeType =
    // Program
    | 'Program'
    // Statements
    | 'VarDeclaration'
    | 'FunctionDeclaration'
    | 'IfStatement'
    | 'WhileStatement'
    | 'ReturnStatement'
    | 'PrintStatement'
    | 'ExpressionStatement'
    | 'BlockStatement'
    // Expressions
    | 'BinaryExpression'
    | 'UnaryExpression'
    | 'CallExpression'
    | 'AssignmentExpression'
    | 'IndexExpression'
    | 'Identifier'
    | 'NumericLiteral'
    | 'StringLiteral'
    | 'BooleanLiteral'
    | 'NullLiteral'
    | 'ArrayLiteral';

export interface BaseNode {
    type: NodeType;
    line: number;
    column: number;
}

// ============================================================
// Program (Root Node)
// ============================================================

export interface Program extends BaseNode {
    type: 'Program';
    body: Statement[];
}

// ============================================================
// Statements
// ============================================================

export type Statement =
    | VarDeclaration
    | FunctionDeclaration
    | IfStatement
    | WhileStatement
    | ReturnStatement
    | PrintStatement
    | ExpressionStatement
    | BlockStatement;

export interface VarDeclaration extends BaseNode {
    type: 'VarDeclaration';
    identifier: Identifier;
    value: Expression | null;
    isConst: boolean;
}

export interface FunctionDeclaration extends BaseNode {
    type: 'FunctionDeclaration';
    name: Identifier;
    params: Identifier[];
    body: BlockStatement;
}

export interface IfStatement extends BaseNode {
    type: 'IfStatement';
    condition: Expression;
    consequent: BlockStatement;
    alternate: BlockStatement | IfStatement | null;
}

export interface WhileStatement extends BaseNode {
    type: 'WhileStatement';
    condition: Expression;
    body: BlockStatement;
}

export interface ReturnStatement extends BaseNode {
    type: 'ReturnStatement';
    argument: Expression | null;
}

export interface PrintStatement extends BaseNode {
    type: 'PrintStatement';
    argument: Expression;
}

export interface ExpressionStatement extends BaseNode {
    type: 'ExpressionStatement';
    expression: Expression;
}

export interface BlockStatement extends BaseNode {
    type: 'BlockStatement';
    body: Statement[];
}

// ============================================================
// Expressions
// ============================================================

export type Expression =
    | BinaryExpression
    | UnaryExpression
    | CallExpression
    | AssignmentExpression
    | IndexExpression
    | Identifier
    | NumericLiteral
    | StringLiteral
    | BooleanLiteral
    | NullLiteral
    | ArrayLiteral;

export interface BinaryExpression extends BaseNode {
    type: 'BinaryExpression';
    operator: string;
    left: Expression;
    right: Expression;
}

export interface UnaryExpression extends BaseNode {
    type: 'UnaryExpression';
    operator: string;
    argument: Expression;
}

export interface CallExpression extends BaseNode {
    type: 'CallExpression';
    callee: Expression;
    arguments: Expression[];
}

export interface AssignmentExpression extends BaseNode {
    type: 'AssignmentExpression';
    assignee: Identifier;
    value: Expression;
}

export interface Identifier extends BaseNode {
    type: 'Identifier';
    name: string;
}

export interface NumericLiteral extends BaseNode {
    type: 'NumericLiteral';
    value: number;
}

export interface StringLiteral extends BaseNode {
    type: 'StringLiteral';
    value: string;
}

export interface BooleanLiteral extends BaseNode {
    type: 'BooleanLiteral';
    value: boolean;
}

export interface NullLiteral extends BaseNode {
    type: 'NullLiteral';
    value: null;
}

export interface ArrayLiteral extends BaseNode {
    type: 'ArrayLiteral';
    elements: Expression[];
}

export interface IndexExpression extends BaseNode {
    type: 'IndexExpression';
    object: Expression;
    index: Expression;
}

// ============================================================
// Factory Functions
// ============================================================

export function createProgram(body: Statement[], line = 1, column = 1): Program {
    return { type: 'Program', body, line, column };
}

export function createIdentifier(name: string, line: number, column: number): Identifier {
    return { type: 'Identifier', name, line, column };
}

export function createNumericLiteral(value: number, line: number, column: number): NumericLiteral {
    return { type: 'NumericLiteral', value, line, column };
}

export function createStringLiteral(value: string, line: number, column: number): StringLiteral {
    return { type: 'StringLiteral', value, line, column };
}

export function createBooleanLiteral(value: boolean, line: number, column: number): BooleanLiteral {
    return { type: 'BooleanLiteral', value, line, column };
}

export function createNullLiteral(line: number, column: number): NullLiteral {
    return { type: 'NullLiteral', value: null, line, column };
}
