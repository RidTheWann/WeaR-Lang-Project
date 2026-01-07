/**
 * WeaR Lang Stage-0 Bootstrap Compiler
 * 
 * A source-to-source transpiler that compiles WeaR Lang (.wr) to C code (.c).
 * This is the first step toward bootstrapping WeaR Lang.
 * 
 * Features:
 * - Variables (var)
 * - Print statements (cetak/print)
 * - While loops (selama/while)
 * - If/Else statements (jika/lainnya)
 * - Function declarations (fungsi/function)
 * - Function calls
 * - Return statements (kembalikan/return)
 * - File I/O (baca_file/tulis_file)
 * - String concatenation with runtime helper
 * 
 * Author: Ridwan Gatro
 * License: MIT
 * 
 * Compile: g++ -std=c++17 -O2 -o wearc wear_bootstrap.cpp
 * Usage:   wearc input.wr [-o output.c] [--compile]
 */

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <cctype>
#include <cstdlib>

// ============================================================
// WeaR Runtime Library (injected into generated C code)
// ============================================================

const char* WEAR_RUNTIME = R"(
/* ============================================================
 * WeaR Lang Runtime Library
 * ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* String concatenation helper */
char* __wear_concat(const char* a, const char* b) {
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
    char* result = __wear_concat(s, num_str);
    free(num_str);
    return result;
}

/* Int + string concatenation */
char* __wear_concat_int_str(int n, const char* s) {
    char* num_str = __wear_int_to_str(n);
    char* result = __wear_concat(num_str, s);
    free(num_str);
    return result;
}

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

/* Print string */
void __wear_print_str(const char* s) {
    printf("%s\n", s);
}

/* Print integer */
void __wear_print_int(int n) {
    printf("%d\n", n);
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

/* ============================================================ */

)";

// ============================================================
// Token Types
// ============================================================

enum class TokenType {
    // Keywords
    VAR,
    CETAK,      // print
    SELAMA,     // while
    JIKA,       // if
    LAINNYA,    // else
    FUNGSI,     // function
    KEMBALIKAN, // return
    BACA_FILE,  // read_file
    TULIS_FILE, // write_file
    SAMA,       // string equality
    PANJANG,    // string length
    CHAR_AT,    // character at index
    IS_QUOTE,   // check if character is quote
    QUOTE_CHAR, // get quote character
    IS_NEWLINE, // check if character is newline
    NEWLINE_CHAR, // get newline character
    
    // Literals
    INTEGER,
    STRING,
    IDENTIFIER,
    
    // Operators
    PLUS,
    MINUS,
    STAR,
    SLASH,
    EQUAL,
    LESS,
    GREATER,
    LESS_EQUAL,
    GREATER_EQUAL,
    EQUAL_EQUAL,
    NOT_EQUAL,
    
    // Delimiters
    LPAREN,
    RPAREN,
    LBRACE,
    RBRACE,
    LBRACKET,
    RBRACKET,
    SEMICOLON,
    COMMA,
    NEWLINE,    // Line terminator
    
    // Special
    END_OF_FILE,
    UNKNOWN
};

// ============================================================
// Token Structure
// ============================================================

struct Token {
    TokenType type;
    std::string value;
    int line;
    int column;
    
    Token(TokenType t, const std::string& v, int l, int c)
        : type(t), value(v), line(l), column(c) {}
};

// ============================================================
// Lexer
// ============================================================

class Lexer {
private:
    std::string source;
    size_t pos = 0;
    int line = 1;
    int column = 1;
    
    std::unordered_map<std::string, TokenType> keywords;
    
    char current() const {
        return pos < source.length() ? source[pos] : '\0';
    }
    
    char peek(int offset = 1) const {
        size_t idx = pos + offset;
        return idx < source.length() ? source[idx] : '\0';
    }
    
    void advance() {
        if (current() == '\n') {
            line++;
            column = 1;
        } else {
            column++;
        }
        pos++;
    }
    
    void skipWhitespace() {
        // Skip spaces and tabs, but NOT newlines (they're significant)
        while (current() == ' ' || current() == '\t' || current() == '\r') {
            advance();
        }
    }
    
    void skipLineComment() {
        while (current() != '\n' && current() != '\0') {
            advance();
        }
    }
    
    Token scanString() {
        int startLine = line;
        int startCol = column;
        advance(); // skip opening quote
        
        std::string value;
        while (current() != '"' && current() != '\0') {
            if (current() == '\\' && peek() == '"') {
                advance();
                value += '"';
            } else if (current() == '\\' && peek() == 'n') {
                advance();
                advance();
                value += "\\n";
            } else {
                value += current();
                advance();
            }
        }
        
        if (current() == '"') {
            advance(); // skip closing quote
        }
        
        return Token(TokenType::STRING, value, startLine, startCol);
    }
    
    Token scanNumber() {
        int startLine = line;
        int startCol = column;
        std::string value;
        
        while (std::isdigit(current())) {
            value += current();
            advance();
        }
        
        return Token(TokenType::INTEGER, value, startLine, startCol);
    }
    
    Token scanIdentifier() {
        int startLine = line;
        int startCol = column;
        std::string value;
        
        while (std::isalnum(current()) || current() == '_') {
            value += current();
            advance();
        }
        
        auto it = keywords.find(value);
        if (it != keywords.end()) {
            return Token(it->second, value, startLine, startCol);
        }
        
        return Token(TokenType::IDENTIFIER, value, startLine, startCol);
    }

public:
    explicit Lexer(const std::string& src) : source(src) {
        // Indonesian keywords
        keywords["var"] = TokenType::VAR;
        keywords["cetak"] = TokenType::CETAK;
        keywords["selama"] = TokenType::SELAMA;
        keywords["jika"] = TokenType::JIKA;
        keywords["lainnya"] = TokenType::LAINNYA;
        keywords["fungsi"] = TokenType::FUNGSI;
        keywords["kembalikan"] = TokenType::KEMBALIKAN;
        keywords["baca_file"] = TokenType::BACA_FILE;
        keywords["tulis_file"] = TokenType::TULIS_FILE;
        
        // English keywords (aliases)
        keywords["print"] = TokenType::CETAK;
        keywords["while"] = TokenType::SELAMA;
        keywords["if"] = TokenType::JIKA;
        keywords["else"] = TokenType::LAINNYA;
        keywords["function"] = TokenType::FUNGSI;
        keywords["return"] = TokenType::KEMBALIKAN;
        keywords["read_file"] = TokenType::BACA_FILE;
        keywords["write_file"] = TokenType::TULIS_FILE;
        keywords["sama"] = TokenType::SAMA;
        keywords["panjang"] = TokenType::PANJANG;
        keywords["char_at"] = TokenType::CHAR_AT;
        keywords["is_quote"] = TokenType::IS_QUOTE;
        keywords["quote_char"] = TokenType::QUOTE_CHAR;
        keywords["is_newline"] = TokenType::IS_NEWLINE;
        keywords["newline_char"] = TokenType::NEWLINE_CHAR;
        keywords["streq"] = TokenType::SAMA;      // English alias
        keywords["strlen"] = TokenType::PANJANG;  // English alias
    }
    
    std::vector<Token> tokenize() {
        std::vector<Token> tokens;
        
        while (pos < source.length()) {
            skipWhitespace();
            
            if (current() == '\0') break;
            
            int startLine = line;
            int startCol = column;
            
            // Newlines (statement terminators)
            if (current() == '\n') {
                tokens.push_back(Token(TokenType::NEWLINE, "\\n", startLine, startCol));
                advance();
                continue;
            }
            
            // Comments
            if (current() == '/' && peek() == '/') {
                skipLineComment();
                continue;
            }
            
            // String literals
            if (current() == '"') {
                tokens.push_back(scanString());
                continue;
            }
            
            // Numbers
            if (std::isdigit(current())) {
                tokens.push_back(scanNumber());
                continue;
            }
            
            // Identifiers and keywords
            if (std::isalpha(current()) || current() == '_') {
                tokens.push_back(scanIdentifier());
                continue;
            }
            
            // Operators and delimiters
            switch (current()) {
                case '+':
                    tokens.push_back(Token(TokenType::PLUS, "+", startLine, startCol));
                    advance();
                    break;
                case '-':
                    tokens.push_back(Token(TokenType::MINUS, "-", startLine, startCol));
                    advance();
                    break;
                case '*':
                    tokens.push_back(Token(TokenType::STAR, "*", startLine, startCol));
                    advance();
                    break;
                case '/':
                    tokens.push_back(Token(TokenType::SLASH, "/", startLine, startCol));
                    advance();
                    break;
                case '=':
                    advance();
                    if (current() == '=') {
                        tokens.push_back(Token(TokenType::EQUAL_EQUAL, "==", startLine, startCol));
                        advance();
                    } else {
                        tokens.push_back(Token(TokenType::EQUAL, "=", startLine, startCol));
                    }
                    break;
                case '<':
                    advance();
                    if (current() == '=') {
                        tokens.push_back(Token(TokenType::LESS_EQUAL, "<=", startLine, startCol));
                        advance();
                    } else {
                        tokens.push_back(Token(TokenType::LESS, "<", startLine, startCol));
                    }
                    break;
                case '>':
                    advance();
                    if (current() == '=') {
                        tokens.push_back(Token(TokenType::GREATER_EQUAL, ">=", startLine, startCol));
                        advance();
                    } else {
                        tokens.push_back(Token(TokenType::GREATER, ">", startLine, startCol));
                    }
                    break;
                case '!':
                    advance();
                    if (current() == '=') {
                        tokens.push_back(Token(TokenType::NOT_EQUAL, "!=", startLine, startCol));
                        advance();
                    } else {
                        tokens.push_back(Token(TokenType::UNKNOWN, "!", startLine, startCol));
                    }
                    break;
                case '(':
                    tokens.push_back(Token(TokenType::LPAREN, "(", startLine, startCol));
                    advance();
                    break;
                case ')':
                    tokens.push_back(Token(TokenType::RPAREN, ")", startLine, startCol));
                    advance();
                    break;
                case '{':
                    tokens.push_back(Token(TokenType::LBRACE, "{", startLine, startCol));
                    advance();
                    break;
                case '}':
                    tokens.push_back(Token(TokenType::RBRACE, "}", startLine, startCol));
                    advance();
                    break;
                case '[':
                    tokens.push_back(Token(TokenType::LBRACKET, "[", startLine, startCol));
                    advance();
                    break;
                case ']':
                    tokens.push_back(Token(TokenType::RBRACKET, "]", startLine, startCol));
                    advance();
                    break;
                case ';':
                    tokens.push_back(Token(TokenType::SEMICOLON, ";", startLine, startCol));
                    advance();
                    break;
                case ',':
                    tokens.push_back(Token(TokenType::COMMA, ",", startLine, startCol));
                    advance();
                    break;
                default:
                    tokens.push_back(Token(TokenType::UNKNOWN, std::string(1, current()), startLine, startCol));
                    advance();
                    break;
            }
        }
        
        tokens.push_back(Token(TokenType::END_OF_FILE, "", line, column));
        return tokens;
    }
};

// ============================================================
// Expression Type (for type inference)
// ============================================================

enum class ExprType {
    INT,
    STRING,
    UNKNOWN
};

// Expression result with type info
struct ExprResult {
    std::string code;
    ExprType type;
    
    ExprResult(const std::string& c, ExprType t) : code(c), type(t) {}
    ExprResult() : code(""), type(ExprType::UNKNOWN) {}
};

// ============================================================
// Code Generator (Transpiler to C)
// ============================================================

class CodeGenerator {
private:
    std::vector<Token> tokens;
    size_t pos = 0;
    std::ostringstream functionsOutput;  // Functions go here (before main)
    std::ostringstream mainOutput;       // Main code goes here
    std::ostringstream* currentOutput;   // Pointer to current output stream
    int indentLevel = 1;
    bool inFunction = false;
    std::unordered_set<std::string> declaredFunctions;
    std::unordered_map<std::string, ExprType> varTypes;
    
    Token current() const {
        return pos < tokens.size() ? tokens[pos] : tokens.back();
    }
    
    Token peek(int offset = 1) const {
        size_t idx = pos + offset;
        return idx < tokens.size() ? tokens[idx] : tokens.back();
    }
    
    void advance() {
        if (pos < tokens.size()) pos++;
    }
    
    bool match(TokenType type) {
        if (current().type == type) {
            advance();
            return true;
        }
        return false;
    }
    
    bool check(TokenType type) const {
        return current().type == type;
    }
    
    void expect(TokenType type, const std::string& message) {
        if (!match(type)) {
            std::cerr << "Error at line " << current().line 
                      << ", column " << current().column 
                      << ": " << message << std::endl;
            std::exit(1);
        }
    }
    
    std::string indent() const {
        return std::string(indentLevel * 4, ' ');
    }
    
    void emitLine(const std::string& code) {
        *currentOutput << indent() << code << "\n";
    }
    
    void emit(const std::string& code) {
        *currentOutput << code;
    }
    
    // Check if identifier is a string variable
    bool isStringVar(const std::string& name) {
        auto it = varTypes.find(name);
        return it != varTypes.end() && it->second == ExprType::STRING;
    }
    
    ExprResult generateTypedExpression() {
        std::vector<std::pair<std::string, ExprType>> parts;
        int parenDepth = 0;
        
        while (!check(TokenType::END_OF_FILE)) {
            Token tok = current();
            
            // Stop conditions (outside parens)
            if (parenDepth == 0) {
                if (tok.type == TokenType::RPAREN ||
                    tok.type == TokenType::LBRACE ||
                    tok.type == TokenType::RBRACE ||
                    tok.type == TokenType::COMMA ||
                    tok.type == TokenType::SEMICOLON ||
                    tok.type == TokenType::NEWLINE) {
                    break;
                }
            }
            
            if (tok.type == TokenType::STRING) {
                parts.push_back({"\"" + tok.value + "\"", ExprType::STRING});
                advance();
            } else if (tok.type == TokenType::INTEGER) {
                parts.push_back({tok.value, ExprType::INT});
                advance();
            } else if (tok.type == TokenType::BACA_FILE) {
                // baca_file("filename")
                advance();
                expect(TokenType::LPAREN, "Expected '(' after 'baca_file'");
                auto arg = generateTypedExpression();
                expect(TokenType::RPAREN, "Expected ')'");
                parts.push_back({"__wear_read_file(" + arg.code + ")", ExprType::STRING});
            } else if (tok.type == TokenType::SAMA) {
                // sama(str1, str2) - string comparison
                advance();
                expect(TokenType::LPAREN, "Expected '(' after 'sama'");
                auto arg1 = generateTypedExpression();
                expect(TokenType::COMMA, "Expected ',' between arguments");
                auto arg2 = generateTypedExpression();
                expect(TokenType::RPAREN, "Expected ')'");
                parts.push_back({"__wear_streq(" + arg1.code + ", " + arg2.code + ")", ExprType::INT});
            } else if (tok.type == TokenType::PANJANG) {
                // panjang(str) - string length
                advance();
                expect(TokenType::LPAREN, "Expected '(' after 'panjang'");
                auto arg = generateTypedExpression();
                expect(TokenType::RPAREN, "Expected ')'");
                parts.push_back({"__wear_strlen(" + arg.code + ")", ExprType::INT});
            } else if (tok.type == TokenType::CHAR_AT) {
                // char_at(str, index) - character at index
                advance();
                expect(TokenType::LPAREN, "Expected '(' after 'char_at'");
                auto str = generateTypedExpression();
                expect(TokenType::COMMA, "Expected ',' between arguments");
                auto idx = generateTypedExpression();
                expect(TokenType::RPAREN, "Expected ')'");
                parts.push_back({"__wear_char_at(" + str.code + ", " + idx.code + ")", ExprType::STRING});
            } else if (tok.type == TokenType::IS_QUOTE) {
                // is_quote(char) - check if character is quote
                advance();
                expect(TokenType::LPAREN, "Expected '(' after 'is_quote'");
                auto arg = generateTypedExpression();
                expect(TokenType::RPAREN, "Expected ')'");
                parts.push_back({"__wear_is_quote(" + arg.code + ")", ExprType::INT});
            } else if (tok.type == TokenType::QUOTE_CHAR) {
                // quote_char() - get quote character as string
                advance();
                expect(TokenType::LPAREN, "Expected '(' after 'quote_char'");
                expect(TokenType::RPAREN, "Expected ')'");
                parts.push_back({"__wear_quote_char()", ExprType::STRING});
            } else if (tok.type == TokenType::IS_NEWLINE) {
                // is_newline(char) - check if character is newline
                advance();
                expect(TokenType::LPAREN, "Expected '(' after 'is_newline'");
                auto arg = generateTypedExpression();
                expect(TokenType::RPAREN, "Expected ')'");
                parts.push_back({"__wear_is_newline(" + arg.code + ")", ExprType::INT});
            } else if (tok.type == TokenType::NEWLINE_CHAR) {
                // newline_char() - get newline character as string
                advance();
                expect(TokenType::LPAREN, "Expected '(' after 'newline_char'");
                expect(TokenType::RPAREN, "Expected ')'");
                parts.push_back({"__wear_newline_char()", ExprType::STRING});
            } else if (tok.type == TokenType::IDENTIFIER) {
                std::string name = tok.value;
                advance();
                
                // Check for function call
                if (check(TokenType::LPAREN)) {
                    std::ostringstream call;
                    call << name << "(";
                    expect(TokenType::LPAREN, "Expected '('");
                    
                    bool first = true;
                    while (!check(TokenType::RPAREN) && !check(TokenType::END_OF_FILE)) {
                        if (!first) {
                            expect(TokenType::COMMA, "Expected ','");
                            call << ", ";
                        }
                        first = false;
                        auto arg = generateTypedExpression();
                        call << arg.code;
                    }
                    
                    expect(TokenType::RPAREN, "Expected ')'");
                    call << ")";
                    
                    // Assume function returns int (could be enhanced)
                    parts.push_back({call.str(), ExprType::INT});
                } else {
                    // Variable reference
                    ExprType vType = isStringVar(name) ? ExprType::STRING : ExprType::INT;
                    parts.push_back({name, vType});
                }
            } else if (tok.type == TokenType::PLUS) {
                parts.push_back({"+", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::MINUS) {
                parts.push_back({"-", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::STAR) {
                parts.push_back({"*", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::SLASH) {
                parts.push_back({"/", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::LESS) {
                parts.push_back({"<", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::GREATER) {
                parts.push_back({">", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::LESS_EQUAL) {
                parts.push_back({"<=", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::GREATER_EQUAL) {
                parts.push_back({">=", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::EQUAL_EQUAL) {
                parts.push_back({"==", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::NOT_EQUAL) {
                parts.push_back({"!=", ExprType::UNKNOWN});
                advance();
            } else if (tok.type == TokenType::LPAREN) {
                parts.push_back({"(", ExprType::UNKNOWN});
                parenDepth++;
                advance();
            } else if (tok.type == TokenType::RPAREN) {
                parts.push_back({")", ExprType::UNKNOWN});
                parenDepth--;
                advance();
            } else {
                break;
            }
        }
        
        // Check if this is a string concatenation expression
        bool hasString = false;
        bool hasPlus = false;
        for (const auto& p : parts) {
            if (p.second == ExprType::STRING) hasString = true;
            if (p.first == "+") hasPlus = true;
        }
        
        if (hasString && hasPlus && parts.size() >= 3) {
            // Build string concatenation chain
            return buildStringConcat(parts);
        }
        
        // Regular expression
        std::ostringstream result;
        ExprType resultType = ExprType::INT;
        for (const auto& p : parts) {
            result << p.first;
            if (p.second == ExprType::STRING) resultType = ExprType::STRING;
        }
        
        return ExprResult(result.str(), resultType);
    }
    
    ExprResult buildStringConcat(const std::vector<std::pair<std::string, ExprType>>& parts) {
        // Build a chain of __wear_concat calls
        std::vector<std::pair<std::string, ExprType>> operands;
        
        for (const auto& p : parts) {
            if (p.first != "+" && p.first != " ") {
                operands.push_back(p);
            }
        }
        
        if (operands.empty()) {
            return ExprResult("\"\"", ExprType::STRING);
        }
        
        if (operands.size() == 1) {
            return ExprResult(operands[0].first, operands[0].second);
        }
        
        // Build nested concat calls
        std::string result = operands[0].first;
        ExprType prevType = operands[0].second;
        
        for (size_t i = 1; i < operands.size(); i++) {
            std::string op = operands[i].first;
            ExprType opType = operands[i].second;
            
            if (prevType == ExprType::STRING && opType == ExprType::STRING) {
                result = "__wear_concat(" + result + ", " + op + ")";
            } else if (prevType == ExprType::STRING && opType == ExprType::INT) {
                result = "__wear_concat_str_int(" + result + ", " + op + ")";
            } else if (prevType == ExprType::INT && opType == ExprType::STRING) {
                result = "__wear_concat_int_str(" + result + ", " + op + ")";
            } else {
                // Both int - just add
                result = "(" + result + " + " + op + ")";
            }
            
            // Result of concat is always string
            if (prevType == ExprType::STRING || opType == ExprType::STRING) {
                prevType = ExprType::STRING;
            }
        }
        
        return ExprResult(result, ExprType::STRING);
    }
    
    // Simple expression for conditions (no string concat)
    std::string generateExpression() {
        auto result = generateTypedExpression();
        return result.code;
    }
    
    // Generate print statement
    void generatePrint() {
        advance(); // skip 'cetak'
        
        auto expr = generateTypedExpression();
        
        if (expr.type == ExprType::STRING) {
            emitLine("__wear_print_str(" + expr.code + ");");
        } else {
            emitLine("__wear_print_int(" + expr.code + ");");
        }
    }
    
    // Generate variable declaration
    void generateVarDecl() {
        advance(); // skip 'var'
        
        std::string varName = current().value;
        advance(); // skip identifier
        
        expect(TokenType::EQUAL, "Expected '=' after variable name");
        
        // Check for baca_file or string literal
        if (check(TokenType::STRING)) {
            std::string value = current().value;
            advance();
            emitLine("char* " + varName + " = \"" + value + "\";");
            varTypes[varName] = ExprType::STRING;
        } else if (check(TokenType::BACA_FILE)) {
            advance();
            expect(TokenType::LPAREN, "Expected '(' after 'baca_file'");
            auto arg = generateTypedExpression();
            expect(TokenType::RPAREN, "Expected ')'");
            emitLine("char* " + varName + " = __wear_read_file(" + arg.code + ");");
            varTypes[varName] = ExprType::STRING;
        } else {
            auto expr = generateTypedExpression();
            if (expr.type == ExprType::STRING) {
                emitLine("char* " + varName + " = " + expr.code + ";");
                varTypes[varName] = ExprType::STRING;
            } else {
                emitLine("int " + varName + " = " + expr.code + ";");
                varTypes[varName] = ExprType::INT;
            }
        }
    }
    
    // Generate while loop
    void generateWhile() {
        advance(); // skip 'selama'
        
        expect(TokenType::LPAREN, "Expected '(' after 'selama'");
        std::string condition = generateExpression();
        expect(TokenType::RPAREN, "Expected ')' after condition");
        
        emitLine("while (" + condition + ") {");
        
        expect(TokenType::LBRACE, "Expected '{' to start while body");
        indentLevel++;
        
        while (!check(TokenType::RBRACE) && !check(TokenType::END_OF_FILE)) {
            generateStatement();
        }
        
        indentLevel--;
        expect(TokenType::RBRACE, "Expected '}' to end while body");
        emitLine("}");
    }
    
    // Generate if statement
    void generateIf() {
        advance(); // skip 'jika'
        
        expect(TokenType::LPAREN, "Expected '(' after 'jika'");
        std::string condition = generateExpression();
        expect(TokenType::RPAREN, "Expected ')' after condition");
        
        emitLine("if (" + condition + ") {");
        
        expect(TokenType::LBRACE, "Expected '{' to start if body");
        indentLevel++;
        
        while (!check(TokenType::RBRACE) && !check(TokenType::END_OF_FILE)) {
            generateStatement();
        }
        
        indentLevel--;
        expect(TokenType::RBRACE, "Expected '}' to end if body");
        emitLine("}");
        
        // Handle else
        if (check(TokenType::LAINNYA)) {
            advance();
            if (check(TokenType::JIKA)) {
                *currentOutput << indent() << "else ";
                generateIf();
            } else {
                emitLine("else {");
                expect(TokenType::LBRACE, "Expected '{' after 'lainnya'");
                indentLevel++;
                
                while (!check(TokenType::RBRACE) && !check(TokenType::END_OF_FILE)) {
                    generateStatement();
                }
                
                indentLevel--;
                expect(TokenType::RBRACE, "Expected '}' to end else body");
                emitLine("}");
            }
        }
    }
    
    // Generate function declaration
    void generateFunctionDecl() {
        advance(); // skip 'fungsi'
        
        std::string funcName = current().value;
        advance(); // skip function name
        
        declaredFunctions.insert(funcName);
        
        expect(TokenType::LPAREN, "Expected '(' after function name");
        
        // Parse parameters
        std::vector<std::string> params;
        while (!check(TokenType::RPAREN) && !check(TokenType::END_OF_FILE)) {
            if (!params.empty()) {
                expect(TokenType::COMMA, "Expected ',' between parameters");
            }
            
            if (check(TokenType::IDENTIFIER)) {
                params.push_back(current().value);
                advance();
            }
        }
        
        expect(TokenType::RPAREN, "Expected ')' after parameters");
        
        // Generate C function signature (char* params for string support)
        std::ostringstream funcSig;
        funcSig << "int " << funcName << "(";
        for (size_t i = 0; i < params.size(); i++) {
            if (i > 0) funcSig << ", ";
            funcSig << "char* " << params[i];
        }
        funcSig << ") {";
        
        // Switch to functions output
        std::ostringstream* prevOutput = currentOutput;
        currentOutput = &functionsOutput;
        int prevIndent = indentLevel;
        indentLevel = 1;
        inFunction = true;
        
        functionsOutput << funcSig.str() << "\n";
        
        expect(TokenType::LBRACE, "Expected '{' to start function body");
        
        while (!check(TokenType::RBRACE) && !check(TokenType::END_OF_FILE)) {
            generateStatement();
        }
        
        expect(TokenType::RBRACE, "Expected '}' to end function body");
        
        functionsOutput << "}\n\n";
        
        // Switch back to main output
        inFunction = false;
        indentLevel = prevIndent;
        currentOutput = prevOutput;
    }
    
    // Generate return statement
    void generateReturn() {
        advance(); // skip 'kembalikan'
        
        std::string expr = generateExpression();
        emitLine("return " + expr + ";");
    }
    
    // Generate tulis_file (write_file)
    void generateWriteFile() {
        advance(); // skip 'tulis_file'
        
        expect(TokenType::LPAREN, "Expected '(' after 'tulis_file'");
        
        auto filename = generateTypedExpression();
        expect(TokenType::COMMA, "Expected ',' between arguments");
        auto content = generateTypedExpression();
        
        expect(TokenType::RPAREN, "Expected ')'");
        
        emitLine("__wear_write_file(" + filename.code + ", " + content.code + ");");
    }
    
    // Generate single statement
    void generateStatement() {
        // Skip any newlines
        while (check(TokenType::NEWLINE)) {
            advance();
        }
        
        // Return early if we hit block end or file end
        if (check(TokenType::RBRACE) || check(TokenType::END_OF_FILE)) {
            return;
        }
        
        switch (current().type) {
            case TokenType::VAR:
                generateVarDecl();
                break;
            case TokenType::CETAK:
                generatePrint();
                break;
            case TokenType::SELAMA:
                generateWhile();
                break;
            case TokenType::JIKA:
                generateIf();
                break;
            case TokenType::FUNGSI:
                generateFunctionDecl();
                break;
            case TokenType::KEMBALIKAN:
                generateReturn();
                break;
            case TokenType::TULIS_FILE:
                generateWriteFile();
                break;
            case TokenType::BACA_FILE:
                // baca_file as statement (result ignored)
                {
                    advance();
                    expect(TokenType::LPAREN, "Expected '('");
                    auto arg = generateTypedExpression();
                    expect(TokenType::RPAREN, "Expected ')'");
                    emitLine("__wear_read_file(" + arg.code + ");");
                }
                break;
            case TokenType::IDENTIFIER:
                {
                    std::string name = current().value;
                    advance();
                    
                    if (match(TokenType::EQUAL)) {
                        // Assignment
                        auto expr = generateTypedExpression();
                        emitLine(name + " = " + expr.code + ";");
                    } else if (match(TokenType::LPAREN)) {
                        // Function call as statement
                        std::ostringstream call;
                        call << name << "(";
                        
                        bool first = true;
                        while (!check(TokenType::RPAREN) && !check(TokenType::END_OF_FILE)) {
                            if (!first) {
                                expect(TokenType::COMMA, "Expected ','");
                                call << ", ";
                            }
                            first = false;
                            auto arg = generateTypedExpression();
                            call << arg.code;
                        }
                        
                        expect(TokenType::RPAREN, "Expected ')'");
                        call << ")";
                        
                        emitLine(call.str() + ";");
                    }
                }
                break;
            default:
                advance(); // Skip unknown tokens
                break;
        }
    }

public:
    explicit CodeGenerator(const std::vector<Token>& toks) : tokens(toks) {
        currentOutput = &mainOutput;
    }
    
    std::string generate() {
        std::ostringstream finalOutput;
        
        // Generate all statements (functions go to functionsOutput, main code to mainOutput)
        while (!check(TokenType::END_OF_FILE)) {
            generateStatement();
        }
        
        // Assemble final output
        finalOutput << "/* Generated by WeaR Lang Stage-0 Compiler */\n";
        
        // Inject runtime library
        finalOutput << WEAR_RUNTIME;
        
        // Output functions BEFORE main
        if (!functionsOutput.str().empty()) {
            finalOutput << "// User-defined functions\n";
            finalOutput << functionsOutput.str();
        }
        
        // Output main function
        finalOutput << "int main(int argc, char* argv[]) {\n";
        finalOutput << mainOutput.str();
        finalOutput << "\n    return 0;\n";
        finalOutput << "}\n";
        
        return finalOutput.str();
    }
};

// ============================================================
// File I/O Utilities
// ============================================================

std::string readFile(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "Error: Cannot open file '" << path << "'" << std::endl;
        std::exit(1);
    }
    
    std::ostringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

void writeFile(const std::string& path, const std::string& content) {
    std::ofstream file(path);
    if (!file.is_open()) {
        std::cerr << "Error: Cannot write to file '" << path << "'" << std::endl;
        std::exit(1);
    }
    file << content;
}

// ============================================================
// Main Entry Point
// ============================================================

void printUsage(const char* programName) {
    std::cout << "WeaR Lang Stage-0 Compiler (Transpiler to C)\n";
    std::cout << "Usage: " << programName << " <input.wr> [-o output.c] [--compile]\n\n";
    std::cout << "Options:\n";
    std::cout << "  -o <file>    Output C file (default: output.c)\n";
    std::cout << "  --compile    Compile generated C code with GCC\n";
    std::cout << "  --run        Compile and run the program\n";
    std::cout << "  --help       Show this help message\n";
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printUsage(argv[0]);
        return 1;
    }
    
    std::string inputFile;
    std::string outputFile = "output.c";
    bool compile = false;
    bool run = false;
    
    // Parse command line arguments
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        
        if (arg == "--help" || arg == "-h") {
            printUsage(argv[0]);
            return 0;
        } else if (arg == "-o" && i + 1 < argc) {
            outputFile = argv[++i];
        } else if (arg == "--compile") {
            compile = true;
        } else if (arg == "--run") {
            compile = true;
            run = true;
        } else if (arg[0] != '-') {
            inputFile = arg;
        }
    }
    
    if (inputFile.empty()) {
        std::cerr << "Error: No input file specified\n";
        return 1;
    }
    
    std::cout << "[WeaR Compiler] Reading: " << inputFile << std::endl;
    
    // Read source file
    std::string source = readFile(inputFile);
    
    // Tokenize
    std::cout << "[WeaR Compiler] Tokenizing..." << std::endl;
    Lexer lexer(source);
    std::vector<Token> tokens = lexer.tokenize();
    
    // Generate C code
    std::cout << "[WeaR Compiler] Generating C code..." << std::endl;
    CodeGenerator codegen(tokens);
    std::string cCode = codegen.generate();
    
    // Write output
    writeFile(outputFile, cCode);
    std::cout << "[WeaR Compiler] Generated: " << outputFile << std::endl;
    
    // Compile with GCC if requested
    if (compile) {
        std::string exeName = outputFile;
        size_t dotPos = exeName.rfind('.');
        if (dotPos != std::string::npos) {
            exeName = exeName.substr(0, dotPos);
        }
        
        #ifdef _WIN32
        exeName += ".exe";
        #endif
        
        std::string gccCmd = "gcc -O2 -o " + exeName + " " + outputFile;
        std::cout << "[WeaR Compiler] Compiling: " << gccCmd << std::endl;
        
        int result = std::system(gccCmd.c_str());
        if (result != 0) {
            std::cerr << "[WeaR Compiler] GCC compilation failed" << std::endl;
            return 1;
        }
        
        std::cout << "[WeaR Compiler] Built: " << exeName << std::endl;
        
        // Run if requested
        if (run) {
            std::cout << "[WeaR Compiler] Running: " << exeName << std::endl;
            std::cout << "----------------------------------------\n";
            
            #ifdef _WIN32
            std::system(exeName.c_str());
            #else
            std::system(("./" + exeName).c_str());
            #endif
        }
    }
    
    return 0;
}
