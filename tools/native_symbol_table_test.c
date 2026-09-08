#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "native_symbol_table.h"

int main(void) {
    static const WearType params[] = {WEAR_TYPE_STR, WEAR_TYPE_INT};
    static const WearSymbol seed_symbols[] = {
        {"caption", WEAR_TYPE_STR, "global", 1, "str_global_caption_1"},
        {"total", WEAR_TYPE_INT, "global", 2, "int_global_total_2"},
        {"caption", WEAR_TYPE_INT, "worker", 4, "int_worker_caption_4"},
        {"local", WEAR_TYPE_STR, "worker", 5, "str_worker_local_5"},
    };
    static const WearFunctionSymbol functions[] = {
        {"panjang", WEAR_TYPE_INT, NULL, 0, 1},
        {"render", WEAR_TYPE_STR, params, 2, 8},
    };

    assert(wear_symbol_lookup_type(seed_symbols, 4, "caption", "worker") == WEAR_TYPE_INT);
    assert(wear_symbol_lookup_type(seed_symbols, 4, "caption", "missing") == WEAR_TYPE_STR);
    assert(wear_symbol_lookup_type(seed_symbols, 4, "total", "worker") == WEAR_TYPE_INT);
    assert(wear_symbol_lookup_type(seed_symbols, 4, "missing", "worker") == WEAR_TYPE_UNKNOWN);

    assert(wear_function_lookup_return_type(functions, 2, "render") == WEAR_TYPE_STR);
    assert(wear_function_lookup_return_type(functions, 2, "panjang") == WEAR_TYPE_INT);
    assert(wear_function_lookup_return_type(functions, 2, "missing") == WEAR_TYPE_UNKNOWN);

    assert(wear_types_compatible(WEAR_TYPE_INT, WEAR_TYPE_INT));
    assert(wear_types_compatible(WEAR_TYPE_UNKNOWN, WEAR_TYPE_STR));
    assert(!wear_types_compatible(WEAR_TYPE_INT, WEAR_TYPE_STR));

    /* Exercise the mutable registration API used by Stage-0 migration. */
    WearSymbol symbols[8] = {0};
    size_t symbol_count = 0;
    assert(wear_symbol_declare(symbols, &symbol_count, 8,
                               "caption", WEAR_TYPE_STR, "global", 11,
                               "str_global_caption_11"));
    assert(wear_symbol_declare(symbols, &symbol_count, 8,
                               "caption", WEAR_TYPE_INT, "worker", 12,
                               "int_worker_caption_12"));
    assert(symbol_count == 2);
    assert(wear_symbol_lookup_type(symbols, symbol_count, "caption", "worker") == WEAR_TYPE_INT);
    assert(wear_symbol_lookup_type(symbols, symbol_count, "caption", "other") == WEAR_TYPE_STR);

    assert(wear_symbol_update_type(symbols, symbol_count, "caption", "worker", WEAR_TYPE_STR));
    assert(wear_symbol_lookup_type(symbols, symbol_count, "caption", "worker") == WEAR_TYPE_STR);
    assert(!wear_symbol_update_type(symbols, symbol_count, "missing", "worker", WEAR_TYPE_STR));

    WearFunctionSymbol declared_functions[4] = {0};
    size_t function_count = 0;
    assert(wear_function_declare(declared_functions, &function_count, 4,
                                 "render", WEAR_TYPE_STR, params, 2, 20));
    assert(wear_function_declare(declared_functions, &function_count, 4,
                                 "compute", WEAR_TYPE_INT, NULL, 0, 21));
    assert(function_count == 2);
    assert(wear_function_lookup_return_type(declared_functions, function_count, "render") == WEAR_TYPE_STR);
    assert(wear_function_lookup_return_type(declared_functions, function_count, "compute") == WEAR_TYPE_INT);

    /* Capacity boundaries must fail without corrupting the table. */
    WearSymbol one_symbol[1] = {0};
    size_t one_count = 0;
    assert(wear_symbol_declare(one_symbol, &one_count, 1,
                               "only", WEAR_TYPE_INT, "global", 1, NULL));
    assert(!wear_symbol_declare(one_symbol, &one_count, 1,
                                "overflow", WEAR_TYPE_STR, "global", 2, NULL));
    assert(one_count == 1);
    assert(strcmp(one_symbol[0].name, "only") == 0);

    puts("native symbol-table contract: PASS");
    return 0;
}
