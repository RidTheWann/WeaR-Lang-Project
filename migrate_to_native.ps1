# WeaR Lang Migration Script: Node.js to Native Edition
# This script removes legacy TypeScript/Node.js artifacts and reorganizes for Native compilation
# Run with: .\migrate_to_native.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WeaR Lang Migration to Native Edition" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Get-Location
}

Set-Location $projectRoot
Write-Host "[INFO] Working directory: $projectRoot" -ForegroundColor Gray

# Safety check - verify native folder exists
if (-not (Test-Path "native")) {
    Write-Host "[ERROR] 'native' folder not found. Aborting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[STEP 1] Removing legacy Node.js/TypeScript artifacts..." -ForegroundColor Yellow

# Folders to delete
$foldersToDelete = @("src", "dist", "node_modules", "out")
foreach ($folder in $foldersToDelete) {
    if (Test-Path $folder) {
        Write-Host "  Deleting folder: $folder" -ForegroundColor Gray
        Remove-Item -Recurse -Force $folder
    }
}

# Files to delete
$filesToDelete = @(
    "tsconfig.json",
    "package.json",
    "package-lock.json",
    ".npmignore"
)
foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        Write-Host "  Deleting file: $file" -ForegroundColor Gray
        Remove-Item -Force $file
    }
}

# Delete VSIX files (VS Code extension packages)
Get-ChildItem -Filter "wear-lang-*.vsix" | ForEach-Object {
    Write-Host "  Deleting VSIX: $($_.Name)" -ForegroundColor Gray
    Remove-Item -Force $_.FullName
}

Write-Host "[OK] Legacy artifacts removed." -ForegroundColor Green

Write-Host ""
Write-Host "[STEP 2] Moving native files to root directory..." -ForegroundColor Yellow

# Move all files from native/ to root
Get-ChildItem -Path "native" | ForEach-Object {
    $dest = Join-Path $projectRoot $_.Name
    if (Test-Path $dest) {
        Write-Host "  Overwriting: $($_.Name)" -ForegroundColor Gray
        Remove-Item -Recurse -Force $dest
    }
    Write-Host "  Moving: $($_.Name)" -ForegroundColor Gray
    Move-Item -Path $_.FullName -Destination $projectRoot
}

# Remove empty native folder
if (Test-Path "native") {
    Remove-Item -Force "native"
    Write-Host "[OK] Removed empty 'native' folder." -ForegroundColor Green
}

Write-Host ""
Write-Host "[STEP 3] Verifying project structure..." -ForegroundColor Yellow

$requiredFiles = @("wear_bootstrap.cpp")
$allPresent = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $allPresent = $false
    }
}

# Check for demo files
$demoFiles = Get-ChildItem -Filter "*.wr" -ErrorAction SilentlyContinue
Write-Host "  Found $($demoFiles.Count) WeaR source files (.wr)" -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($allPresent) {
    Write-Host "  Migration Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Next steps:" -ForegroundColor White
    Write-Host "    1. Compile: g++ -std=c++17 -O2 -o wearc.exe wear_bootstrap.cpp" -ForegroundColor Gray
    Write-Host "    2. Run: .\wearc.exe demo.wr --run" -ForegroundColor Gray
} else {
    Write-Host "  Migration completed with warnings." -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
