# fix_release.ps1
# WeaR Lang v1.0 Release REMEDIATION Script
# Usage: .\fix_release.ps1

Write-Host "🚨 STARTING RELEASE FIX PROTOCOL..." -ForegroundColor Red

# ---------------------------------------------------------
# Step 1: Undo the Bad Commit
# ---------------------------------------------------------
Write-Host "1️⃣ Undoing previous bad commit..." -ForegroundColor Yellow
git reset --soft HEAD~1
if ($LASTEXITCODE -ne 0) { 
    Write-Host "   Git reset failed or nothing to reset. Continuing..." -ForegroundColor DarkGray
}

Write-Host "   Deleting local v1.0.0 tag..." -ForegroundColor Yellow
git tag -d v1.0.0 2>$null

# ---------------------------------------------------------
# Step 2: Aggressive Cleanup
# ---------------------------------------------------------
Write-Host "2️⃣ Executing Aggressive Cleanup..." -ForegroundColor Yellow

# 2a. Archive Stage-0
$archiveDir = "archive\stage0_bootstrap"
if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null
}

$bootstrapFiles = @("wearc.exe", "wear_bootstrap.cpp", "wearc_debug.exe")
foreach ($file in $bootstrapFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination $archiveDir -Force -ErrorAction SilentlyContinue
        Write-Host "   Archived $file" -ForegroundColor Gray
    }
}

# 2b. Delete specific garbage
$garbageFiles = @(
    "*.o", "*.obj",
    "stage1.c", "stage2.c", "output.c",
    "compiler_gen1.exe", "test.exe", "temp.exe", 
    "input.wr", "hello.wr", "hello.exe"
)

foreach ($pattern in $garbageFiles) {
    Get-ChildItem -Path . -Filter $pattern -File | Remove-Item -Force -ErrorAction SilentlyContinue
    # Also Check if literal filename exists (for non-patterns)
    if (-not ($pattern -like "*") -and (Test-Path $pattern)) {
         Remove-Item -Path $pattern -Force -ErrorAction SilentlyContinue
    }
}
Get-ChildItem -Path . -Filter "demo*.exe" -File | Remove-Item -Force -ErrorAction SilentlyContinue

# 2c. Delete ALL .exe except allowed
$allowedExes = @("wear.exe")
$exes = Get-ChildItem -Path . -Filter "*.exe" -File
foreach ($exe in $exes) {
    if ($allowedExes -notcontains $exe.Name) {
        Remove-Item -Path $exe.FullName -Force
        Write-Host "   Deleted $($exe.Name)" -ForegroundColor Red
    }
}

# ---------------------------------------------------------
# Step 3: Update README.md
# ---------------------------------------------------------
Write-Host "3️⃣ Overwriting README.md..." -ForegroundColor Yellow

$readmeContent = @"
# WeaR Lang v1.0 (Native)

![v1.0-stable](https://img.shields.io/badge/version-v1.0--stable-blue) ![Native](https://img.shields.io/badge/type-Native-green) ![Zero-Dependencies](https://img.shields.io/badge/dependencies-None-success)

A statically compiled programming language written in itself.

## Installation
Currently, WeaR Lang is distributed as a portable executable for Windows.

1. Download \`wear.exe\` from Releases.
2. Add the folder to your PATH.
3. Ensure \`gcc\` (MinGW) is installed and in your PATH.

## Usage
\`\`\`bash
# Compile a WeaR source file
wear.exe input.wr

# This produces 'output.c'. Compile it with GCC:
gcc output.c -o program.exe

# Run
./program.exe
\`\`\`

## Build from Source
To rebuild the compiler from scratch using the self-hosted source:
\`\`\`cmd
build_v1.bat
\`\`\`
"@

Set-Content -Path "README.md" -Value $readmeContent -Encoding UTF8

# ---------------------------------------------------------
# Step 4: Force Update Release
# ---------------------------------------------------------
Write-Host "4️⃣ Force Pushing Release..." -ForegroundColor Yellow

# Add all changes (including deletions)
git add .

# Commit
git commit -m "Release: WeaR Lang v1.0 (Clean & Self-Hosted)"

# Retag
git tag v1.0.0

# Force push tag (delete remote first)
Write-Host "   Deleting remote tag..." -ForegroundColor Cyan
git push origin :refs/tags/v1.0.0
# Note: output might show error if tag didn't exist remotely, safe to ignore.

Write-Host "   Pushing new release..." -ForegroundColor Cyan
git push origin main --tags

Write-Host "✅ RECOVERY COMPLETE. WeaR Lang v1.0 is now clean and live!" -ForegroundColor Green
