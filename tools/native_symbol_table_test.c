#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include "native_symbol_table.h"

int main(void) {
    static const WearType params[] = {WEAR_TYPE_STR, WEAR_TYPE_INT};
    static const WearSymbol symbols[] = {
        {"caption", WEAR_TYPE_STR, "global", 1, "str_global_caption_1"},
        {"total", WEAR_TYPE_INT, "global", 2, "int_global_total_2"},
        {"caption", WEAR_TYPE_INT, "worker", 4, "int_worker_caption_4"},
        {"local", WEAR_TYPE_STR, "worker", 5, "str_worker_local_5"},
    };
    static const WearFunctionSymbol functions[] = {
        {"panjang", WEAR_TYPE_INT, NULL, 0, 1},
        {"render", WEAR_TYPE_STR, params, 2, 8},
    };

    assert(wear_symbol_lookup_type(symbols, 4, "caption", "worker") == WEAR_TYPE_INT);
    assert(wear_symbol_lookup_type(symbols, 4, "caption", "missing") == WEAR_TYPE_STR);
    assert(wear_symbol_lookup_type(symbols, 4, "total", "worker") == WEAR_TYPE_INT);
    assert(wear_symbol_lookup_type(symbols, 4, "missing", "worker") == WEAR_TYPE_UNKNOWN);

    assert(wear_function_lookup_return_type(functions, 2, "render") == WEAR_TYPE_STR);
    assert(wear_function_lookup_return_type(functions, 2, "panjang") == WEAR_TYPE_INT);
    assert(wear_function_lookup_return_type(functions, 2, "missing") == WEAR_TYPE_UNKNOWN);

    assert(wear_types_compatible(WEAR_TYPE_INT, WEAR_TYPE_INT));
    assert(wear_types_compatible(WEAR_TYPE_UNKNOWN, WEAR_TYPE_STR));
    assert(!wear_types_compatible(WEAR_TYPE_INT, WEAR_TYPE_STR));

    puts("native symbol-table contract: PASS");
    return 0;
}
