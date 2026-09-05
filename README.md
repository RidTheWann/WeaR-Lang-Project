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
- `examples/` — language examples and regression inputs.
- `docs/` — browser playground and static web assets.
- `archive/stage0_bootstrap/` — historical bootstrap artifacts.

## Building the compiler

### Windows

Requirements:

- GCC/MinGW available in `PATH`.
- The repository's bootstrap compiler (`wear.exe`) or a Stage-0 bootstrap compiler.

Run:

```bat
build_v1.bat
```

The bootstrap script builds a self-hosted compiler and runs a basic validation program.

### Native smoke test

GitHub Actions builds `compiler.c`, transpiles `examples/demo.wr`, compiles the generated C with GCC, and runs the resulting program.

## Using WeaR

The current native compiler expects the input source at `input.wr` and generates `output.c`.

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

Use `development` for compiler/runtime changes and validation. Merge to `main` only after the CI smoke test and self-hosting bootstrap succeed.

## Security

Do not commit credentials, tokens, private keys, or other sensitive information. See [SECURITY.md](SECURITY.md) for the reporting and repository-hygiene policy.

## License

WeaR Lang is released under the MIT License. See [LICENSE](LICENSE).
