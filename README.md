# WeaR Lang v1.1-dev

![status](https://img.shields.io/badge/status-development-orange)
![language](https://img.shields.io/badge/compiler-C-blue)
![self--hosted](https://img.shields.io/badge/self--hosted-yes-success)
![license](https://img.shields.io/badge/license-MIT-green)

**WeaR Lang** is a small statically compiled programming language with a self-hosted compiler written in WeaR itself. The current implementation transpiles WeaR source to C and uses GCC/MinGW to produce a native executable.

## Project status

The project is actively developed on the `development` branch. The `main` branch is reserved for stable releases.

The repository currently contains:

- `compiler.c` — Stage-0/native bootstrap compiler.
- `compiler.wr` — self-hosted Stage-1 compiler source.
- `runtime.c` — C runtime helpers used by generated programs.
- `tools/wear.py` — portable command-line frontend for compile/run workflows.
- `examples/` — language examples and regression inputs.
- `tests/` — native regression cases and CI runner.
- `docs/` — browser playground and static web assets.
- `archive/stage0_bootstrap/` — historical bootstrap artifacts.

## Building and using WeaR

### Recommended CLI

The project now provides a Python-based command-line frontend that keeps intermediate build files isolated from the source tree.

Compile a WeaR program to generated C:

```bash
python3 tools/wear.py compile examples/demo.wr -o build/demo.c
```

Run a WeaR program directly through the native toolchain:

```bash
python3 tools/wear.py run examples/demo.wr
```

Show the compiler frontend version:

```bash
python3 tools/wear.py --version
```

Use a different C compiler when necessary:

```bash
python3 tools/wear.py --cc clang compile examples/demo.wr -o build/demo.c
```

The CLI uses temporary build directories, stages the required `compiler.c` and `runtime.c` files there, and only writes the requested generated-C destination to the project workspace. Exit codes distinguish usage, toolchain, compiler, and native-program failures.

### Windows

Requirements:

- GCC/MinGW available in `PATH`.
- Python 3.10+.

Run the CLI from the repository root:

```bat
python tools\wear.py compile examples\demo.wr -o build\demo.c
```

The legacy bootstrap script remains available:

```bat
build_v1.bat
```

### Native regression suite

The CI-native regression suite builds `compiler.c` with GCC, runs it against representative WeaR programs, compiles the generated C, and executes the resulting native programs. The suite currently covers literals/variables, control flow, and function returns.

```bash
bash tests/run_regression.sh
```

The complete Stage-0 → Stage-1 bootstrap is intentionally not a required CI gate yet because `compiler.c` and the current `compiler.wr` still have known semantic drift. See GitHub issue #1 for the synchronization work.

## Legacy compiler workflow

The native compiler itself expects `input.wr` in its working directory and generates `output.c`.

```bat
copy examples\demo.wr input.wr
wear.exe
gcc output.c -o demo.exe
demo.exe
```

Generated/intermediate files such as `output.c`, `stage*.c`, object files, and temporary executables are ignored by Git.

## Language example

```wear
var nama = "Ridwan"
cetak "Halo " + nama

fungsi hitung_luas(panjang, lebar) {
    kembalikan panjang * lebar
}

jika (hitung_luas(10, 5) > 40) {
    cetak "Luasnya besar!"
} lainnya {
    cetak "Luasnya kecil."
}
```

English-style examples are also present in the playground, while the self-hosted compiler source currently uses the Indonesian dialect (`fungsi`, `jika`, `lainnya`, `selama`, `kembalikan`, `cetak`, and related forms).

## Browser playground

The static playground lives in `docs/` and can be deployed directly to GitHub Pages. The Pages workflow publishes the existing static files and does not require an npm build step.

## Development workflow

Use `development` for compiler/runtime changes and validation. Merge to `main` only after the native regression suite is green and the Stage-0/Stage-1 bootstrap has been verified.

## Security

Do not commit credentials, tokens, private keys, or other sensitive information. See [SECURITY.md](SECURITY.md) for the reporting and repository-hygiene policy.

## License

WeaR Lang is released under the MIT License. See [LICENSE](LICENSE).