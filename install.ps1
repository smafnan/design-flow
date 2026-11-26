param(
  [ValidateSet('claude', 'codex', 'antigravity')][string]$Agent = 'claude',
  [ValidateSet('user', 'project')][string]$Scope = 'user',
  [string]$Project,
  [string]$SkillsDir,
  [switch]$Replace,
  [switch]$Uninstall,
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$pythonArguments = @((Join-Path $PSScriptRoot 'install.py'), '--agent', $Agent, '--scope', $Scope)
if ($Project) { $pythonArguments += @('--project', $Project) }
if ($SkillsDir) { $pythonArguments += @('--skills-dir', $SkillsDir) }
if ($Replace) { $pythonArguments += '--replace' }
if ($Uninstall) { $pythonArguments += '--uninstall' }
if ($DryRun) { $pythonArguments += '--dry-run' }
if (Get-Command python -ErrorAction SilentlyContinue) {
  & python @pythonArguments
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3 @pythonArguments
} else {
  throw 'Python 3.10 or newer is required.'
}
exit $LASTEXITCODE
