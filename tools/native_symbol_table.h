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

/*
 * These declarations define the native semantic API boundary.  The existing
 * compiler can adopt the table incrementally without tying type decisions to
 * spelling conventions such as msg*, str*, output*, etc.
 */
WearType wear_symbol_lookup_type(const WearSymbol* symbols, size_t count,
                                 const char* name, const char* scope);
WearType wear_function_lookup_return_type(const WearFunctionSymbol* functions,
                                          size_t count, const char* name);
int wear_types_compatible(WearType expected, WearType actual);

#endif /* WEAR_NATIVE_SYMBOL_TABLE_H */
