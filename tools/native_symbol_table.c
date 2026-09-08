#include <string.h>
#include "native_symbol_table.h"

WearType wear_symbol_lookup_type(const WearSymbol* symbols, size_t count,
                                 const char* name, const char* scope) {
    if (!symbols || !name) {
        return WEAR_TYPE_UNKNOWN;
    }

    if (scope) {
        for (size_t i = count; i > 0; --i) {
            const WearSymbol* symbol = &symbols[i - 1];
            if (symbol->name && symbol->scope &&
                strcmp(symbol->name, name) == 0 &&
                strcmp(symbol->scope, scope) == 0) {
                return symbol->type;
            }
        }
    }

    for (size_t i = count; i > 0; --i) {
        const WearSymbol* symbol = &symbols[i - 1];
        if (symbol->name && symbol->scope &&
            strcmp(symbol->name, name) == 0 &&
            strcmp(symbol->scope, "global") == 0) {
            return symbol->type;
        }
    }

    return WEAR_TYPE_UNKNOWN;
}

WearType wear_function_lookup_return_type(const WearFunctionSymbol* functions,
                                          size_t count, const char* name) {
    if (!functions || !name) {
        return WEAR_TYPE_UNKNOWN;
    }

    for (size_t i = count; i > 0; --i) {
        const WearFunctionSymbol* function = &functions[i - 1];
        if (function->name && strcmp(function->name, name) == 0) {
            return function->return_type;
        }
    }

    return WEAR_TYPE_UNKNOWN;
}

int wear_types_compatible(WearType expected, WearType actual) {
    if (expected == WEAR_TYPE_UNKNOWN || actual == WEAR_TYPE_UNKNOWN) {
        return 1;
    }
    return expected == actual;
}

int wear_symbol_declare(WearSymbol* symbols, size_t* count, size_t capacity,
                        const char* name, WearType type, const char* scope,
                        int line, const char* internal_name) {
    if (!symbols || !count || !name || !scope || *count >= capacity) {
        return 0;
    }

    /*
     * The native bootstrap models global/function scope (not nested block
     * scope). Keep the table canonical by rejecting a second declaration of
     * the same source name in the same scope instead of allowing the most
     * recent entry to silently change the resolved type.
     */
    for (size_t i = 0; i < *count; ++i) {
        if (symbols[i].name && symbols[i].scope &&
            strcmp(symbols[i].name, name) == 0 &&
            strcmp(symbols[i].scope, scope) == 0) {
            return 0;
        }
    }

    symbols[*count] = (WearSymbol){
        .name = name,
        .type = type,
        .scope = scope,
        .line = line,
        .internal_name = internal_name,
    };
    ++(*count);
    return 1;
}

int wear_symbol_update_type(WearSymbol* symbols, size_t count,
                            const char* name, const char* scope,
                            WearType type) {
    if (!symbols || !name || !scope) {
        return 0;
    }
    for (size_t i = count; i > 0; --i) {
        WearSymbol* symbol = &symbols[i - 1];
        if (symbol->name && symbol->scope &&
            strcmp(symbol->name, name) == 0 &&
            strcmp(symbol->scope, scope) == 0) {
            symbol->type = type;
            return 1;
        }
    }
    return 0;
}

int wear_function_declare(WearFunctionSymbol* functions, size_t* count,
                          size_t capacity, const char* name,
                          WearType return_type, const WearType* params,
                          size_t param_count, int line) {
    if (!functions || !count || !name || *count >= capacity) {
        return 0;
    }

    /* Function names have their own namespace and are globally unique. */
    for (size_t i = 0; i < *count; ++i) {
        if (functions[i].name && strcmp(functions[i].name, name) == 0) {
            return 0;
        }
    }

    functions[*count] = (WearFunctionSymbol){
        .name = name,
        .return_type = return_type,
        .params = params,
        .param_count = param_count,
        .line = line,
    };
    ++(*count);
    return 1;
}
