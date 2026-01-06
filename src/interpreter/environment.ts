/**
 * Environment for WeaR Lang
 * Handles variable scoping and lookup
 */

export type RuntimeValue = string | number | boolean | null | WearFunction | RuntimeValue[] | undefined;

export interface WearFunction {
    type: 'function';
    name: string;
    params: string[];
    body: unknown; // AST.BlockStatement
    closure: Environment;
}

export class Environment {
    private values: Map<string, RuntimeValue> = new Map();
    private constants: Set<string> = new Set();
    private parent: Environment | null;

    constructor(parent: Environment | null = null) {
        this.parent = parent;
    }

    /**
     * Define a new variable
     */
    define(name: string, value: RuntimeValue, isConst: boolean = false): void {
        if (this.values.has(name)) {
            throw new Error(`Variable '${name}' is already defined in this scope.`);
        }
        this.values.set(name, value);
        if (isConst) {
            this.constants.add(name);
        }
    }

    /**
     * Get a variable's value
     */
    get(name: string): RuntimeValue {
        if (this.values.has(name)) {
            return this.values.get(name);
        }
        if (this.parent) {
            return this.parent.get(name);
        }
        throw new Error(`Undefined variable '${name}'.`);
    }

    /**
     * Assign a new value to an existing variable
     */
    assign(name: string, value: RuntimeValue): void {
        if (this.values.has(name)) {
            if (this.constants.has(name)) {
                throw new Error(`Cannot reassign constant '${name}'.`);
            }
            this.values.set(name, value);
            return;
        }
        if (this.parent) {
            this.parent.assign(name, value);
            return;
        }
        throw new Error(`Undefined variable '${name}'.`);
    }

    /**
     * Check if a variable exists
     */
    has(name: string): boolean {
        if (this.values.has(name)) return true;
        if (this.parent) return this.parent.has(name);
        return false;
    }
}
