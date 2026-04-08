# 🚀 OpenEnv Deployment Setup Script
# Automates GitHub repository setup and deployment

param(
    [string]$GitHubUsername = "dreammast",
    [string]$RepoName = "OpenENV",
    [string]$HFUsername = "dreammast",
    [string]$HFSpaceName = "OpenENV"
)

Write-Host "🚀 OpenEnv Automated Deployment Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed. Please install Git from https://git-scm.com" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git is installed" -ForegroundColor Green

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  Docker not found (optional, for local testing)" -ForegroundColor Yellow
}
else {
    Write-Host "✅ Docker is installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "   GitHub User: $GitHubUsername"
Write-Host "   GitHub Repo: $RepoName"
Write-Host "   HF User: $HFUsername"
Write-Host "   HF Space: $HFSpaceName"
Write-Host ""

# Step 1: Initialize Git
Write-Host "📝 Step 1: Initializing Git repository..." -ForegroundColor Yellow
git init
git add .
git commit -m "🎓 Initial commit: OpenEnv education AI training dashboard"
Write-Host "✅ Git initialized and files committed" -ForegroundColor Green
Write-Host ""

# Step 2: Add GitHub remote
Write-Host "🐙 Step 2: Adding GitHub remote..." -ForegroundColor Yellow
$GitHubUrl = "https://github.com/$GitHubUsername/$RepoName.git"
Write-Host "   Repository URL: $GitHubUrl" -ForegroundColor Cyan

git remote add origin $GitHubUrl
git branch -M main

Write-Host "✅ GitHub remote added" -ForegroundColor Green
Write-Host ""

# Step 3: Test Docker build (optional)
$BuildDocker = Read-Host "🐳 Test Docker build locally? (y/n)"
if ($BuildDocker -eq "y" -or $BuildDocker -eq "Y") {
    Write-Host "📦 Building Docker image..." -ForegroundColor Yellow
    docker build -t openenv:latest .
    if ($?) {
        Write-Host "✅ Docker image built successfully" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Docker build failed (continuing anyway)" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Step 4: Instructions for manual setup
Write-Host "📋 Next Steps (Manual):" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Create GitHub Repository:" -ForegroundColor White
Write-Host "   • Go to: https://github.com/new" -ForegroundColor Gray
Write-Host "   • Name: $RepoName" -ForegroundColor Gray
Write-Host "   • Make it PUBLIC (for GitHub Pages)" -ForegroundColor Gray
Write-Host "   • Click 'Create repository'" -ForegroundColor Gray
Write-Host ""

Write-Host "2️⃣  Push to GitHub:" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""

Write-Host "3️⃣  Create Hugging Face Space:" -ForegroundColor White
Write-Host "   • Go to: https://huggingface.co/spaces" -ForegroundColor Gray
Write-Host "   • Click 'Create new Space'" -ForegroundColor Gray
Write-Host "   • Name: $HFSpaceName" -ForegroundColor Gray
Write-Host "   • SDK: Docker" -ForegroundColor Gray
Write-Host ""

Write-Host "4️⃣  Add GitHub Secrets (for auto-deployment):" -ForegroundColor White
Write-Host "   • Go to: https://github.com/$GitHubUsername/$RepoName/settings/secrets/actions" -ForegroundColor Gray
Write-Host "   • Add HF_TOKEN = <your-api-token>" -ForegroundColor Gray
Write-Host "   • Get token at: https://huggingface.co/settings/tokens" -ForegroundColor Gray
Write-Host ""

Write-Host "5️⃣  Enable GitHub Pages:" -ForegroundColor White
Write-Host "   • Go to: https://github.com/$GitHubUsername/$RepoName/settings/pages" -ForegroundColor Gray
Write-Host "   • Source: GitHub Actions" -ForegroundColor Gray
Write-Host ""

Write-Host "✨ Ready to deploy! Run: git push -u origin main" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Your apps will be at:" -ForegroundColor Cyan
Write-Host "   🤗 HF Spaces: https://huggingface.co/spaces/$HFUsername/$HFSpaceName" -ForegroundColor Gray
Write-Host "   📄 GitHub Pages: https://$GitHubUsername.github.io/$RepoName/" -ForegroundColor Gray
Write-Host ""
