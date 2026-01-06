/**
 * WeaR Lang Demo Script
 * Tests the interpreter with Indonesian and English dialects
 */

import { WearLang } from './src/index';
import * as fs from 'fs';
import * as path from 'path';

// ANSI color codes for pretty output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    cyan: '\x1b[36m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
};

function printHeader(text: string): void {
    console.log(`\n${colors.cyan}${colors.bright}${'='.repeat(50)}${colors.reset}`);
    console.log(`${colors.cyan}${colors.bright}  ${text}${colors.reset}`);
    console.log(`${colors.cyan}${colors.bright}${'='.repeat(50)}${colors.reset}\n`);
}

function printSubHeader(text: string): void {
    console.log(`\n${colors.yellow}--- ${text} ---${colors.reset}\n`);
}

function printSuccess(text: string): void {
    console.log(`${colors.green}✓ ${text}${colors.reset}`);
}

function printError(text: string): void {
    console.log(`${colors.red}✗ ${text}${colors.reset}`);
}

// Main demo function
async function runDemo(): Promise<void> {
    printHeader('WeaR Lang Demo');

    console.log(`${colors.magenta}A polyglot programming language:`);
    console.log(`  • Friendly for beginners`);
    console.log(`  • Powerful for professionals`);
    console.log(`  • Supports localized keywords${colors.reset}`);

    // =====================================================
    // Indonesian Demo
    // =====================================================
    printSubHeader('Indonesian Demo (Bahasa Indonesia)');

    const indonesianCode = `
// Beginner Style
var nama = "Ridwan"
cetak "Halo " + nama

// Pro Style (Function)
fungsi hitung_luas(panjang, lebar) {
   kembalikan panjang * lebar
}

jika (hitung_luas(10, 5) > 40) {
   cetak "Luasnya besar!"
}
`;

    console.log(`${colors.blue}Source Code:${colors.reset}`);
    console.log(indonesianCode);
    console.log(`${colors.blue}Output:${colors.reset}`);

    const wearID = new WearLang('id');
    const resultID = wearID.run(indonesianCode);

    if (resultID.success) {
        printSuccess('Executed successfully!');
    } else {
        printError('Execution failed');
        console.log(resultID.errors.join('\n'));
    }

    // =====================================================
    // English Demo
    // =====================================================
    printSubHeader('English Demo');

    const englishCode = `
// Beginner Style
var name = "John"
print "Hello " + name

// Pro Style (Function)
function calculate_area(length, width) {
   return length * width
}

if (calculate_area(10, 5) > 40) {
   print "The area is large!"
}
`;

    console.log(`${colors.blue}Source Code:${colors.reset}`);
    console.log(englishCode);
    console.log(`${colors.blue}Output:${colors.reset}`);

    const wearEN = new WearLang('en');
    const resultEN = wearEN.run(englishCode);

    if (resultEN.success) {
        printSuccess('Executed successfully!');
    } else {
        printError('Execution failed');
        console.log(resultEN.errors.join('\n'));
    }

    // =====================================================
    // Error Handling Demo
    // =====================================================
    printSubHeader('Friendly Error Messages Demo');

    const errorCode = `
var x = 10
cetak x +
`;

    console.log(`${colors.blue}Intentionally broken code:${colors.reset}`);
    console.log(errorCode);
    console.log(`${colors.blue}Error Output:${colors.reset}`);

    const wearError = new WearLang('id');
    const resultError = wearError.run(errorCode);

    if (!resultError.success) {
        console.log(resultError.errors.join('\n'));
        printSuccess('Friendly error message generated!');
    }

    // =====================================================
    // File-based Demo (if examples exist)
    // =====================================================
    const demoFilePath = path.join(__dirname, 'examples', 'demo.wr');
    if (fs.existsSync(demoFilePath)) {
        printSubHeader('Running examples/demo.wr');

        const fileContent = fs.readFileSync(demoFilePath, 'utf-8');
        console.log(`${colors.blue}Source (from file):${colors.reset}`);
        console.log(fileContent.slice(0, 200) + '...\n');
        console.log(`${colors.blue}Output:${colors.reset}`);

        const wearFile = new WearLang('id');
        const resultFile = wearFile.run(fileContent);

        if (resultFile.success) {
            printSuccess('File executed successfully!');
        } else {
            printError('File execution failed');
            console.log(resultFile.errors.join('\n'));
        }
    }

    // =====================================================
    // Summary
    // =====================================================
    printHeader('Demo Complete');

    const allPassed = resultID.success && resultEN.success;
    if (allPassed) {
        console.log(`${colors.green}${colors.bright}✓ All tests passed!${colors.reset}`);
    } else {
        console.log(`${colors.red}${colors.bright}✗ Some tests failed${colors.reset}`);
    }

    console.log(`\n${colors.magenta}Available languages: id (Indonesian), en (English)${colors.reset}`);
    console.log(`${colors.magenta}Usage: const wear = new WearLang('id'); wear.run(code);${colors.reset}\n`);
}

// Run the demo
runDemo().catch(console.error);
