# Deploy v4.0 to Existing GitHub Repository
# This script replaces all code in your existing repo with v4.0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy v4.0 to GitHub Repository" -ForegroundColor Cyan
Write-Host "Repository: https://github.com/Vijay-Ashley/FinanceInvoiceRag.git" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "ERROR: app.py not found. Please run this from finalinvoicerag_v4 directory" -ForegroundColor Red
    exit 1
}

Write-Host "WARNING: This will replace ALL code in your GitHub repository!" -ForegroundColor Yellow
Write-Host "Current repo: https://github.com/Vijay-Ashley/FinanceInvoiceRag.git" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Are you sure you want to continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Deployment cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "Step 1: Checking for existing git repository..." -ForegroundColor Cyan

# Remove existing .git if present
if (Test-Path ".git") {
    Write-Host "Removing old git repository..." -ForegroundColor Yellow
    Remove-Item -Path ".git" -Recurse -Force
    Write-Host "Old git removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Initializing new git repository..." -ForegroundColor Cyan
git init
Write-Host "Git initialized" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Adding all files..." -ForegroundColor Cyan
git add .

# Show what will be committed
Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Cyan
git status --short | Select-Object -First 20
$totalFiles = (git status --short | Measure-Object).Count
Write-Host "... and $totalFiles total files" -ForegroundColor Gray

Write-Host ""
Write-Host "Step 4: Committing changes..." -ForegroundColor Cyan
git commit -m "v4.0: Complete rewrite - Invoice Intelligence Platform

New Features:
- Improved invoice extraction (70-80% accuracy)
- Multi-pattern regex (4 patterns per field)
- Fixed API endpoints and chunk generation
- Complete documentation

Technical Improvements:
- Multi-container Cosmos DB architecture
- Field-aware vector search
- Deterministic analytics
- Confidence scoring

Documentation:
- Complete deployment guides
- API documentation
- Testing guides
- Azure setup instructions

Ready for production deployment"

Write-Host "Changes committed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Adding remote repository..." -ForegroundColor Cyan
git remote add origin https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
Write-Host "Remote added" -ForegroundColor Green

Write-Host ""
Write-Host "Step 6: Pushing to GitHub (force push)..." -ForegroundColor Cyan
Write-Host "This will replace ALL code in the repository!" -ForegroundColor Yellow
Write-Host ""

# Force push to replace everything
git branch -M main
git push -f origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Successfully deployed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository has been updated!" -ForegroundColor Cyan
    Write-Host "Repository: https://github.com/Vijay-Ashley/FinanceInvoiceRag" -ForegroundColor White
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Visit: https://github.com/Vijay-Ashley/FinanceInvoiceRag" -ForegroundColor White
    Write-Host "2. Verify the README.md looks good" -ForegroundColor White
    Write-Host "3. Deploy to VM:" -ForegroundColor White
    Write-Host "   ssh azureuser@YOUR_VM_IP" -ForegroundColor Gray
    Write-Host "   cd /home/azureuser/rag_pdf_finance" -ForegroundColor Gray
    Write-Host "   git pull origin main" -ForegroundColor Gray
    Write-Host "   sudo systemctl restart rag-api" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Push failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Authentication failed - You may need to:" -ForegroundColor White
    Write-Host "   - Use a Personal Access Token instead of password" -ForegroundColor Gray
    Write-Host "   - Go to: https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host "   - Generate new token with 'repo' scope" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Try manual push:" -ForegroundColor White
    Write-Host "   git push -f origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Or use GitHub Desktop / VS Code Git integration" -ForegroundColor White
    Write-Host ""
}

Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "- README.md - Main documentation" -ForegroundColor White
Write-Host "- DEPLOYMENT_V4.md - Deployment guide" -ForegroundColor White
Write-Host "- VERSION.md - What is new" -ForegroundColor White
Write-Host ""

