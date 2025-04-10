# Set the size threshold (e.g., 100MB)
$thresholdMB = 100
$thresholdBytes = $thresholdMB * 1MB

# Path to the .gitignore file
$gitignorePath = ".gitignore"

# Ensure .gitignore exists
if (-not (Test-Path $gitignorePath)) {
    New-Item -ItemType File -Path $gitignorePath -Force | Out-Null
}

# Find all files larger than the threshold
Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt $thresholdBytes } | ForEach-Object {
    $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1).Replace("\", "/")

    # Check if it's already in .gitignore
    if (-not (Select-String -Path $gitignorePath -Pattern "^$relativePath$" -Quiet)) {
        Add-Content -Path $gitignorePath -Value $relativePath
        Write-Host "Added to .gitignore: $relativePath"
    }

    # Check if file is already tracked by Git
    $isTracked = git ls-files --error-unmatch "$relativePath" 2>$null
    if ($LASTEXITCODE -eq 0) {
        git rm --cached "$relativePath" | Out-Null
        Write-Host "Removed from Git index: $relativePath"
    }
}

Write-Host "✅ Done. .gitignore updated and large files removed from Git tracking."
