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

/* ============================================================
 * Array Operations
 * ============================================================ */

/* Create integer array dynamically */
int* __wear_create_int_array(int count, ...) {
    int* arr = (int*)malloc(count * sizeof(int));
    if (arr == NULL) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
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

/* Implementation of string + string */
char* __wear_concat_impl(const char* a, const char* b) {
    size_t len_a = strlen(a);
    size_t len_b = strlen(b);
    char* result = (char*)malloc(len_a + len_b + 1);
    if (result == NULL) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    strcpy(result, a);
    strcat(result, b);
    return result;
}

/* Integer to string helper */
char* __wear_int_to_str(int value) {
    char* buffer = (char*)malloc(32);
    if (buffer == NULL) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    sprintf(buffer, "%d", value);
    return buffer;
}

/* String + int concatenation */
char* __wear_concat_str_int(const char* s, int n) {
    char* num_str = __wear_int_to_str(n);
    char* result = __wear_concat_impl(s, num_str);
    free(num_str);
    return result;
}

/* Generic macro for overload */
#define __wear_concat(a, b) _Generic((b), \
    int: __wear_concat_str_int, \
    char*: __wear_concat_impl, \
    const char*: __wear_concat_impl \
)(a, b)

/* Int + string concatenation */
char* __wear_concat_int_str(int n, const char* s) {
    char* num_str = __wear_int_to_str(n);
    char* result = __wear_concat(num_str, s);
    free(num_str);
    return result;
}

/* String comparison (returns 1 if equal, 0 otherwise) */
int __wear_streq(const char* a, const char* b) {
    return strcmp(a, b) == 0 ? 1 : 0;
}

/* String length */
int __wear_strlen(const char* s) {
    return (int)strlen(s);
}

/* Character at index (returns 1-char string) */
char* __wear_char_at(const char* s, int index) {
    char* result = (char*)malloc(2);
    if (result == NULL) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    if (index >= 0 && index < (int)strlen(s)) {
        result[0] = s[index];
        result[1] = '\0';
    } else {
        result[0] = '\0';
    }
    return result;
}

/* Check if character is a quote (returns 1 if quote, 0 otherwise) */
int __wear_is_quote(const char* s) {
    if (s == NULL || s[0] == '\0') return 0;
    return s[0] == '"' ? 1 : 0;
}

/* Get quote character as a string */
char* __wear_quote_char() {
    char* result = (char*)malloc(2);
    result[0] = '"';
    result[1] = '\0';
    return result;
}

/* Get newline character as a string */
char* __wear_newline_char() {
    char* result = (char*)malloc(2);
    result[0] = '\n';
    result[1] = '\0';
    return result;
}

/* Check if character is a newline (returns 1 if newline, 0 otherwise) */
int __wear_is_newline(const char* s) {
    if (s == NULL || s[0] == '\0') return 0;
    return (s[0] == '\n' || s[0] == '\r') ? 1 : 0;
}

/* ============================================================
 * File I/O Operations
 * ============================================================ */

/* Read file contents */
char* __wear_read_file(const char* filename) {
    FILE* file = fopen(filename, "rb");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot open file '%s'\n", filename);
        return (char*)malloc(1);  /* Return empty string */
    }
    
    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    char* content = (char*)malloc(length + 1);
    if (content == NULL) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        fclose(file);
        exit(1);
    }
    
    fread(content, 1, length, file);
    content[length] = '\0';
    fclose(file);
    
    return content;
}

/* Write file contents */
void __wear_write_file(const char* filename, const char* content) {
    FILE* file = fopen(filename, "wb");
    if (file == NULL) {
        fprintf(stderr, "Error: Cannot write to file '%s'\n", filename);
        return;
    }
    
    fwrite(content, 1, strlen(content), file);
    fclose(file);
}

/* ============================================================
 * Input Operations
 * ============================================================ */

/* Input from user */
char* __wear_input(const char* prompt) {
    if (prompt != NULL && prompt[0] != '\0') {
        printf("%s", prompt);
        fflush(stdout);
    }
    
    char* buffer = (char*)malloc(256);
    if (buffer == NULL) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        exit(1);
    }
    
    if (fgets(buffer, 256, stdin) != NULL) {
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len-1] == '\n') {
            buffer[len-1] = '\0';
        }
    } else {
        buffer[0] = '\0';
    }
    
    return buffer;
}

/* ============================================================
 * Print Operations
 * ============================================================ */

/* Print string */
void __wear_print_str(const char* s) {
    printf("%s\n", s);
}

/* Print integer */
void __wear_print_int(int n) {
    printf("%d\n", n);
}

/* ============================================================ */

/* Forward declarations for self-hosted compiler functions */
char* process_imports(char* src);
int is_string_varname(char* name);
int returns_string(char* fn);
int returns_int(char* fn);
int is_quote(char* c);
int is_newline(char* c);
int is_digit(char* c);
int is_letter(char* c);
int is_space(char* c);
