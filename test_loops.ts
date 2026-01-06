/**
 * Test script for Arrays and While Loops
 */

import { WearLang } from './src/index';

console.log('=== WeaR Lang: Arrays & While Loops Test ===\n');

// Test Indonesian
const wearID = new WearLang('id');
const codeID = `
var angka = [10, 20, 30, 40, 50]
var i = 0

cetak "Memulai Loop..."

selama (i < 5) {
    cetak "Angka ke-" + i + " adalah: " + angka[i]
    i = i + 1
}

cetak "Selesai!"
`;

console.log('--- Indonesian (selama) ---');
const resultID = wearID.run(codeID);
console.log('');

// Test English
const wearEN = new WearLang('en');
const codeEN = `
var numbers = [100, 200, 300]
var j = 0

print "Starting loop..."

while (j < 3) {
    print "Number " + j + " = " + numbers[j]
    j = j + 1
}

print "Done!"
`;

console.log('--- English (while) ---');
const resultEN = wearEN.run(codeEN);
console.log('');

// Summary
console.log('=== Test Results ===');
console.log('Indonesian:', resultID.success ? '✓ PASSED' : '✗ FAILED');
console.log('English:', resultEN.success ? '✓ PASSED' : '✗ FAILED');

if (!resultID.success) console.log('ID Errors:', resultID.errors);
if (!resultEN.success) console.log('EN Errors:', resultEN.errors);
