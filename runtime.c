/* ============================================================
 * WeaR Lang Runtime Library
 * ============================================================
 * This file contains C helper functions required by WeaR programs.
 * It is injected into generated C code by the WeaR transpiler.
 * ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stdint.h>

static void __wear_fatal(const char* message) {
    fprintf(stderr, "WeaR runtime error: %s\n", message);
    exit(EXIT_FAILURE);
}

static char* __wear_empty_string(void) {
    char* result = (char*)malloc(1);
    if (result == NULL) {
        __wear_fatal("memory allocation failed");
    }
    result[0] = '\0';
    return result;
}

/* ============================================================
 * Array Operations
 * ============================================================ */

/* Create integer array dynamically. */
int* __wear_create_int_array(int count, ...) {
    if (count < 0) {
        __wear_fatal("negative array size");
    }

    size_t size = (size_t)count * sizeof(int);
    if (count > 0 && size / sizeof(int) != (size_t)count) {
        __wear_fatal("array size overflow");
    }

    int* arr = (int*)malloc(size > 0 ? size : sizeof(int));
    if (arr == NULL) {
        __wear_fatal("memory allocation failed");
    }

    va_list args;
    va_start(args, count);
    for (int i = 0; i < count; i++) {
        arr[i] = va_arg(args, int);
    }
    va_end(args);

    return arr;
}

/* ============================================================
 * String Operations
 * ============================================================ */

/* Implementation of string + string. NULL is treated as an empty string. */
char* __wear_concat_impl(const char* a, const char* b) {
    if (a == NULL) a = "";
    if (b == NULL) b = "";

    size_t len_a = strlen(a);
    size_t len_b = strlen(b);
    if (len_a > SIZE_MAX - len_b - 1) {
        __wear_fatal("string size overflow");
    }

    char* result = (char*)malloc(len_a + len_b + 1);
    if (result == NULL) {
        __wear_fatal("memory allocation failed");
    }

    memcpy(result, a, len_a);
    memcpy(result + len_a, b, len_b + 1);
    return result;
}

/* Integer to string helper. */
char* __wear_int_to_str(int value) {
    char* buffer = (char*)malloc(32);
    if (buffer == NULL) {
        __wear_fatal("memory allocation failed");
    }

    int written = snprintf(buffer, 32, "%d", value);
    if (written < 0 || written >= 32) {
        free(buffer);
        __wear_fatal("integer formatting failed");
    }
    return buffer;
}

/* String + int concatenation. */
char* __wear_concat_str_int(const char* s, int n) {
    char* num_str = __wear_int_to_str(n);
    char* result = __wear_concat_impl(s, num_str);
    free(num_str);
    return result;
}

/* Generic string/int concatenation dispatch. */
#define __wear_concat(a, b) _Generic((b), \
    int: __wear_concat_str_int, \
    char*: __wear_concat_impl, \
    const char*: __wear_concat_impl \
)(a, b)

/* Int + string concatenation. */
char* __wear_concat_int_str(int n, const char* s) {
    char* num_str = __wear_int_to_str(n);
    char* result = __wear_concat_impl(num_str, s);
    free(num_str);
    return result;
}

/* String comparison (returns 1 if equal, 0 otherwise). */
int __wear_streq(const char* a, const char* b) {
    if (a == NULL || b == NULL) {
        return a == b ? 1 : 0;
    }
    return strcmp(a, b) == 0 ? 1 : 0;
}

/* String length. */
int __wear_strlen(const char* s) {
    if (s == NULL) {
        return 0;
    }
    size_t len = strlen(s);
    return len > (size_t)INT32_MAX ? INT32_MAX : (int)len;
}

/* Character at index (returns a 1-character string). */
char* __wear_char_at(const char* s, int index) {
    char* result = (char*)malloc(2);
    if (result == NULL) {
        __wear_fatal("memory allocation failed");
    }

    result[0] = '\0';
    result[1] = '\0';

    if (s != NULL && index >= 0) {
        size_t len = strlen(s);
        if ((size_t)index < len) {
            result[0] = s[index];
        }
    }
    return result;
}

/* Check if character is a quote. */
int __wear_is_quote(const char* s) {
    if (s == NULL || s[0] == '\0') return 0;
    return s[0] == '"' ? 1 : 0;
}

/* Get quote character as a string. */
char* __wear_quote_char(void) {
    char* result = (char*)malloc(2);
    if (result == NULL) {
        __wear_fatal("memory allocation failed");
    }
    result[0] = '"';
    result[1] = '\0';
    return result;
}

/* Get newline character as a string. */
char* __wear_newline_char(void) {
    char* result = (char*)malloc(2);
    if (result == NULL) {
        __wear_fatal("memory allocation failed");
    }
    result[0] = '\n';
    result[1] = '\0';
    return result;
}

/* Check if character is a newline. */
int __wear_is_newline(const char* s) {
    if (s == NULL || s[0] == '\0') return 0;
    return (s[0] == '\n' || s[0] == '\r') ? 1 : 0;
}

/* ============================================================
 * File I/O Operations
 * ============================================================ */

/* Read file contents. Failed reads return an allocated empty string. */
char* __wear_read_file(const char* filename) {
    if (filename == NULL) {
        fprintf(stderr, "Error: Cannot open a null filename\n");
        return __wear_empty_string();
    }

    FILE* file = fopen(filename, "rb");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
        return __wear_empty_string();
    }

    if (fseek(file, 0, SEEK_END) != 0) {
        fclose(file);
        fprintf(stderr, "Error: Cannot seek file '%s'\n", filename);
        return __wear_empty_string();
    }

    long length = ftell(file);
    if (length < 0) {
        fclose(file);
        fprintf(stderr, "Error: Cannot determine size of file '%s'\n", filename);
        return __wear_empty_string();
    }

    if (fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        fprintf(stderr, "Error: Cannot rewind file '%s'\n", filename);
        return __wear_empty_string();
    }

    size_t size = (size_t)length;
    if ((long)size != length || size == SIZE_MAX) {
        fclose(file);
        fprintf(stderr, "Error: File '%s' is too large\n", filename);
        return __wear_empty_string();
    }

    char* content = (char*)malloc(size + 1);
    if (content == NULL) {
        fclose(file);
        __wear_fatal("memory allocation failed");
    }

    size_t bytes_read = fread(content, 1, size, file);
    if (bytes_read != size && ferror(file)) {
        free(content);
        fclose(file);
        fprintf(stderr, "Error: Failed reading file '%s'\n", filename);
        return __wear_empty_string();
    }

    content[bytes_read] = '\0';
    fclose(file);
    return content;
}

/* Write file contents. Errors are reported on stderr. */
void __wear_write_file(const char* filename, const char* content) {
    if (filename == NULL) {
        fprintf(stderr, "Error: Cannot write to a null filename\n");
        return;
    }

    FILE* file = fopen(filename, "wb");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot write to file '%s'\n", filename);
        return;
    }

    const char* data = content != NULL ? content : "";
    size_t length = strlen(data);
    size_t written = fwrite(data, 1, length, file);
    if (written != length || fclose(file) != 0) {
        fprintf(stderr, "Error: Failed writing file '%s'\n", filename);
        return;
    }
}

/* ============================================================
 * Input Operations
 * ============================================================ */

/* Read one line from stdin using a dynamically growing buffer. */
char* __wear_input(const char* prompt) {
    if (prompt != NULL && prompt[0] != '\0') {
        fputs(prompt, stdout);
        fflush(stdout);
    }

    size_t capacity = 128;
    size_t length = 0;
    char* buffer = (char*)malloc(capacity);
    if (buffer == NULL) {
        __wear_fatal("memory allocation failed");
    }

    int ch;
    while ((ch = fgetc(stdin)) != EOF && ch != '\n') {
        if (length + 1 >= capacity) {
            if (capacity > SIZE_MAX / 2) {
                free(buffer);
                __wear_fatal("input buffer size overflow");
            }
            size_t next_capacity = capacity * 2;
            char* resized = (char*)realloc(buffer, next_capacity);
            if (resized == NULL) {
                free(buffer);
                __wear_fatal("memory allocation failed");
            }
            buffer = resized;
            capacity = next_capacity;
        }
        buffer[length++] = (char)ch;
    }

    buffer[length] = '\0';
    return buffer;
}

/* ============================================================
 * Print Operations
 * ============================================================ */

/* Print string. */
void __wear_print_str(const char* s) {
    printf("%s\n", s != NULL ? s : "");
}

/* Print integer. */
void __wear_print_int(int n) {
    printf("%d\n", n);
}

/* ============================================================
 * Forward declarations for self-hosted compiler functions
 * ============================================================ */
char* process_imports(char* src);
int is_string_varname(char* name);
int returns_string(char* fn);
int returns_int(char* fn);
int is_quote(char* c);
int is_newline(char* c);
int is_digit(char* c);
int is_letter(char* c);
int is_space(char* c);
