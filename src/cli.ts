#!/usr/bin/env node
import * as fs from 'fs';
import * as path from 'path';
import { WearLang } from './index';

// Ambil argumen dari terminal
// [0]=node, [1]=wear, [2]=nama_file
const args = process.argv.slice(2);

if (args.length === 0) {
    // Jika tidak ada argumen, jalankan REPL (Mode Interaktif)
    console.log("Memulai WeaR Lang REPL...");
    // Di sini Anda bisa import logika REPL yang tadi (tapi versi function)
    // Untuk sekarang kita kasih info saja dulu:
    console.log("Usage: wear <filename.wr>");
    console.log("Example: wear demo.wr");
    process.exit(0);
}

const filename = args[0];

// Cek ekstensi file
if (!filename.endsWith('.wr')) {
    console.error("❌ Error: WeaR Lang source files must end with .wr");
    process.exit(1);
}

// Baca File
const filePath = path.resolve(process.cwd(), filename);
if (!fs.existsSync(filePath)) {
    console.error(`❌ Error: File '${filename}' not found.`);
    process.exit(1);
}

const content = fs.readFileSync(filePath, 'utf-8');

// Jalankan Interpreter
console.log(`🚀 Running ${filename}...`);
const engine = new WearLang('id'); // Default ID, atau bisa deteksi otomatis nanti
engine.run(content);