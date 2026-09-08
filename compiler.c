/* WeaR Lang Stage-0 compiler entrypoint.
 *
 * The historical transpiler is kept in compiler_legacy.c while this entrypoint
 * performs the native semantic symbol pass first.  The pass uses the canonical
 * native symbol table to assign deterministic internal names to variables, then
 * feeds the rewritten source to the mature Stage-0 backend.  This removes the
 * old variable-name heuristic from the correctness path without changing the
 * backend's established code-generation behavior.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "tools/native_symbol_table.h"

#define WEAR_NATIVE_MAX_SYMBOLS 4096
#define WEAR_NATIVE_MAX_FUNCTIONS 512
#define WEAR_NATIVE_MAX_ALLOCATIONS 4096
#define WEAR_ALIAS_MAX 192

static WearSymbol native_symbols[WEAR_NATIVE_MAX_SYMBOLS];
static size_t native_symbol_count = 0;
static WearFunctionSymbol native_functions[WEAR_NATIVE_MAX_FUNCTIONS];
static size_t native_function_count = 0;
static char *native_allocations[WEAR_NATIVE_MAX_ALLOCATIONS];
static size_t native_allocation_count = 0;

static void native_reset(void) {
    size_t i;
    for (i = 0; i < native_allocation_count; ++i) {
        free(native_allocations[i]);
    }
    native_allocation_count = 0;
    native_symbol_count = 0;
    native_function_count = 0;
    memset(native_symbols, 0, sizeof(native_symbols));
    memset(native_functions, 0, sizeof(native_functions));
}

static char *native_strdup_tracked(const char *text) {
    size_t len;
    char *copy;
    if (text == NULL || native_allocation_count >= WEAR_NATIVE_MAX_ALLOCATIONS) {
        return NULL;
    }
    len = strlen(text);
    copy = (char *)malloc(len + 1);
    if (copy == NULL) {
        return NULL;
    }
    memcpy(copy, text, len + 1);
    native_allocations[native_allocation_count++] = copy;
    return copy;
}

static void register_builtin_functions(void) {
    static const char *string_builtins[] = {
        "baca_file", "char_at", "quote_char", "newline_char", "input",
        "process_imports"
    };
    static const char *int_builtins[] = {
        "panjang", "sama", "is_quote", "is_newline", "is_digit",
        "is_letter", "is_space"
    };
    size_t i;

    for (i = 0; i < sizeof(string_builtins) / sizeof(string_builtins[0]); ++i) {
        (void)wear_function_declare(
            native_functions, &native_function_count, WEAR_NATIVE_MAX_FUNCTIONS,
            string_builtins[i], WEAR_TYPE_STR, NULL, 0, 0);
    }
    for (i = 0; i < sizeof(int_builtins) / sizeof(int_builtins[0]); ++i) {
        (void)wear_function_declare(
            native_functions, &native_function_count, WEAR_NATIVE_MAX_FUNCTIONS,
            int_builtins[i], WEAR_TYPE_INT, NULL, 0, 0);
    }
}

static int is_ident_start(unsigned char c) {
    return isalpha(c) || c == '_';
}

static int is_ident_continue(unsigned char c) {
    return isalnum(c) || c == '_';
}

static void skip_space_and_comments(const char *src, size_t len, size_t *pos) {
    for (;;) {
        while (*pos < len && isspace((unsigned char)src[*pos])) {
            (*pos)++;
        }
        if (*pos + 1 < len && src[*pos] == '/' && src[*pos + 1] == '/') {
            *pos += 2;
            while (*pos < len && src[*pos] != '\n' && src[*pos] != '\r') {
                (*pos)++;
            }
            continue;
        }
        break;
    }
}

static int read_identifier(const char *src, size_t len, size_t *pos,
                           size_t *start, size_t *end) {
    size_t p;
    skip_space_and_comments(src, len, pos);
    if (*pos >= len || !is_ident_start((unsigned char)src[*pos])) {
        return 0;
    }
    p = *pos;
    *start = p++;
    while (p < len && is_ident_continue((unsigned char)src[p])) {
        ++p;
    }
    *end = p;
    *pos = p;
    return 1;
}

static int ident_equals(const char *src, size_t start, size_t end,
                        const char *word) {
    size_t len = end - start;
    return strlen(word) == len && strncmp(src + start, word, len) == 0;
}

static void skip_string_literal(const char *src, size_t len, size_t *pos) {
    int escaped = 0;
    if (*pos >= len || src[*pos] != '"') {
        return;
    }
    ++(*pos);
    while (*pos < len) {
        char c = src[*pos];
        ++(*pos);
        if (escaped) {
            escaped = 0;
            continue;
        }
        if (c == '\\') {
            escaped = 1;
            continue;
        }
        if (c == '"') {
            break;
        }
    }
}

static int token_is_number(const char *src, size_t len, size_t *pos) {
    size_t p;
    int saw_digit = 0;
    skip_space_and_comments(src, len, pos);
    p = *pos;
    if (p < len && (src[p] == '-' || src[p] == '+')) {
        ++p;
    }
    while (p < len && isdigit((unsigned char)src[p])) {
        saw_digit = 1;
        ++p;
    }
    if (saw_digit) {
        *pos = p;
    }
    return saw_digit;
}

static WearType lookup_word_type(const char *src, size_t start, size_t end,
                                 const char *scope) {
    char word[WEAR_ALIAS_MAX];
    size_t len = end - start;
    WearType type;
    WearType fn_type;

    if (len == 0 || len >= sizeof(word)) {
        return WEAR_TYPE_UNKNOWN;
    }
    memcpy(word, src + start, len);
    word[len] = '\0';

    type = wear_symbol_lookup_type(
        native_symbols, native_symbol_count, word, scope);
    if (type != WEAR_TYPE_UNKNOWN) {
        return type;
    }
    fn_type = wear_function_lookup_return_type(
        native_functions, native_function_count, word);
    if (fn_type != WEAR_TYPE_UNKNOWN) {
        return fn_type;
    }
    return WEAR_TYPE_UNKNOWN;
}

static char *make_internal_name(const char *scope, const char *name,
                                WearType type, size_t serial) {
    char buffer[WEAR_ALIAS_MAX];
    const char *prefix = (type == WEAR_TYPE_STR) ? "str" : "int";
    if (scope == NULL || name == NULL) {
        return NULL;
    }
    (void)snprintf(buffer, sizeof(buffer), "%s__%s__%s__%zu",
                   prefix, scope, name, serial);
    return native_strdup_tracked(buffer);
}

static int declare_native_variable(const char *src, size_t name_start,
                                   size_t name_end, const char *scope,
                                   WearType type, int line) {
    char name[WEAR_ALIAS_MAX];
    char *internal_name;
    size_t name_len = name_end - name_start;

    if (name_len == 0 || name_len >= sizeof(name) ||
        (type != WEAR_TYPE_INT && type != WEAR_TYPE_STR)) {
        return 0;
    }
    memcpy(name, src + name_start, name_len);
    name[name_len] = '\0';

    internal_name = make_internal_name(scope, name, type,
                                       native_symbol_count + 1);
    if (internal_name == NULL) {
        return 0;
    }
    return wear_symbol_declare(
        native_symbols, &native_symbol_count, WEAR_NATIVE_MAX_SYMBOLS,
        native_strdup_tracked(name), type, native_strdup_tracked(scope),
        line, internal_name);
}

static const char *native_alias_for(const char *src, size_t start, size_t end,
                                    const char *scope) {
    size_t i;
    size_t name_len = end - start;
    size_t scope_len = strlen(scope);

    for (i = native_symbol_count; i > 0; --i) {
        const WearSymbol *symbol = &native_symbols[i - 1];
        if (symbol->name == NULL || symbol->scope == NULL ||
            symbol->internal_name == NULL) {
            continue;
        }
        if (strlen(symbol->name) != name_len ||
            strncmp(symbol->name, src + start, name_len) != 0) {
            continue;
        }
        if (strlen(symbol->scope) == scope_len &&
            strncmp(symbol->scope, scope, scope_len) == 0) {
            return symbol->internal_name;
        }
        if (strcmp(symbol->scope, "global") == 0 &&
            strcmp(scope, "global") != 0) {
            return symbol->internal_name;
        }
    }
    return NULL;
}

static WearType infer_initializer_type(const char *src, size_t len,
                                       size_t *pos, const char *scope) {
    size_t save = *pos;
    size_t start, end;
    WearType type;

    skip_space_and_comments(src, len, pos);
    if (*pos < len && src[*pos] == '"') {
        *pos = save;
        return WEAR_TYPE_STR;
    }
    if (token_is_number(src, len, pos)) {
        return WEAR_TYPE_INT;
    }
    *pos = save;
    if (read_identifier(src, len, pos, &start, &end)) {
        type = lookup_word_type(src, start, end, scope);
        if (type != WEAR_TYPE_UNKNOWN) {
            return type;
        }
        /* An expression beginning with an identifier defaults to int in the
         * legacy backend. Native lookup is authoritative whenever available. */
        return WEAR_TYPE_INT;
    }
    return WEAR_TYPE_INT;
}

static int parse_function_signature(const char *src, size_t len, size_t *pos,
                                   char *function_name, size_t name_cap,
                                   const char *outer_scope) {
    size_t start, end;
    size_t param_pos;
    size_t param_index = 0;
    char parameter_names[64][WEAR_ALIAS_MAX];
    WearType parameter_types[64];
    (void)outer_scope;

    skip_space_and_comments(src, len, pos);
    if (!read_identifier(src, len, pos, &start, &end)) {
        return 0;
    }
    if (end - start >= name_cap) {
        return 0;
    }
    memcpy(function_name, src + start, end - start);
    function_name[end - start] = '\0';

    skip_space_and_comments(src, len, pos);
    if (*pos >= len || src[*pos] != '(') {
        return 1;
    }
    ++(*pos);
    param_pos = *pos;
    for (;;) {
        size_t pstart, pend;
        WearType param_type = WEAR_TYPE_STR;
        char param_name[WEAR_ALIAS_MAX];

        skip_space_and_comments(src, len, &param_pos);
        if (param_pos >= len) {
            *pos = param_pos;
            break;
        }
        if (src[param_pos] == ')') {
            param_pos++;
            *pos = param_pos;
            break;
        }
        if (!read_identifier(src, len, &param_pos, &pstart, &pend)) {
            param_pos++;
            continue;
        }
        if (pend - pstart >= sizeof(param_name)) {
            continue;
        }
        memcpy(param_name, src + pstart, pend - pstart);
        param_name[pend - pstart] = '\0';

        skip_space_and_comments(src, len, &param_pos);
        if (param_pos < len && src[param_pos] == ':') {
            size_t tstart, tend;
            ++param_pos;
            if (read_identifier(src, len, &param_pos, &tstart, &tend) &&
                ident_equals(src, tstart, tend, "int")) {
                param_type = WEAR_TYPE_INT;
            }
        }
        if (param_index < 64) {
            strcpy(parameter_names[param_index], param_name);
            parameter_types[param_index] = param_type;
            ++param_index;
        }
        skip_space_and_comments(src, len, &param_pos);
        if (param_pos < len && src[param_pos] == ',') {
            ++param_pos;
        }
    }
    return 1;
}

static int collect_native_symbols(const char *src, size_t len) {
    size_t pos = 0;
    int line = 1;
    int in_function = 0;
    int brace_depth = 0;
    char scope[WEAR_ALIAS_MAX] = "global";

    while (pos < len) {
        size_t start, end;
        skip_space_and_comments(src, len, &pos);
        if (pos >= len) {
            break;
        }
        if (src[pos] == '\n') {
            ++line;
            ++pos;
            continue;
        }
        if (src[pos] == '"') {
            skip_string_literal(src, len, &pos);
            continue;
        }
        if (src[pos] == '{') {
            if (in_function) {
                ++brace_depth;
            }
            ++pos;
            continue;
        }
        if (src[pos] == '}') {
            if (in_function && brace_depth > 0) {
                --brace_depth;
                if (brace_depth == 0) {
                    in_function = 0;
                    strcpy(scope, "global");
                }
            }
            ++pos;
            continue;
        }
        if (!read_identifier(src, len, &pos, &start, &end)) {
            ++pos;
            continue;
        }

        if (ident_equals(src, start, end, "fungsi")) {
            size_t function_pos = pos;
            char function_name[WEAR_ALIAS_MAX] = "";
            size_t signature_pos = pos;
            (void)parse_function_signature(src, len, &signature_pos,
                                            function_name, sizeof(function_name),
                                            scope);
            if (function_name[0] != '\0') {
                WearType return_type =
                    (wear_function_lookup_return_type(
                         native_functions, native_function_count, function_name) ==
                     WEAR_TYPE_STR) ? WEAR_TYPE_STR : WEAR_TYPE_INT;
                (void)wear_function_declare(
                    native_functions, &native_function_count,
                    WEAR_NATIVE_MAX_FUNCTIONS, function_name, return_type,
                    NULL, 0, line);
                strcpy(scope, function_name);
                in_function = 1;
                brace_depth = 0;
            }
            pos = function_pos;
            continue;
        }

        if (ident_equals(src, start, end, "var")) {
            size_t name_start, name_end;
            size_t initializer_pos;
            WearType type;
            size_t p = pos;
            if (read_identifier(src, len, &p, &name_start, &name_end)) {
                skip_space_and_comments(src, len, &p);
                if (p < len && src[p] == '=') {
                    initializer_pos = p + 1;
                    type = infer_initializer_type(src, len, &initializer_pos, scope);
                } else {
                    type = WEAR_TYPE_INT;
                }
                (void)declare_native_variable(src, name_start, name_end,
                                               scope, type, line);
                pos = p;
                continue;
            }
        }

        while (pos < len && src[pos] != '\n' && src[pos] != '\r') {
            if (src[pos] == '"') {
                skip_string_literal(src, len, &pos);
            } else if (src[pos] == '}' || src[pos] == '{') {
                break;
            } else {
                ++pos;
            }
        }
    }
    return 1;
}

static int rewrite_source(const char *src, size_t len, char **out_source,
                          size_t *out_len) {
    size_t pos = 0;
    size_t cap = len + 1024;
    size_t used = 0;
    int in_function = 0;
    int brace_depth = 0;
    char scope[WEAR_ALIAS_MAX] = "global";
    char *out = (char *)malloc(cap);

    if (out == NULL) {
        return 0;
    }

#define ENSURE_CAP(extra) do { \
        if (used + (extra) + 1 > cap) { \
            size_t new_cap = cap * 2; \
            while (used + (extra) + 1 > new_cap) new_cap *= 2; \
            char *new_out = (char *)realloc(out, new_cap); \
            if (new_out == NULL) { free(out); return 0; } \
            out = new_out; cap = new_cap; \
        } \
    } while (0)

    while (pos < len) {
        size_t start = pos;
        size_t end;
        if (src[pos] == '"') {
            size_t q = pos;
            skip_string_literal(src, len, &q);
            ENSURE_CAP(q - pos);
            memcpy(out + used, src + pos, q - pos);
            used += q - pos;
            pos = q;
            continue;
        }
        if (src[pos] == '/' && pos + 1 < len && src[pos + 1] == '/') {
            size_t q = pos + 2;
            while (q < len && src[q] != '\n' && src[q] != '\r') ++q;
            ENSURE_CAP(q - pos);
            memcpy(out + used, src + pos, q - pos);
            used += q - pos;
            pos = q;
            continue;
        }
        if (src[pos] == '{') {
            if (in_function) ++brace_depth;
            ENSURE_CAP(1); out[used++] = src[pos++];
            continue;
        }
        if (src[pos] == '}') {
            if (in_function && brace_depth > 0) {
                --brace_depth;
                if (brace_depth == 0) {
                    in_function = 0;
                    strcpy(scope, "global");
                }
            }
            ENSURE_CAP(1); out[used++] = src[pos++];
            continue;
        }
        if (!is_ident_start((unsigned char)src[pos])) {
            ENSURE_CAP(1); out[used++] = src[pos++];
            continue;
        }
        end = pos + 1;
        while (end < len && is_ident_continue((unsigned char)src[end])) ++end;

        if (ident_equals(src, pos, end, "fungsi")) {
            size_t p = end;
            size_t fn_start, fn_end;
            ENSURE_CAP(end - pos);
            memcpy(out + used, src + pos, end - pos);
            used += end - pos;
            skip_space_and_comments(src, len, &p);
            if (read_identifier(src, len, &p, &fn_start, &fn_end)) {
                ENSURE_CAP(fn_end - fn_start);
                memcpy(out + used, src + fn_start, fn_end - fn_start);
                used += fn_end - fn_start;
                if (fn_end > fn_start && fn_end - fn_start < sizeof(scope)) {
                    memcpy(scope, src + fn_start, fn_end - fn_start);
                    scope[fn_end - fn_start] = '\0';
                    in_function = 1;
                    brace_depth = 0;
                }
            }
            pos = end;
            continue;
        }

        if (ident_equals(src, pos, end, "//")) {
            ENSURE_CAP(end - pos);
            memcpy(out + used, src + pos, end - pos);
            used += end - pos;
            pos = end;
            continue;
        }

        {
            size_t next = end;
            const char *alias = NULL;
            skip_space_and_comments(src, len, &next);
            if (next < len && src[next] == '(') {
                alias = NULL; /* Function call / builtin: keep canonical name. */
            } else {
                alias = native_alias_for(src, start, end, scope);
            }
            if (alias != NULL) {
                size_t alias_len = strlen(alias);
                ENSURE_CAP(alias_len);
                memcpy(out + used, alias, alias_len);
                used += alias_len;
            } else {
                ENSURE_CAP(end - start);
                memcpy(out + used, src + start, end - start);
                used += end - start;
            }
        }
        pos = end;
    }

    out[used] = '\0';
    *out_source = out;
    *out_len = used;
#undef ENSURE_CAP
    return 1;
}

static char *read_entire_file(const char *path, size_t *out_len) {
    FILE *file = fopen(path, "rb");
    long size;
    char *buffer;
    size_t read_size;
    if (file == NULL) return NULL;
    if (fseek(file, 0, SEEK_END) != 0) { fclose(file); return NULL; }
    size = ftell(file);
    if (size < 0) { fclose(file); return NULL; }
    if (fseek(file, 0, SEEK_SET) != 0) { fclose(file); return NULL; }
    buffer = (char *)malloc((size_t)size + 1);
    if (buffer == NULL) { fclose(file); return NULL; }
    read_size = fread(buffer, 1, (size_t)size, file);
    fclose(file);
    buffer[read_size] = '\0';
    if (out_len != NULL) *out_len = read_size;
    return buffer;
}

static int write_entire_file(const char *path, const char *data, size_t len) {
    FILE *file = fopen(path, "wb");
    size_t written;
    if (file == NULL) return 0;
    written = fwrite(data, 1, len, file);
    if (fclose(file) != 0) return 0;
    return written == len;
}

#define main wear_legacy_main
#include "compiler_legacy.c"
#undef main

int main(int argc, char *argv[]) {
    size_t source_len = 0;
    size_t rewritten_len = 0;
    char *source = NULL;
    char *rewritten = NULL;
    int result;

    native_reset();
    register_builtin_functions();

    source = read_entire_file("input.wr", &source_len);
    if (source == NULL) {
        fprintf(stderr, "Error: Cannot open input.wr for native symbol analysis.\n");
        native_reset();
        return 1;
    }

    if (!collect_native_symbols(source, source_len) ||
        !rewrite_source(source, source_len, &rewritten, &rewritten_len)) {
        fprintf(stderr, "Error: Native symbol analysis failed.\n");
        free(source);
        native_reset();
        return 1;
    }

    if (!write_entire_file("input.wr", rewritten, rewritten_len)) {
        fprintf(stderr, "Error: Cannot write native-lowered input.wr.\n");
        free(rewritten);
        free(source);
        native_reset();
        return 1;
    }

    result = wear_legacy_main(argc, argv);

    if (!write_entire_file("input.wr", source, source_len)) {
        fprintf(stderr, "Error: Failed to restore original input.wr after compilation.\n");
        result = result == 0 ? 1 : result;
    }

    free(rewritten);
    free(source);
    native_reset();
    return result;
}
