# Multimodal RAG System - Setup Script for Windows PowerShell
# This script helps you set up and verify the project

Write-Host "🚀 Multimodal RAG System - Setup Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Check prerequisites
Write-Host "📋 Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

$prerequisites = @{
    "Docker" = "docker"
    "Docker Compose" = "docker-compose"
    "Python" = "python"
    "Git" = "git"
}

$allPrerequisitesMet = $true

foreach ($prereq in $prerequisites.GetEnumerator()) {
    $name = $prereq.Key
    $command = $prereq.Value
    
    if (Test-Command $command) {
        Write-Host "✅ $name is installed" -ForegroundColor Green
        
        # Show version
        if ($command -eq "python") {
            $version = (& python --version 2>&1)
            Write-Host "   Version: $version" -ForegroundColor Gray
        }
        elseif ($command -eq "docker") {
            $version = (& docker --version 2>&1)
            Write-Host "   Version: $version" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "❌ $name is NOT installed" -ForegroundColor Red
        $allPrerequisitesMet = $false
        
        # Provide installation guidance
        switch ($command) {
            "docker" {
                Write-Host "   Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
            }
            "python" {
                Write-Host "   Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
            }
            "git" {
                Write-Host "   Install from: https://git-scm.com/download/win" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host ""

if (-not $allPrerequisitesMet) {
    Write-Host "⚠️  Please install missing prerequisites before continuing." -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Check if .env exists
Write-Host "🔧 Checking Configuration..." -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env and add your API keys!" -ForegroundColor Red
    Write-Host "   You need at least ONE of these:" -ForegroundColor Yellow
    Write-Host "   - GOOGLE_API_KEY" -ForegroundColor Yellow
    Write-Host "   - GROQ_API_KEY" -ForegroundColor Yellow
    Write-Host "   - OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "   - HUGGINGFACEHUB_API_TOKEN" -ForegroundColor Yellow
    Write-Host ""
    
    # Ask if user wants to edit now
    $response = Read-Host "Do you want to edit .env now? (y/n)"
    if ($response -eq "y") {
        notepad ".env"
    }
}
else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

Write-Host ""

# Create sample data
Write-Host "📦 Creating Sample Data..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path "samples\text\machine_learning.txt") {
    Write-Host "✅ Sample data already exists" -ForegroundColor Green
}
else {
    Write-Host "📝 Generating sample documents..." -ForegroundColor Yellow
    & python scripts\seed_data.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Sample data created" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Failed to create sample data" -ForegroundColor Red
    }
}

Write-Host ""

# Check if Docker is running
Write-Host "🐳 Checking Docker..." -ForegroundColor Yellow
Write-Host ""

try {
    $null = & docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Docker is not running" -ForegroundColor Red
        Write-Host "   Please start Docker Desktop" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "❌ Docker is not running" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Ask if user wants to start services
Write-Host "🚀 Ready to Start Services" -ForegroundColor Cyan
Write-Host ""
$response = Read-Host "Do you want to start all services now? (y/n)"

if ($response -eq "y") {
    Write-Host ""
    Write-Host "🔄 Starting services with docker-compose..." -ForegroundColor Yellow
    Write-Host ""
    
    & docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Services started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "⏳ Waiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        Write-Host ""
        Write-Host "🔍 Checking service health..." -ForegroundColor Yellow
        Write-Host ""
        
        # Check API health
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/healthz" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ API is healthy" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "⚠️  API is not responding yet" -ForegroundColor Yellow
            Write-Host "   It may need more time to start" -ForegroundColor Gray
        }
        
        # Check Qdrant
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:6333/health" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Qdrant is healthy" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "⚠️  Qdrant is not responding yet" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "📊 Service URLs:" -ForegroundColor Cyan
        Write-Host "   API: http://localhost:8000" -ForegroundColor White
        Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
        Write-Host "   Qdrant: http://localhost:6333/dashboard" -ForegroundColor White
        Write-Host "   Prometheus: http://localhost:9090" -ForegroundColor White
        Write-Host "   Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White
        Write-Host "   Flower: http://localhost:5555" -ForegroundColor White
        Write-Host ""
        
        Write-Host "📝 View logs:" -ForegroundColor Cyan
        Write-Host "   docker-compose logs -f api" -ForegroundColor White
        Write-Host ""
        
        Write-Host "🛑 Stop services:" -ForegroundColor Cyan
        Write-Host "   docker-compose down" -ForegroundColor White
        Write-Host ""
    }
    else {
        Write-Host ""
        Write-Host "❌ Failed to start services" -ForegroundColor Red
        Write-Host "   Check docker-compose logs for errors" -ForegroundColor Yellow
        Write-Host ""
    }
}
else {
    Write-Host ""
    Write-Host "ℹ️  To start services later, run:" -ForegroundColor Cyan
    Write-Host "   docker-compose up -d" -ForegroundColor White
    Write-Host ""
}

Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Edit .env and add your API keys (if not done)" -ForegroundColor White
Write-Host "   2. Implement remaining components from IMPLEMENTATION_GUIDE.md" -ForegroundColor White
Write-Host "   3. Run tests: pytest tests/ -v" -ForegroundColor White
Write-Host "   4. Read README.md for complete documentation" -ForegroundColor White
Write-Host ""

Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
