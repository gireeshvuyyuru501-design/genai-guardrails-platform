$ErrorActionPreference = "Stop"

$repoUrl = "https://github.com/gireeshvuyyuru501-design/genai-guardrails-platform.git"

if (-not (Test-Path ".git")) {
    git init
    git branch -M main
}

git add -A
$changes = git status --porcelain

if ($changes) {
    git commit -m "Build standalone GenAI guardrails platform"
}
else {
    Write-Host "Nothing new to commit." -ForegroundColor Yellow
}

$origin = git remote get-url origin 2>$null
if ($LASTEXITCODE -eq 0) {
    git remote set-url origin $repoUrl
}
else {
    git remote add origin $repoUrl
}

git push -u origin main
git status
