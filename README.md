# WeaR Lang v1.0 (Native)

![v1.0-stable](https://img.shields.io/badge/version-v1.0--stable-blue) ![Native](https://img.shields.io/badge/type-Native-green) ![Zero-Dependencies](https://img.shields.io/badge/dependencies-None-success)

A statically compiled programming language written in itself.

## Installation
Currently, WeaR Lang is distributed as a portable executable for Windows.

1. Download \wear.exe\ from Releases.
2. Add the folder to your PATH.
3. Ensure \gcc\ (MinGW) is installed and in your PATH.

## Usage
\\\ash
# Compile a WeaR source file
wear.exe input.wr

# This produces 'output.c'. Compile it with GCC:
gcc output.c -o program.exe

# Run
./program.exe
\\\

## Build from Source
To rebuild the compiler from scratch using the self-hosted source:
\\\cmd
build_v1.bat
\\\
