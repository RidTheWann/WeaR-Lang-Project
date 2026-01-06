"use strict";
(() => {
  var __defProp = Object.defineProperty;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __publicField = (obj, key, value) => {
    __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
    return value;
  };

  // src/types/tokens.ts
  function createToken(type, lexeme, literal, line, column) {
    return { type, lexeme, literal, line, column };
  }

  // src/types/config.ts
  function createReversedKeywordMap(config) {
    const reversed = /* @__PURE__ */ new Map();
    for (const [canonical, localized] of Object.entries(config.keywords)) {
      reversed.set(localized, canonical);
    }
    return reversed;
  }

  // src/types/ast.ts
  function createProgram(body, line = 1, column = 1) {
    return { type: "Program", body, line, column };
  }
  function createIdentifier(name, line, column) {
    return { type: "Identifier", name, line, column };
  }
  function createNumericLiteral(value, line, column) {
    return { type: "NumericLiteral", value, line, column };
  }
  function createStringLiteral(value, line, column) {
    return { type: "StringLiteral", value, line, column };
  }
  function createBooleanLiteral(value, line, column) {
    return { type: "BooleanLiteral", value, line, column };
  }
  function createNullLiteral(line, column) {
    return { type: "NullLiteral", value: null, line, column };
  }

  // src/utils/error-reporter.ts
  var ErrorReporter = class {
    constructor() {
      __publicField(this, "errors", []);
      __publicField(this, "source", "");
      __publicField(this, "sourceLines", []);
    }
    /**
     * Set the source code for snippet extraction
     */
    setSource(source) {
      this.source = source;
      this.sourceLines = source.split("\n");
    }
    /**
     * Report an error with a friendly message
     */
    reportError(message, line, column, expected, found) {
      let friendlyMessage = `\u274C I found an error on line ${line}`;
      if (column > 0) {
        friendlyMessage += `, column ${column}`;
      }
      friendlyMessage += ".\n";
      if (expected && found) {
        friendlyMessage += `   I was expecting ${expected}, but found '${found}' instead.
`;
      } else if (expected) {
        friendlyMessage += `   I was expecting ${expected}.
`;
      } else {
        friendlyMessage += `   ${message}
`;
      }
      let sourceSnippet;
      if (this.sourceLines.length >= line && line > 0) {
        const sourceLine = this.sourceLines[line - 1];
        sourceSnippet = `
   ${line} | ${sourceLine}
`;
        if (column > 0) {
          const padding = " ".repeat(String(line).length + 3 + column - 1);
          sourceSnippet += `${padding}^
`;
        }
      }
      const error = {
        message,
        line,
        column,
        friendlyMessage: friendlyMessage + (sourceSnippet || ""),
        sourceSnippet
      };
      this.errors.push(error);
    }
    /**
     * Report an unexpected token error
     */
    reportUnexpectedToken(token, expected) {
      const found = token.type === "EOF" /* EOF */ ? "end of file" : token.lexeme;
      this.reportError(
        `Unexpected token: ${token.lexeme}`,
        token.line,
        token.column,
        expected,
        found
      );
    }
    /**
     * Report a syntax error
     */
    reportSyntaxError(message, line, column) {
      this.reportError(message, line, column);
    }
    /**
     * Report a runtime error
     */
    reportRuntimeError(message, line, column) {
      const friendlyMessage = `\u{1F525} Runtime error on line ${line}:
   ${message}
`;
      this.errors.push({
        message,
        line,
        column,
        friendlyMessage
      });
    }
    /**
     * Check if there are any errors
     */
    hasErrors() {
      return this.errors.length > 0;
    }
    /**
     * Get all collected errors
     */
    getErrors() {
      return [...this.errors];
    }
    /**
     * Get all error messages formatted for display
     */
    getFormattedErrors() {
      return this.errors.map((e) => e.friendlyMessage).join("\n");
    }
    /**
     * Clear all errors
     */
    clear() {
      this.errors = [];
    }
    /**
     * Get error count
     */
    count() {
      return this.errors.length;
    }
  };
  var errorReporter = new ErrorReporter();

  // src/lexer/lexer.ts
  var KEYWORD_TO_TOKEN = {
    var: "VAR" /* VAR */,
    const: "CONST" /* CONST */,
    function: "FUNCTION" /* FUNCTION */,
    return: "RETURN" /* RETURN */,
    if: "IF" /* IF */,
    else: "ELSE" /* ELSE */,
    while: "WHILE" /* WHILE */,
    for: "FOR" /* FOR */,
    and: "AND" /* AND */,
    or: "OR" /* OR */,
    print: "PRINT" /* PRINT */,
    true: "TRUE" /* TRUE */,
    false: "FALSE" /* FALSE */,
    null: "NULL" /* NULL */
  };
  var Lexer = class {
    constructor(source, config, errorReporter2) {
      __publicField(this, "source");
      __publicField(this, "tokens", []);
      __publicField(this, "start", 0);
      __publicField(this, "current", 0);
      __publicField(this, "line", 1);
      __publicField(this, "column", 1);
      __publicField(this, "lineStart", 0);
      __publicField(this, "keywordMap");
      __publicField(this, "errorReporter");
      this.source = source;
      this.keywordMap = createReversedKeywordMap(config);
      this.errorReporter = errorReporter2 || new ErrorReporter();
      this.errorReporter.setSource(source);
    }
    /**
     * Tokenize the entire source code
     */
    tokenize() {
      while (!this.isAtEnd()) {
        this.start = this.current;
        this.scanToken();
      }
      this.tokens.push(createToken(
        "EOF" /* EOF */,
        "",
        null,
        this.line,
        this.column
      ));
      return this.tokens;
    }
    /**
     * Scan a single token
     */
    scanToken() {
      const char = this.advance();
      switch (char) {
        case "(":
          this.addToken("LEFT_PAREN" /* LEFT_PAREN */);
          break;
        case ")":
          this.addToken("RIGHT_PAREN" /* RIGHT_PAREN */);
          break;
        case "{":
          this.addToken("LEFT_BRACE" /* LEFT_BRACE */);
          break;
        case "}":
          this.addToken("RIGHT_BRACE" /* RIGHT_BRACE */);
          break;
        case "[":
          this.addToken("LEFT_BRACKET" /* LEFT_BRACKET */);
          break;
        case "]":
          this.addToken("RIGHT_BRACKET" /* RIGHT_BRACKET */);
          break;
        case ",":
          this.addToken("COMMA" /* COMMA */);
          break;
        case ".":
          this.addToken("DOT" /* DOT */);
          break;
        case ":":
          this.addToken("COLON" /* COLON */);
          break;
        case "+":
          this.addToken("PLUS" /* PLUS */);
          break;
        case "-":
          this.addToken("MINUS" /* MINUS */);
          break;
        case "*":
          this.addToken("STAR" /* STAR */);
          break;
        case "%":
          this.addToken("PERCENT" /* PERCENT */);
          break;
        case "!":
          this.addToken(this.match("=") ? "BANG_EQUAL" /* BANG_EQUAL */ : "BANG" /* BANG */);
          break;
        case "=":
          this.addToken(this.match("=") ? "EQUAL_EQUAL" /* EQUAL_EQUAL */ : "EQUAL" /* EQUAL */);
          break;
        case "<":
          this.addToken(this.match("=") ? "LESS_EQUAL" /* LESS_EQUAL */ : "LESS" /* LESS */);
          break;
        case ">":
          this.addToken(this.match("=") ? "GREATER_EQUAL" /* GREATER_EQUAL */ : "GREATER" /* GREATER */);
          break;
        case "/":
          if (this.match("/")) {
            while (this.peek() !== "\n" && !this.isAtEnd()) {
              this.advance();
            }
          } else {
            this.addToken("SLASH" /* SLASH */);
          }
          break;
        case " ":
        case "\r":
        case "	":
          break;
        case "\n":
          this.line++;
          this.lineStart = this.current;
          this.column = 1;
          break;
        case '"':
          this.scanString();
          break;
        default:
          if (this.isDigit(char)) {
            this.scanNumber();
          } else if (this.isAlpha(char)) {
            this.scanIdentifier();
          } else {
            this.errorReporter.reportError(
              `Unexpected character: '${char}'`,
              this.line,
              this.getColumn(this.start)
            );
          }
      }
    }
    /**
     * Scan a string literal
     */
    scanString() {
      const startLine = this.line;
      const startColumn = this.getColumn(this.start);
      while (this.peek() !== '"' && !this.isAtEnd()) {
        if (this.peek() === "\n") {
          this.line++;
          this.lineStart = this.current + 1;
        }
        this.advance();
      }
      if (this.isAtEnd()) {
        this.errorReporter.reportError(
          "Unterminated string",
          startLine,
          startColumn,
          'a closing "',
          "end of file"
        );
        return;
      }
      this.advance();
      const value = this.source.substring(this.start + 1, this.current - 1);
      this.addToken("STRING" /* STRING */, value);
    }
    /**
     * Scan a number literal
     */
    scanNumber() {
      while (this.isDigit(this.peek())) {
        this.advance();
      }
      if (this.peek() === "." && this.isDigit(this.peekNext())) {
        this.advance();
        while (this.isDigit(this.peek())) {
          this.advance();
        }
      }
      const value = parseFloat(this.source.substring(this.start, this.current));
      this.addToken("NUMBER" /* NUMBER */, value);
    }
    /**
     * Scan an identifier or keyword
     */
    scanIdentifier() {
      while (this.isAlphaNumeric(this.peek())) {
        this.advance();
      }
      const text = this.source.substring(this.start, this.current);
      const canonical = this.keywordMap.get(text);
      if (canonical) {
        const tokenType = KEYWORD_TO_TOKEN[canonical];
        if (tokenType === "TRUE" /* TRUE */) {
          this.addToken(tokenType, true);
        } else if (tokenType === "FALSE" /* FALSE */) {
          this.addToken(tokenType, false);
        } else if (tokenType === "NULL" /* NULL */) {
          this.addToken(tokenType, null);
        } else {
          this.addToken(tokenType);
        }
      } else {
        this.addToken("IDENTIFIER" /* IDENTIFIER */);
      }
    }
    // ============================================================
    // Helper Methods
    // ============================================================
    isAtEnd() {
      return this.current >= this.source.length;
    }
    advance() {
      const char = this.source.charAt(this.current);
      this.current++;
      this.column++;
      return char;
    }
    peek() {
      if (this.isAtEnd())
        return "\0";
      return this.source.charAt(this.current);
    }
    peekNext() {
      if (this.current + 1 >= this.source.length)
        return "\0";
      return this.source.charAt(this.current + 1);
    }
    match(expected) {
      if (this.isAtEnd())
        return false;
      if (this.source.charAt(this.current) !== expected)
        return false;
      this.current++;
      this.column++;
      return true;
    }
    isDigit(char) {
      return char >= "0" && char <= "9";
    }
    isAlpha(char) {
      return char >= "a" && char <= "z" || char >= "A" && char <= "Z" || char === "_";
    }
    isAlphaNumeric(char) {
      return this.isAlpha(char) || this.isDigit(char);
    }
    getColumn(position) {
      return position - this.lineStart + 1;
    }
    addToken(type, literal = null) {
      const lexeme = this.source.substring(this.start, this.current);
      this.tokens.push(createToken(
        type,
        lexeme,
        literal,
        this.line,
        this.getColumn(this.start)
      ));
    }
    /**
     * Get the error reporter
     */
    getErrorReporter() {
      return this.errorReporter;
    }
  };

  // src/parser/parser.ts
  var ParseError = class extends Error {
    constructor(message) {
      super(message);
      this.name = "ParseError";
    }
  };
  var Parser = class {
    constructor(tokens, errorReporter2) {
      __publicField(this, "tokens");
      __publicField(this, "current", 0);
      __publicField(this, "errorReporter");
      this.tokens = tokens;
      this.errorReporter = errorReporter2 || new ErrorReporter();
    }
    /**
     * Parse all tokens into an AST
     */
    parse() {
      const statements = [];
      while (!this.isAtEnd()) {
        try {
          const stmt = this.declaration();
          if (stmt) {
            statements.push(stmt);
          }
        } catch (error) {
          if (error instanceof ParseError) {
            this.synchronize();
          } else {
            throw error;
          }
        }
      }
      return createProgram(statements);
    }
    // ============================================================
    // Declarations
    // ============================================================
    declaration() {
      try {
        if (this.check("VAR" /* VAR */) || this.check("CONST" /* CONST */)) {
          return this.varDeclaration();
        }
        if (this.check("FUNCTION" /* FUNCTION */)) {
          return this.functionDeclaration();
        }
        return this.statement();
      } catch (error) {
        if (error instanceof ParseError) {
          this.synchronize();
          return null;
        }
        throw error;
      }
    }
    varDeclaration() {
      const isConst = this.check("CONST" /* CONST */);
      const keyword = this.advance();
      const nameToken = this.consume("IDENTIFIER" /* IDENTIFIER */, "a variable name");
      const identifier = createIdentifier(nameToken.lexeme, nameToken.line, nameToken.column);
      let value = null;
      if (this.match("EQUAL" /* EQUAL */)) {
        value = this.expression();
      }
      return {
        type: "VarDeclaration",
        identifier,
        value,
        isConst,
        line: keyword.line,
        column: keyword.column
      };
    }
    functionDeclaration() {
      const keyword = this.advance();
      const nameToken = this.consume("IDENTIFIER" /* IDENTIFIER */, "a function name");
      const name = createIdentifier(nameToken.lexeme, nameToken.line, nameToken.column);
      this.consume("LEFT_PAREN" /* LEFT_PAREN */, "'('");
      const params = [];
      if (!this.check("RIGHT_PAREN" /* RIGHT_PAREN */)) {
        do {
          const paramToken = this.consume("IDENTIFIER" /* IDENTIFIER */, "a parameter name");
          params.push(createIdentifier(paramToken.lexeme, paramToken.line, paramToken.column));
        } while (this.match("COMMA" /* COMMA */));
      }
      this.consume("RIGHT_PAREN" /* RIGHT_PAREN */, "')'");
      const body = this.blockStatement();
      return {
        type: "FunctionDeclaration",
        name,
        params,
        body,
        line: keyword.line,
        column: keyword.column
      };
    }
    // ============================================================
    // Statements
    // ============================================================
    statement() {
      if (this.check("IF" /* IF */)) {
        return this.ifStatement();
      }
      if (this.check("WHILE" /* WHILE */)) {
        return this.whileStatement();
      }
      if (this.check("RETURN" /* RETURN */)) {
        return this.returnStatement();
      }
      if (this.check("PRINT" /* PRINT */)) {
        return this.printStatement();
      }
      if (this.check("LEFT_BRACE" /* LEFT_BRACE */)) {
        return this.blockStatement();
      }
      return this.expressionStatement();
    }
    ifStatement() {
      const keyword = this.advance();
      this.consume("LEFT_PAREN" /* LEFT_PAREN */, "'('");
      const condition = this.expression();
      this.consume("RIGHT_PAREN" /* RIGHT_PAREN */, "')'");
      const consequent = this.blockStatement();
      let alternate = null;
      if (this.match("ELSE" /* ELSE */)) {
        if (this.check("IF" /* IF */)) {
          alternate = this.ifStatement();
        } else {
          alternate = this.blockStatement();
        }
      }
      return {
        type: "IfStatement",
        condition,
        consequent,
        alternate,
        line: keyword.line,
        column: keyword.column
      };
    }
    whileStatement() {
      const keyword = this.advance();
      this.consume("LEFT_PAREN" /* LEFT_PAREN */, "'('");
      const condition = this.expression();
      this.consume("RIGHT_PAREN" /* RIGHT_PAREN */, "')'");
      const body = this.blockStatement();
      return {
        type: "WhileStatement",
        condition,
        body,
        line: keyword.line,
        column: keyword.column
      };
    }
    returnStatement() {
      const keyword = this.advance();
      let argument = null;
      if (!this.check("RIGHT_BRACE" /* RIGHT_BRACE */) && !this.isAtEnd()) {
        if (!this.check("EOF" /* EOF */)) {
          argument = this.expression();
        }
      }
      return {
        type: "ReturnStatement",
        argument,
        line: keyword.line,
        column: keyword.column
      };
    }
    printStatement() {
      const keyword = this.advance();
      const argument = this.expression();
      return {
        type: "PrintStatement",
        argument,
        line: keyword.line,
        column: keyword.column
      };
    }
    blockStatement() {
      const brace = this.consume("LEFT_BRACE" /* LEFT_BRACE */, "'{'");
      const statements = [];
      while (!this.check("RIGHT_BRACE" /* RIGHT_BRACE */) && !this.isAtEnd()) {
        const stmt = this.declaration();
        if (stmt) {
          statements.push(stmt);
        }
      }
      this.consume("RIGHT_BRACE" /* RIGHT_BRACE */, "'}'");
      return {
        type: "BlockStatement",
        body: statements,
        line: brace.line,
        column: brace.column
      };
    }
    expressionStatement() {
      const expr = this.expression();
      return {
        type: "ExpressionStatement",
        expression: expr,
        line: expr.line,
        column: expr.column
      };
    }
    // ============================================================
    // Expressions (Precedence Climbing)
    // ============================================================
    expression() {
      return this.assignment();
    }
    assignment() {
      const expr = this.or();
      if (this.match("EQUAL" /* EQUAL */)) {
        const equals = this.previous();
        const value = this.assignment();
        if (expr.type === "Identifier") {
          return {
            type: "AssignmentExpression",
            assignee: expr,
            value,
            line: expr.line,
            column: expr.column
          };
        }
        this.errorReporter.reportError(
          "Invalid assignment target",
          equals.line,
          equals.column
        );
      }
      return expr;
    }
    or() {
      let expr = this.and();
      while (this.match("OR" /* OR */)) {
        const operator = this.previous();
        const right = this.and();
        expr = {
          type: "BinaryExpression",
          operator: "or",
          left: expr,
          right,
          line: operator.line,
          column: operator.column
        };
      }
      return expr;
    }
    and() {
      let expr = this.equality();
      while (this.match("AND" /* AND */)) {
        const operator = this.previous();
        const right = this.equality();
        expr = {
          type: "BinaryExpression",
          operator: "and",
          left: expr,
          right,
          line: operator.line,
          column: operator.column
        };
      }
      return expr;
    }
    equality() {
      let expr = this.comparison();
      while (this.match("BANG_EQUAL" /* BANG_EQUAL */, "EQUAL_EQUAL" /* EQUAL_EQUAL */)) {
        const operator = this.previous();
        const right = this.comparison();
        expr = {
          type: "BinaryExpression",
          operator: operator.lexeme,
          left: expr,
          right,
          line: operator.line,
          column: operator.column
        };
      }
      return expr;
    }
    comparison() {
      let expr = this.term();
      while (this.match("GREATER" /* GREATER */, "GREATER_EQUAL" /* GREATER_EQUAL */, "LESS" /* LESS */, "LESS_EQUAL" /* LESS_EQUAL */)) {
        const operator = this.previous();
        const right = this.term();
        expr = {
          type: "BinaryExpression",
          operator: operator.lexeme,
          left: expr,
          right,
          line: operator.line,
          column: operator.column
        };
      }
      return expr;
    }
    term() {
      let expr = this.factor();
      while (this.match("PLUS" /* PLUS */, "MINUS" /* MINUS */)) {
        const operator = this.previous();
        const right = this.factor();
        expr = {
          type: "BinaryExpression",
          operator: operator.lexeme,
          left: expr,
          right,
          line: operator.line,
          column: operator.column
        };
      }
      return expr;
    }
    factor() {
      let expr = this.unary();
      while (this.match("STAR" /* STAR */, "SLASH" /* SLASH */, "PERCENT" /* PERCENT */)) {
        const operator = this.previous();
        const right = this.unary();
        expr = {
          type: "BinaryExpression",
          operator: operator.lexeme,
          left: expr,
          right,
          line: operator.line,
          column: operator.column
        };
      }
      return expr;
    }
    unary() {
      if (this.match("BANG" /* BANG */, "MINUS" /* MINUS */)) {
        const operator = this.previous();
        const right = this.unary();
        return {
          type: "UnaryExpression",
          operator: operator.lexeme,
          argument: right,
          line: operator.line,
          column: operator.column
        };
      }
      return this.call();
    }
    call() {
      let expr = this.primary();
      while (true) {
        if (this.match("LEFT_PAREN" /* LEFT_PAREN */)) {
          expr = this.finishCall(expr);
        } else if (this.match("LEFT_BRACKET" /* LEFT_BRACKET */)) {
          const index = this.expression();
          this.consume("RIGHT_BRACKET" /* RIGHT_BRACKET */, "']' after index");
          expr = {
            type: "IndexExpression",
            object: expr,
            index,
            line: expr.line,
            column: expr.column
          };
        } else {
          break;
        }
      }
      return expr;
    }
    finishCall(callee) {
      const args = [];
      if (!this.check("RIGHT_PAREN" /* RIGHT_PAREN */)) {
        do {
          args.push(this.expression());
        } while (this.match("COMMA" /* COMMA */));
      }
      const paren = this.consume("RIGHT_PAREN" /* RIGHT_PAREN */, "')' after arguments");
      return {
        type: "CallExpression",
        callee,
        arguments: args,
        line: callee.line,
        column: callee.column
      };
    }
    primary() {
      if (this.match("FALSE" /* FALSE */)) {
        const token2 = this.previous();
        return createBooleanLiteral(false, token2.line, token2.column);
      }
      if (this.match("TRUE" /* TRUE */)) {
        const token2 = this.previous();
        return createBooleanLiteral(true, token2.line, token2.column);
      }
      if (this.match("NULL" /* NULL */)) {
        const token2 = this.previous();
        return createNullLiteral(token2.line, token2.column);
      }
      if (this.match("NUMBER" /* NUMBER */)) {
        const token2 = this.previous();
        return createNumericLiteral(token2.literal, token2.line, token2.column);
      }
      if (this.match("STRING" /* STRING */)) {
        const token2 = this.previous();
        return createStringLiteral(token2.literal, token2.line, token2.column);
      }
      if (this.match("IDENTIFIER" /* IDENTIFIER */)) {
        const token2 = this.previous();
        return createIdentifier(token2.lexeme, token2.line, token2.column);
      }
      if (this.match("LEFT_PAREN" /* LEFT_PAREN */)) {
        const expr = this.expression();
        this.consume("RIGHT_PAREN" /* RIGHT_PAREN */, "')'");
        return expr;
      }
      if (this.match("LEFT_BRACKET" /* LEFT_BRACKET */)) {
        return this.parseArrayLiteral();
      }
      const token = this.peek();
      this.errorReporter.reportUnexpectedToken(token, "an expression");
      throw new ParseError(`Unexpected token: ${token.lexeme}`);
    }
    /**
     * Parse an array literal: [element1, element2, ...]
     */
    parseArrayLiteral() {
      const bracket = this.previous();
      const elements = [];
      if (!this.check("RIGHT_BRACKET" /* RIGHT_BRACKET */)) {
        do {
          elements.push(this.expression());
        } while (this.match("COMMA" /* COMMA */));
      }
      this.consume("RIGHT_BRACKET" /* RIGHT_BRACKET */, "']' to close array");
      return {
        type: "ArrayLiteral",
        elements,
        line: bracket.line,
        column: bracket.column
      };
    }
    // ============================================================
    // Panic Mode Recovery
    // ============================================================
    /**
     * Synchronize after an error by advancing to a statement boundary
     */
    synchronize() {
      this.advance();
      while (!this.isAtEnd()) {
        switch (this.peek().type) {
          case "FUNCTION" /* FUNCTION */:
          case "VAR" /* VAR */:
          case "CONST" /* CONST */:
          case "IF" /* IF */:
          case "WHILE" /* WHILE */:
          case "FOR" /* FOR */:
          case "RETURN" /* RETURN */:
          case "PRINT" /* PRINT */:
            return;
        }
        this.advance();
      }
    }
    // ============================================================
    // Helper Methods
    // ============================================================
    match(...types) {
      for (const type of types) {
        if (this.check(type)) {
          this.advance();
          return true;
        }
      }
      return false;
    }
    check(type) {
      if (this.isAtEnd())
        return false;
      return this.peek().type === type;
    }
    advance() {
      if (!this.isAtEnd())
        this.current++;
      return this.previous();
    }
    isAtEnd() {
      return this.peek().type === "EOF" /* EOF */;
    }
    peek() {
      return this.tokens[this.current];
    }
    previous() {
      return this.tokens[this.current - 1];
    }
    consume(type, expected) {
      if (this.check(type))
        return this.advance();
      const token = this.peek();
      this.errorReporter.reportUnexpectedToken(token, expected);
      throw new ParseError(`Expected ${expected}`);
    }
    /**
     * Get the error reporter
     */
    getErrorReporter() {
      return this.errorReporter;
    }
  };

  // src/interpreter/environment.ts
  var Environment = class {
    constructor(parent = null) {
      __publicField(this, "values", /* @__PURE__ */ new Map());
      __publicField(this, "constants", /* @__PURE__ */ new Set());
      __publicField(this, "parent");
      this.parent = parent;
    }
    /**
     * Define a new variable
     */
    define(name, value, isConst = false) {
      if (this.values.has(name)) {
        throw new Error(`Variable '${name}' is already defined in this scope.`);
      }
      this.values.set(name, value);
      if (isConst) {
        this.constants.add(name);
      }
    }
    /**
     * Get a variable's value
     */
    get(name) {
      if (this.values.has(name)) {
        return this.values.get(name);
      }
      if (this.parent) {
        return this.parent.get(name);
      }
      throw new Error(`Undefined variable '${name}'.`);
    }
    /**
     * Assign a new value to an existing variable
     */
    assign(name, value) {
      if (this.values.has(name)) {
        if (this.constants.has(name)) {
          throw new Error(`Cannot reassign constant '${name}'.`);
        }
        this.values.set(name, value);
        return;
      }
      if (this.parent) {
        this.parent.assign(name, value);
        return;
      }
      throw new Error(`Undefined variable '${name}'.`);
    }
    /**
     * Check if a variable exists
     */
    has(name) {
      if (this.values.has(name))
        return true;
      if (this.parent)
        return this.parent.has(name);
      return false;
    }
  };

  // src/interpreter/interpreter.ts
  var ReturnValue = class extends Error {
    constructor(value) {
      super("Return");
      __publicField(this, "value");
      this.value = value;
    }
  };
  var Interpreter = class {
    constructor(errorReporter2, outputCallback) {
      __publicField(this, "globalEnv");
      __publicField(this, "currentEnv");
      __publicField(this, "errorReporter");
      __publicField(this, "output", []);
      __publicField(this, "outputCallback");
      this.globalEnv = new Environment();
      this.currentEnv = this.globalEnv;
      this.errorReporter = errorReporter2 || new ErrorReporter();
      this.outputCallback = outputCallback || ((text) => console.log(text));
    }
    /**
     * Interpret a program AST
     */
    interpret(program) {
      this.output = [];
      try {
        for (const statement of program.body) {
          this.executeStatement(statement);
        }
      } catch (error) {
        if (error instanceof Error && !(error instanceof ReturnValue)) {
          this.errorReporter.reportRuntimeError(error.message, 0, 0);
        }
      }
      return this.output;
    }
    /**
     * Execute a statement
     */
    executeStatement(stmt) {
      switch (stmt.type) {
        case "VarDeclaration":
          this.executeVarDeclaration(stmt);
          break;
        case "FunctionDeclaration":
          this.executeFunctionDeclaration(stmt);
          break;
        case "IfStatement":
          this.executeIfStatement(stmt);
          break;
        case "WhileStatement":
          this.executeWhileStatement(stmt);
          break;
        case "ReturnStatement":
          this.executeReturnStatement(stmt);
          break;
        case "PrintStatement":
          this.executePrintStatement(stmt);
          break;
        case "BlockStatement":
          this.executeBlockStatement(stmt, new Environment(this.currentEnv));
          break;
        case "ExpressionStatement":
          this.evaluate(stmt.expression);
          break;
      }
    }
    executeVarDeclaration(stmt) {
      const value = stmt.value ? this.evaluate(stmt.value) : null;
      this.currentEnv.define(stmt.identifier.name, value, stmt.isConst);
    }
    executeFunctionDeclaration(stmt) {
      const func = {
        type: "function",
        name: stmt.name.name,
        params: stmt.params.map((p) => p.name),
        body: stmt.body,
        closure: this.currentEnv
      };
      this.currentEnv.define(stmt.name.name, func);
    }
    executeIfStatement(stmt) {
      const condition = this.evaluate(stmt.condition);
      if (this.isTruthy(condition)) {
        this.executeBlockStatement(stmt.consequent, new Environment(this.currentEnv));
      } else if (stmt.alternate) {
        if (stmt.alternate.type === "IfStatement") {
          this.executeIfStatement(stmt.alternate);
        } else {
          this.executeBlockStatement(stmt.alternate, new Environment(this.currentEnv));
        }
      }
    }
    executeWhileStatement(stmt) {
      while (this.isTruthy(this.evaluate(stmt.condition))) {
        this.executeBlockStatement(stmt.body, new Environment(this.currentEnv));
      }
    }
    executeReturnStatement(stmt) {
      const value = stmt.argument ? this.evaluate(stmt.argument) : null;
      throw new ReturnValue(value);
    }
    executePrintStatement(stmt) {
      const value = this.evaluate(stmt.argument);
      const output = this.stringify(value);
      this.output.push(output);
      this.outputCallback(output);
    }
    executeBlockStatement(block, env) {
      const previousEnv = this.currentEnv;
      this.currentEnv = env;
      try {
        for (const stmt of block.body) {
          this.executeStatement(stmt);
        }
      } finally {
        this.currentEnv = previousEnv;
      }
    }
    // ============================================================
    // Expression Evaluation
    // ============================================================
    evaluate(expr) {
      switch (expr.type) {
        case "NumericLiteral":
          return expr.value;
        case "StringLiteral":
          return expr.value;
        case "BooleanLiteral":
          return expr.value;
        case "NullLiteral":
          return null;
        case "Identifier":
          return this.currentEnv.get(expr.name);
        case "BinaryExpression":
          return this.evaluateBinaryExpression(expr);
        case "UnaryExpression":
          return this.evaluateUnaryExpression(expr);
        case "CallExpression":
          return this.evaluateCallExpression(expr);
        case "AssignmentExpression":
          return this.evaluateAssignmentExpression(expr);
        case "ArrayLiteral":
          return this.evaluateArrayLiteral(expr);
        case "IndexExpression":
          return this.evaluateIndexExpression(expr);
        default:
          throw new Error(`Unknown expression type: ${expr.type}`);
      }
    }
    evaluateBinaryExpression(expr) {
      const left = this.evaluate(expr.left);
      const right = this.evaluate(expr.right);
      switch (expr.operator) {
        case "+":
          if (typeof left === "string" || typeof right === "string") {
            return String(left) + String(right);
          }
          return left + right;
        case "-":
          return left - right;
        case "*":
          return left * right;
        case "/":
          if (right === 0) {
            throw new Error("Division by zero");
          }
          return left / right;
        case "%":
          return left % right;
        case ">":
          return left > right;
        case ">=":
          return left >= right;
        case "<":
          return left < right;
        case "<=":
          return left <= right;
        case "==":
          return left === right;
        case "!=":
          return left !== right;
        case "and":
          return this.isTruthy(left) && this.isTruthy(right);
        case "or":
          return this.isTruthy(left) || this.isTruthy(right);
        default:
          throw new Error(`Unknown operator: ${expr.operator}`);
      }
    }
    evaluateUnaryExpression(expr) {
      const value = this.evaluate(expr.argument);
      switch (expr.operator) {
        case "-":
          return -value;
        case "!":
          return !this.isTruthy(value);
        default:
          throw new Error(`Unknown unary operator: ${expr.operator}`);
      }
    }
    evaluateCallExpression(expr) {
      const callee = this.evaluate(expr.callee);
      if (!callee || typeof callee !== "object" || callee.type !== "function") {
        throw new Error("Can only call functions");
      }
      const func = callee;
      const args = expr.arguments.map((arg) => this.evaluate(arg));
      if (args.length !== func.params.length) {
        throw new Error(
          `Function '${func.name}' expects ${func.params.length} arguments, but got ${args.length}`
        );
      }
      const funcEnv = new Environment(func.closure);
      for (let i = 0; i < func.params.length; i++) {
        funcEnv.define(func.params[i], args[i]);
      }
      try {
        this.executeBlockStatement(func.body, funcEnv);
      } catch (error) {
        if (error instanceof ReturnValue) {
          return error.value;
        }
        throw error;
      }
      return null;
    }
    evaluateAssignmentExpression(expr) {
      const value = this.evaluate(expr.value);
      this.currentEnv.assign(expr.assignee.name, value);
      return value;
    }
    evaluateArrayLiteral(expr) {
      return expr.elements.map((element) => this.evaluate(element));
    }
    evaluateIndexExpression(expr) {
      const object = this.evaluate(expr.object);
      const index = this.evaluate(expr.index);
      if (!Array.isArray(object)) {
        throw new Error("Can only index into arrays");
      }
      if (typeof index !== "number") {
        throw new Error("Array index must be a number");
      }
      if (index < 0 || index >= object.length) {
        throw new Error(`Array index ${index} out of bounds (array length: ${object.length})`);
      }
      return object[index];
    }
    // ============================================================
    // Helper Methods
    // ============================================================
    isTruthy(value) {
      if (value === null || value === void 0)
        return false;
      if (typeof value === "boolean")
        return value;
      return true;
    }
    stringify(value) {
      if (value === null || value === void 0)
        return "null";
      if (Array.isArray(value)) {
        return "[" + value.map((v) => this.stringify(v)).join(", ") + "]";
      }
      if (typeof value === "object" && value.type === "function") {
        return `<function ${value.name}>`;
      }
      return String(value);
    }
    /**
     * Get collected output
     */
    getOutput() {
      return [...this.output];
    }
    /**
     * Get the error reporter
     */
    getErrorReporter() {
      return this.errorReporter;
    }
    /**
     * Reset the interpreter state
     */
    reset() {
      this.globalEnv = new Environment();
      this.currentEnv = this.globalEnv;
      this.output = [];
      this.errorReporter.clear();
    }
  };

  // src/languages/en.json
  var en_default = {
    name: "English",
    code: "en",
    keywords: {
      var: "var",
      const: "const",
      function: "function",
      return: "return",
      if: "if",
      else: "else",
      while: "while",
      for: "for",
      and: "and",
      or: "or",
      print: "print",
      true: "true",
      false: "false",
      null: "null"
    }
  };

  // src/languages/id.json
  var id_default = {
    name: "Indonesian",
    code: "id",
    keywords: {
      var: "var",
      const: "konstan",
      function: "fungsi",
      return: "kembalikan",
      if: "jika",
      else: "lainnya",
      while: "selama",
      for: "untuk",
      and: "dan",
      or: "atau",
      print: "cetak",
      true: "benar",
      false: "salah",
      null: "kosong"
    }
  };

  // src/languages/loader.ts
  var languages = /* @__PURE__ */ new Map([
    ["en", en_default],
    ["id", id_default]
  ]);
  function getLanguageConfig(code) {
    const config = languages.get(code.toLowerCase());
    if (!config) {
      throw new Error(`Language configuration not found for code: ${code}. Available: ${Array.from(languages.keys()).join(", ")}`);
    }
    return config;
  }
  function getAvailableLanguages() {
    return Array.from(languages.keys());
  }

  // src/index.ts
  var WearLang = class {
    constructor(languageCode = "en", outputCallback) {
      __publicField(this, "config");
      __publicField(this, "errorReporter");
      __publicField(this, "outputCallback");
      this.config = getLanguageConfig(languageCode);
      this.errorReporter = new ErrorReporter();
      this.outputCallback = outputCallback || ((text) => console.log(text));
    }
    /**
     * Run WeaR source code
     */
    run(source) {
      this.errorReporter.clear();
      this.errorReporter.setSource(source);
      const interpreter = new Interpreter(this.errorReporter, this.outputCallback);
      const lexer = new Lexer(source, this.config, this.errorReporter);
      const tokens = lexer.tokenize();
      if (this.errorReporter.hasErrors()) {
        return {
          output: [],
          errors: [this.errorReporter.getFormattedErrors()],
          success: false
        };
      }
      const parser = new Parser(tokens, this.errorReporter);
      const ast = parser.parse();
      if (this.errorReporter.hasErrors()) {
        return {
          output: [],
          errors: [this.errorReporter.getFormattedErrors()],
          success: false
        };
      }
      const output = interpreter.interpret(ast);
      if (this.errorReporter.hasErrors()) {
        return {
          output,
          errors: [this.errorReporter.getFormattedErrors()],
          success: false
        };
      }
      return {
        output,
        errors: [],
        success: true
      };
    }
    /**
     * Set a custom output callback (for browser use)
     */
    setOutputCallback(callback) {
      this.outputCallback = callback;
    }
    /**
     * Change the language configuration
     */
    setLanguage(languageCode) {
      this.config = getLanguageConfig(languageCode);
    }
    /**
     * Get current language name
     */
    getLanguageName() {
      return this.config.name;
    }
  };

  // src/web.ts
  if (typeof window !== "undefined") {
    window.WearLang = WearLang;
    window.getAvailableLanguages = getAvailableLanguages;
  }
})();
