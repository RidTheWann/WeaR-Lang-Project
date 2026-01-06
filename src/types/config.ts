/**
 * Language Configuration Interface for WeaR Lang
 * Enables polyglot keyword support
 */

export interface KeywordMap {
    // Variable declarations
    var: string;
    const: string;

    // Function
    function: string;
    return: string;

    // Control flow
    if: string;
    else: string;
    while: string;
    for: string;

    // Logical operators
    and: string;
    or: string;

    // Built-in functions
    print: string;

    // Literals
    true: string;
    false: string;
    null: string;
}

export interface LanguageConfig {
    name: string;
    code: string;  // 'en', 'id', etc.
    keywords: KeywordMap;
}

/**
 * Reverses a keyword map for lexer lookup
 * Maps localized keyword -> canonical token type key
 */
export function createReversedKeywordMap(config: LanguageConfig): Map<string, keyof KeywordMap> {
    const reversed = new Map<string, keyof KeywordMap>();

    for (const [canonical, localized] of Object.entries(config.keywords)) {
        reversed.set(localized, canonical as keyof KeywordMap);
    }

    return reversed;
}
