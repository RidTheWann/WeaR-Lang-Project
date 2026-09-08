#ifndef WEAR_NATIVE_SYMBOL_TABLE_H
#define WEAR_NATIVE_SYMBOL_TABLE_H

#include <stddef.h>
#include "native_types.h"

/* Native compiler migration seam: identifiers are metadata keys only. */
typedef struct {
    const char* name;
    WearType type;
    const char* scope;
    int line;
    const char* internal_name;
} WearSymbol;

typedef struct {
    const char* name;
    WearType return_type;
    const WearType* params;
    size_t param_count;
    int line;
} WearFunctionSymbol;

/* Lookup APIs used by native compiler semantic lowering. */
WearType wear_symbol_lookup_type(const WearSymbol* symbols, size_t count,
                                 const char* name, const char* scope);
WearType wear_function_lookup_return_type(const WearFunctionSymbol* functions,
                                          size_t count, const char* name);
int wear_types_compatible(WearType expected, WearType actual);

/* Mutable table helpers for the Stage-0 migration. */
int wear_symbol_declare(WearSymbol* symbols, size_t* count, size_t capacity,
                        const char* name, WearType type, const char* scope,
                        int line, const char* internal_name);
int wear_symbol_update_type(WearSymbol* symbols, size_t count,
                            const char* name, const char* scope,
                            WearType type);
int wear_function_declare(WearFunctionSymbol* functions, size_t* count,
                          size_t capacity, const char* name,
                          WearType return_type, const WearType* params,
                          size_t param_count, int line);

#endif /* WEAR_NATIVE_SYMBOL_TABLE_H */
