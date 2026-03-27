Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$requiredFiles = @(
  "platforms/chatgpt/custom-gpt-instructions.md",
  "platforms/chatgpt/README.md",
  "priorities.md",
  "convergence.md",
  "prd-rubric.md",
  "code-rubric.md",
  "discriminator-prompt.md"
)

$requiredInstructionMarkers = @(
  "Step 1: Determine Configuration",
  "Step 2: Generator Pass",
  "Step 3: Discriminator Pass",
  "Step 4: Arbiter Decision",
  "Step 5: Final Output",
  "WEIGHTED_AVERAGE:",
  "HARD_GATE_STATUS:",
  "TOP_ISSUES:",
  "CONVERGENCE:"
)

function Resolve-RepoFile {
  param([string]$RelativePath)
  return Join-Path $repoRoot $RelativePath
}

Write-Host "[1/4] Checking required files..."
$missingFiles = @()
foreach ($file in $requiredFiles) {
  $fullPath = Resolve-RepoFile $file
  if (-not (Test-Path $fullPath)) {
    $missingFiles += $file
  }
}

if ($missingFiles.Count -gt 0) {
  Write-Host "FAIL: Missing required files:" -ForegroundColor Red
  $missingFiles | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
  exit 1
}
Write-Host "PASS: Required files are present." -ForegroundColor Green

Write-Host "[2/4] Checking instruction schema markers..."
$instructionsPath = Resolve-RepoFile "platforms/chatgpt/custom-gpt-instructions.md"
$instructionsContent = Get-Content $instructionsPath -Raw
$missingMarkers = @()
foreach ($marker in $requiredInstructionMarkers) {
  if ($instructionsContent -notmatch [regex]::Escape($marker)) {
    $missingMarkers += $marker
  }
}

if ($missingMarkers.Count -gt 0) {
  Write-Host "FAIL: Missing instruction markers:" -ForegroundColor Red
  $missingMarkers | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
  exit 1
}
Write-Host "PASS: Instruction schema markers found." -ForegroundColor Green

Write-Host "[3/4] Checking README knowledge references..."
$chatgptReadmePath = Resolve-RepoFile "platforms/chatgpt/README.md"
$chatgptReadme = Get-Content $chatgptReadmePath -Raw
$knowledgeFiles = @(
  "priorities.md",
  "convergence.md",
  "prd-rubric.md",
  "code-rubric.md",
  "discriminator-prompt.md"
)

$missingReadmeRefs = @()
foreach ($file in $knowledgeFiles) {
  if ($chatgptReadme -notmatch [regex]::Escape($file)) {
    $missingReadmeRefs += $file
  }
}

if ($missingReadmeRefs.Count -gt 0) {
  Write-Host "FAIL: README is missing knowledge references:" -ForegroundColor Red
  $missingReadmeRefs | ForEach-Object { Write-Host " - $_" -ForegroundColor Red }
  exit 1
}
Write-Host "PASS: README references all required knowledge files." -ForegroundColor Green

Write-Host "[4/4] Creating upload bundle..."
$bundlePath = Resolve-RepoFile "platforms/chatgpt/chatgpt-knowledge-bundle.zip"
if (Test-Path $bundlePath) {
  Remove-Item $bundlePath -Force
}

$bundleFiles = @(
  (Resolve-RepoFile "platforms/chatgpt/custom-gpt-instructions.md"),
  (Resolve-RepoFile "priorities.md"),
  (Resolve-RepoFile "convergence.md"),
  (Resolve-RepoFile "prd-rubric.md"),
  (Resolve-RepoFile "code-rubric.md"),
  (Resolve-RepoFile "discriminator-prompt.md")
)

Compress-Archive -Path $bundleFiles -DestinationPath $bundlePath -Force
$bundle = Get-Item $bundlePath
Write-Host "PASS: Bundle created at $($bundle.FullName) ($($bundle.Length) bytes)." -ForegroundColor Green

Write-Host "Validation complete." -ForegroundColor Green
exit 0