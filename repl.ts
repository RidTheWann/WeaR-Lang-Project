// repl.ts
import * as readline from 'readline';
import { WearLang } from './src/index';

// Setup Interface Terminal
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: 'wear> ' // Kursor keren
});

console.clear();
console.log("\x1b[36m%s\x1b[0m", "========================================");
console.log("\x1b[1m%s\x1b[0m", "   WeaR Lang Interactive Shell (v1.0)   ");
console.log("\x1b[36m%s\x1b[0m", "========================================");
console.log("Ketik 'keluar' untuk berhenti.");
console.log("Ketik '#en' untuk Inggris, '#id' untuk Indonesia.");
console.log("----------------------------------------");

// Inisialisasi Engine (Default Indo)
const engine = new WearLang('id');

rl.prompt();

rl.on('line', (line) => {
  const input = line.trim();

  switch (input) {
    case 'keluar':
    case 'exit':
      console.log('Sampai jumpa! 👋');
      process.exit(0);
      break;
      
    case '#id':
      engine.setLanguage('id');
      break;
      
    case '#en':
      engine.setLanguage('en');
      break;
      
    case 'bersih':
    case 'clear':
      console.clear();
      break;

    default:
      if (input) {
        // Eksekusi kode baris ini
        engine.run(input);
      }
      break;
  }
  
  rl.prompt();
}).on('close', () => {
  console.log('Exit.');
  process.exit(0);
});