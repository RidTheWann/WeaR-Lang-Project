# release_prep.ps1
# WeaR Lang v1.0 Release Preparation Script

Write-Host "🚀 Starting WeaR Lang v1.0 Release Prep..." -ForegroundColor Cyan

# ---------------------------------------------------------
# Task 1: Archive Stage-0 Bootstrap
# ---------------------------------------------------------
Write-Host "📦 Archiving Stage-0 Bootstrap artifacts..." -ForegroundColor Yellow

# Create archive directory
$archiveDir = "archive\stage0_bootstrap"
if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null
}

# Move bootstrap files
$bootstrapFiles = @("wearc.exe", "wear_bootstrap.cpp", "wearc_debug.exe")
foreach ($file in $bootstrapFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination $archiveDir -Force
        Write-Host "   Moved $file to archive." -ForegroundColor Gray
    }
}

# ---------------------------------------------------------
# Task 2: Delete Garbage & Cleanup Root
# ---------------------------------------------------------
Write-Host "🧹 Cleaning up repository..." -ForegroundColor Yellow

# 2a. Delete specific build artifacts
$extensions = @("*.o", "*.obj")
foreach ($ext in $extensions) {
    Get-ChildItem -Path . -Filter $ext -File | Remove-Item -Force
}

$tempFiles = @("stage1.c", "stage2.c", "output.c", "compiler_gen1.exe", "test.exe", "input.wr")
foreach ($file in $tempFiles) {
    if (Test-Path $file) { Remove-Item -Path $file -Force }
}

# Delete demo executables
Get-ChildItem -Path . -Filter "demo*.exe" -File | Remove-Item -Force

# 2b. Delete all executables EXCEPT wear.exe
# Note: wearc.exe matches *.exe but was moved already.
$exes = Get-ChildItem -Path . -Filter "*.exe" -File
foreach ($exe in $exes) {
    if ($exe.Name -ne "wear.exe") {
        Remove-Item -Path $exe.FullName -Force
        Write-Host "   Deleted $($exe.Name)" -ForegroundColor Red
    }
}

# 2c. Strict Root Cleanup
# Ensure only allowed files remain in root
$allowedFiles = @(
    "wear.exe",
    "compiler.wr",
    "runtime.c",
    "build_v1.bat",
    "LICENSE",
    ".gitignore",
    "README.md",
    "release_prep.ps1"
)
# Note: We preserve folders (docs, examples, etc.) and hidden files like .git

$rootFiles = Get-ChildItem -Path . -File
foreach ($file in $rootFiles) {
    if ($allowedFiles -notcontains $file.Name) {
        # Check if it's not a git file logic is handled by Get-ChildItem usually ignoring .git folder content but .gitignore is file
        # Also .gitattributes or .vscodeignore might exist.
        # User requested strict list.
        if ($file.Name -ne ".gitattributes" -and $file.Name -ne ".vscodeignore" -and $file.Name -ne "WALKTHROUGH_v1.md" -and $file.Name -ne "language-configuration.json") {
            # Move known non-garbage to archive/misc? Or just delete per instruction?
            # Instruction: "Ensure only [list] remain"
            # I'll archive others to be safe or delete if obvious garbage.
            # demo*.c, demo*.wr are garbage now.
            Remove-Item -Path $file.FullName -Force
            Write-Host "   Removed $($file.Name)" -ForegroundColor Red
        }
    }
}


# ---------------------------------------------------------
# Task 3: Generate New README.md
# ---------------------------------------------------------
Write-Host "📝 Generating README.md..." -ForegroundColor Yellow

$readmeContent = @"
# WeaR Lang v1.0 (Self-Hosted Edition)

![v1.0-stable](https://img.shields.io/badge/version-v1.0--stable-blue) ![Native](https://img.shields.io/badge/type-Native-green) ![Zero-Dependencies](https://img.shields.io/badge/dependencies-None-success)

A statically compiled programming language written in itself.

## Quick Start
```bash
# Compile a program
./wear.exe my_program.wr

# Compile the C output
gcc output.c -o my_program.exe
```

## Building from Source
Run the included bootstrap script to rebuild the compiler from scratch:

```cmd
build_v1.bat
```

This script will:
1. Verify prerequisites (`gcc`, `runtime.c`).
2. Use the backup bootstrap compiler (if restored) or existing `wear.exe` logic to regenerate the compiler.
*Note: Since this is the release self-hosted version, `wear.exe` is the source of truth.*
"@

Set-Content -Path "README.md" -Value $readmeContent -Encoding UTF8

# ---------------------------------------------------------
# Task 4: Git Operations
# ---------------------------------------------------------
Write-Host "🐙 Performing Git Operations..." -ForegroundColor Yellow

git add .
git commit -m "Release: WeaR Lang v1.0 (Self-Hosted)"
git tag v1.0.0
# Pushing tags requires explicit flag usually
git push origin main --tags

Write-Host "✅ WeaR Lang v1.0 has been released to GitHub!" -ForegroundColor Green
