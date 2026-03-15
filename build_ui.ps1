# Build UI script for finalinvoicerag_v3
Write-Output "Building UI..."

Push-Location ui

# Clean old build
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue

# Build
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Output "Build successful!"

    # Copy to public
    Pop-Location
    Remove-Item -Path "public" -Recurse -Force -ErrorAction SilentlyContinue
    Copy-Item -Path "ui\dist" -Destination "public" -Recurse -Force

    Write-Output "UI deployed to public folder!"
    Write-Output ""
    Write-Output "Refresh your browser at http://localhost:9000"
} else {
    Pop-Location
    Write-Output "Build failed with exit code: $LASTEXITCODE"
}

