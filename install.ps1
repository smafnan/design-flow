# Installs the design-flow skill globally for Claude Code (Windows PowerShell).
param([switch]$Uninstall)
$ErrorActionPreference = "Stop"
$src  = Join-Path $PSScriptRoot "skill\design-flow"
$root = if ($env:CLAUDE_SKILLS_DIR) { $env:CLAUDE_SKILLS_DIR } else { Join-Path $HOME ".claude\skills" }
$dest = Join-Path $root "design-flow"

if ($Uninstall) {
  if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
  Write-Host "Removed $dest"
  exit 0
}

New-Item -ItemType Directory -Force $root | Out-Null
if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
Copy-Item -Recurse $src $dest
Write-Host "Installed design-flow to $dest"
Write-Host "Restart Claude Code, then run: /design-flow <what you want>"
