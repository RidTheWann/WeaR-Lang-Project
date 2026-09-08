#!/usr/bin/env python3
"""WeaR Lang command-line frontend.

The frontend isolates compiler artifacts in a temporary workspace and provides
one stable entry point for source validation, semantic lowering, transpilation,
and native builds. The legacy Stage-0 compiler remains the backend while the
frontend removes its historical dependence on variable-name-based typing.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from semantic_contract import check_source
from semantic_frontend import rewrite_file

VERSION = "1.1-dev"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPILER = ROOT / "compiler.c"
DEFAULT_RUNTIME = ROOT / "runtime.c"

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_TOOLCHAIN = 3
EXIT_COMPILE = 4
EXIT_RUNTIME = 5
EXIT_SEMANTIC = 6


def fail(message: str, code: int) -> int:
    print(f"wear: error: {message}", file=sys.stderr)
    return code


def find_tool(name: str) -> str | None:
    return shutil.which(name)


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path}")


def run_process(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    except OSError as exc:
        raise RuntimeError(f"failed to start {' '.join(command)}: {exc}") from exc


def validate_source(source: Path) -> None:
    errors = check_source(source)
    if errors:
        raise ValueError("\n".join(errors))


def build_stage0(compiler_source: Path, runtime_source: Path, cc: str, workdir: Path) -> Path:
    staged_compiler = workdir / "compiler.c"
    staged_runtime = workdir / "runtime.c"
    compiler_exe = workdir / ("wear-bootstrap.exe" if os.name == "nt" else "wear-bootstrap")

    shutil.copy2(compiler_source, staged_compiler)
    shutil.copy2(runtime_source, staged_runtime)

    result = run_process([cc, str(staged_compiler), "-O2", "-o", str(compiler_exe)], cwd=workdir)
    if result.returncode != 0:
        diagnostics = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"native compiler build failed\n{diagnostics}")

    return compiler_exe


def transpile(compiler_exe: Path, source: Path, workdir: Path) -> Path:
    # The backend still expects input.wr. Feed it the semantically lowered
    # source so arbitrary user variable names no longer control C type choice.
    lowered = workdir / "input.wr"
    rewrite_file(source, lowered)

    result = run_process([str(compiler_exe)], cwd=workdir)
    if result.returncode != 0:
        diagnostics = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
        raise RuntimeError(f"WeaR compilation failed\n{diagnostics}")

    generated = workdir / "output.c"
    if not generated.is_file():
        raise RuntimeError("compiler completed without generating output.c")
    return generated


def native_output_name(target: Path) -> Path:
    if target.suffix:
        return target
    return target.with_suffix(".exe" if os.name == "nt" else "")


def compile_source(
    source: Path,
    output: Path,
    *,
    compiler_source: Path,
    runtime_source: Path,
    cc: str,
    keep_c: bool,
    skip_semantic: bool,
) -> Path:
    require_file(source, "source file")
    require_file(compiler_source, "compiler source")
    require_file(runtime_source, "runtime source")

    if not skip_semantic:
        validate_source(source)

    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="wear-build-") as temp:
        workdir = Path(temp)
        compiler_exe = build_stage0(compiler_source, runtime_source, cc, workdir)
        generated = transpile(compiler_exe, source.resolve(), workdir)
        shutil.copy2(generated, output)

        if keep_c:
            shutil.copy2(generated, output.with_suffix(output.suffix + ".c"))

    return output


def command_compile(args: argparse.Namespace) -> int:
    try:
        output = compile_source(
            Path(args.source),
            Path(args.output),
            compiler_source=Path(args.compiler),
            runtime_source=Path(args.runtime),
            cc=args.cc,
            keep_c=args.keep_c,
            skip_semantic=args.no_semantic_check,
        )
    except FileNotFoundError as exc:
        return fail(str(exc), EXIT_USAGE)
    except ValueError as exc:
        return fail(f"semantic validation failed\n{exc}", EXIT_SEMANTIC)
    except RuntimeError as exc:
        return fail(str(exc), EXIT_COMPILE)

    print(f"compiled {Path(args.source)} -> {output}")
    return EXIT_OK


def command_run(args: argparse.Namespace) -> int:
    source = Path(args.source)
    try:
        require_file(source, "source file")
        require_file(Path(args.compiler), "compiler source")
        require_file(Path(args.runtime), "runtime source")
        if not args.no_semantic_check:
            validate_source(source)
    except FileNotFoundError as exc:
        return fail(str(exc), EXIT_USAGE)
    except ValueError as exc:
        return fail(f"semantic validation failed\n{exc}", EXIT_SEMANTIC)

    cc = args.cc
    if not find_tool(cc):
        return fail(f"C compiler '{cc}' was not found in PATH", EXIT_TOOLCHAIN)

    with tempfile.TemporaryDirectory(prefix="wear-run-") as temp:
        temp_root = Path(temp)
        executable = native_output_name(temp_root / "program")
        generated_c = temp_root / "program.c"

        try:
            compile_source(
                source,
                generated_c,
                compiler_source=Path(args.compiler),
                runtime_source=Path(args.runtime),
                cc=cc,
                keep_c=False,
                skip_semantic=args.no_semantic_check,
            )
        except ValueError as exc:
            return fail(f"semantic validation failed\n{exc}", EXIT_SEMANTIC)
        except RuntimeError as exc:
            return fail(str(exc), EXIT_COMPILE)

        build = run_process([cc, str(generated_c), "-O2", "-o", str(executable)], cwd=temp_root)
        if build.returncode != 0:
            diagnostics = (build.stderr or build.stdout).strip()
            return fail(f"generated C build failed\n{diagnostics}", EXIT_COMPILE)

        try:
            result = subprocess.run([str(executable), *args.program_args], cwd=source.resolve().parent)
        except OSError as exc:
            return fail(f"failed to launch native program: {exc}", EXIT_RUNTIME)
        return result.returncode


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--no-semantic-check", action="store_true", help="skip semantic validation and compatibility lowering")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wear",
        description="Compile and run WeaR Lang programs with the native Stage-0 compiler.",
    )
    parser.add_argument("--version", action="version", version=f"WeaR Lang {VERSION}")
    parser.add_argument("--cc", default=os.environ.get("WEAR_CC", "gcc"), help="C compiler executable (default: gcc)")
    parser.add_argument("--compiler", default=str(DEFAULT_COMPILER), help="Stage-0 compiler.c path")
    parser.add_argument("--runtime", default=str(DEFAULT_RUNTIME), help="runtime.c path")

    sub = parser.add_subparsers(dest="command", required=True)

    compile_cmd = sub.add_parser("compile", help="compile a .wr source file to generated C")
    compile_cmd.add_argument("source", help="input .wr file")
    compile_cmd.add_argument("-o", "--output", required=True, help="generated C output path")
    compile_cmd.add_argument("--keep-c", action="store_true", help="also preserve a <output>.c copy")
    add_common_options(compile_cmd)
    compile_cmd.set_defaults(handler=command_compile)

    run_cmd = sub.add_parser("run", help="compile a .wr source and execute the native program")
    run_cmd.add_argument("source", help="input .wr file")
    run_cmd.add_argument("program_args", nargs=argparse.REMAINDER, help="arguments passed to the native program")
    add_common_options(run_cmd)
    run_cmd.set_defaults(handler=command_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
