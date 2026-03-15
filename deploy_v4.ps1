# 🚀 Deploy v4.0 to GitHub
# This script prepares and pushes v4.0 to GitHub

Write-Host "🚀 Deploying Invoice Intelligence v4.0 to GitHub" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Error: app.py not found. Please run this from finalinvoicerag_v4 directory" -ForegroundColor Red
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

Write-Host "📋 Pre-deployment checks..." -ForegroundColor Yellow

# Check for .gitignore
if (-not (Test-Path ".gitignore")) {
    Write-Host "⚠️  Creating .gitignore..." -ForegroundColor Yellow
    @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# Environment
.env
.env.local

# Uploads
uploads/
*.pdf
*.png
*.jpg

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
nohup.out

# Node
node_modules/
dist/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
}

Write-Host "✅ .gitignore ready" -ForegroundColor Green

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository exists" -ForegroundColor Green
}

# Add all files
Write-Host ""
Write-Host "📦 Adding files to git..." -ForegroundColor Yellow
git add .

# Show status
Write-Host ""
Write-Host "📊 Git status:" -ForegroundColor Cyan
git status --short

# Commit
Write-Host ""
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "v4.0: Invoice Intelligence - Improved extraction with multi-pattern regex"
}

Write-Host "💾 Committing changes..." -ForegroundColor Yellow
git commit -m "$commitMessage"

# Check if remote exists
$remoteExists = git remote | Select-String "origin"

if (-not $remoteExists) {
    Write-Host ""
    Write-Host "🔗 No remote repository configured" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please enter your GitHub repository URL:"
    Write-Host "Example: https://github.com/username/rag-invoice-v4.git"
    $repoUrl = Read-Host "Repository URL"
    
    if (-not [string]::IsNullOrWhiteSpace($repoUrl)) {
        git remote add origin $repoUrl
        Write-Host "✅ Remote added: $repoUrl" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No remote added. You can add it later with:" -ForegroundColor Yellow
        Write-Host "   git remote add origin YOUR_REPO_URL" -ForegroundColor Gray
    }
}

# Push to GitHub
Write-Host ""
$push = Read-Host "Push to GitHub now? (y/n)"
if ($push -eq "y") {
    Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
    
    # Check if main branch exists
    $currentBranch = git branch --show-current
    if ([string]::IsNullOrWhiteSpace($currentBranch)) {
        git branch -M main
    }
    
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Push failed. Please check your credentials and try again." -ForegroundColor Red
        Write-Host "   You can push manually with: git push -u origin main" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "⏭️  Skipped push. You can push later with:" -ForegroundColor Yellow
    Write-Host "   git push -u origin main" -ForegroundColor Gray
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Connect to your VM: ssh azureuser@YOUR_VM_IP" -ForegroundColor White
Write-Host "2. Pull the code: cd /home/azureuser/rag_pdf_finance && git pull" -ForegroundColor White
Write-Host "3. Restart service: sudo systemctl restart rag-api" -ForegroundColor White
Write-Host "4. Check logs: sudo journalctl -u rag-api -f" -ForegroundColor White
Write-Host ""
Write-Host "📚 See DEPLOYMENT_V4.md for detailed instructions" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Deployment preparation complete!" -ForegroundColor Green

