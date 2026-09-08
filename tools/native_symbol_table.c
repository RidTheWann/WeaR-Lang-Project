#include <string.h>
#include "native_symbol_table.h"

WearType wear_symbol_lookup_type(const WearSymbol* symbols, size_t count,
                                 const char* name, const char* scope) {
    if (!symbols || !name) {
        return WEAR_TYPE_UNKNOWN;
    }

    /* Exact local-scope match wins over global, mirroring frontend semantics. */
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
