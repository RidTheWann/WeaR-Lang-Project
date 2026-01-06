# WeaR Lang

**A Polyglot Programming Language**

WeaR Lang is a programming language designed with the philosophy of "Low Floor, High Ceiling" - friendly for beginners yet powerful for professionals. It features polyglot keyword support, allowing developers to write code using localized keywords in their native language.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Syntax Reference](#syntax-reference)
- [Web Playground](#web-playground)
- [Development](#development)
- [License](#license)

---

## About

WeaR Lang addresses the challenge of making programming accessible to non-English speakers while maintaining professional capabilities. The language supports multiple keyword sets, enabling developers to write code in their preferred language (currently English and Indonesian).

### Design Philosophy

1. **Readable Syntax** - Minimal punctuation with clear block structures using curly braces
2. **Polyglot Keywords** - Native language keyword support (e.g., `if` in English, `jika` in Indonesian)
3. **Friendly Error Messages** - Descriptive error messages with line numbers and contextual hints
4. **Low Floor, High Ceiling** - Simple scripts require minimal syntax; complex programs have full language features

---

## Features

- Variables and constants
- Functions with closures
- Control flow (if/else, while loops)
- Arrays with index access
- String and numeric operations
- Multi-language keyword support
- Browser-based playground
- VS Code extension support

---

## Installation

### Using npm (Global Installation)

```bash
npm install -g wear-lang
```

### Local Development

```bash
git clone https://github.com/RidTheWann/WeaR-Lang-Project.git
cd WeaR-Lang-Project
npm install
npm run build
```

---

## Usage

### Command Line Interface

Run a WeaR script file:

```bash
wear examples/demo.wr
```

### Programmatic Usage (Node.js)

```javascript
const { WearLang } = require('wear-lang');

// Indonesian dialect
const wear = new WearLang('id');
wear.run(`
  var nama = "Ridwan"
  cetak "Halo " + nama
`);

// English dialect
const wearEN = new WearLang('en');
wearEN.run(`
  var name = "John"
  print "Hello " + name
`);
```

### VS Code Extension

1. Open VS Code
2. Navigate to Extensions (Ctrl+Shift+X)
3. Search for "WeaR Lang"
4. Click Install

The extension provides syntax highlighting for `.wr` files.

---

## Syntax Reference

### Keyword Comparison

| Feature          | English     | Indonesian    |
|------------------|-------------|---------------|
| Variable         | `var`       | `var`         |
| Constant         | `const`     | `konstan`     |
| Function         | `function`  | `fungsi`      |
| Return           | `return`    | `kembalikan`  |
| If               | `if`        | `jika`        |
| Else             | `else`      | `lainnya`     |
| While            | `while`     | `selama`      |
| Print            | `print`     | `cetak`       |
| True             | `true`      | `benar`       |
| False            | `false`     | `salah`       |
| Null             | `null`      | `kosong`      |
| And              | `and`       | `dan`         |
| Or               | `or`        | `atau`        |

### Code Examples

**Variable Declaration**

```
// English
var name = "John"
const PI = 3.14159

// Indonesian
var nama = "Budi"
konstan PI = 3.14159
```

**Functions**

```
// English
function greet(name) {
    return "Hello, " + name
}
print greet("World")

// Indonesian
fungsi sapa(nama) {
    kembalikan "Halo, " + nama
}
cetak sapa("Dunia")
```

**Control Flow**

```
// English
if (x > 10) {
    print "Large"
} else {
    print "Small"
}

// Indonesian
jika (x > 10) {
    cetak "Besar"
} lainnya {
    cetak "Kecil"
}
```

**Arrays and Loops**

```
// English
var numbers = [10, 20, 30]
var i = 0
while (i < 3) {
    print numbers[i]
    i = i + 1
}

// Indonesian
var angka = [10, 20, 30]
var i = 0
selama (i < 3) {
    cetak angka[i]
    i = i + 1
}
```

---

## Web Playground

Try WeaR Lang directly in your browser without any installation:

**[WeaR Playground](https://ridthewann.github.io/WeaR-Lang-Project/)**

The playground features:
- Split-pane code editor and output display
- Language switching between English and Indonesian
- Keyboard shortcut support (Ctrl+Enter to run)
- Syntax example templates

---

## Development

### Project Structure

```
WeaR-Lang-Project/
├── src/
│   ├── types/         # AST and token definitions
│   ├── lexer/         # Tokenizer
│   ├── parser/        # Recursive descent parser
│   ├── interpreter/   # Tree-walking interpreter
│   ├── languages/     # Keyword configurations (en, id)
│   └── utils/         # Error reporting utilities
├── docs/              # GitHub Pages (web playground)
├── examples/          # Example WeaR scripts
└── .github/workflows/ # CI/CD configuration
```

### Build Commands

```bash
# Build TypeScript
npm run build

# Build web bundle for browser
npm run build:web

# Run demo
npm run demo

# Run tests
npm test
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Ridwan Gatro
