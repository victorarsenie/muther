# Installs the Jarvis persona into each harness.
#
# The persona is owned here (persona/assistant.md) and copied into the harness's
# identity slot. The memory layer is not involved: it injects facts and the map.
#
#   .\install\persona.ps1                 # Hermes + OpenCode
#   .\install\persona.ps1 -Only hermes
param(
  [ValidateSet('all', 'hermes', 'opencode')]
  [string]$Only = 'all',
  [string]$HermesHome = 'D:\Hermes',
  [string]$OpenCodeAgents = (Join-Path $env:USERPROFILE '.config\opencode\agents')
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$personaPath = Join-Path $repo 'persona\assistant.md'
if (-not (Test-Path $personaPath)) { throw "persona not found: $personaPath" }
$persona = ([IO.File]::ReadAllText($personaPath)).Trim()
$marker = '<!-- managed by jarvis repo: persona/assistant.md -->'

function Backup($path) {
  if (Test-Path $path) {
    $bak = "$path.bak-" + (Get-Date -Format 'yyyyMMdd-HHmmss')
    Copy-Item $path $bak -Force
    Write-Host "  backed up: $bak"
  }
}

if ($Only -in 'all', 'hermes') {
  $soul = Join-Path $HermesHome 'SOUL.md'
  Backup $soul
  [IO.File]::WriteAllText($soul, "$marker`n`n$persona`n", (New-Object System.Text.UTF8Encoding($false)))
  Write-Host ("  hermes: $soul ({0} chars)" -f (Get-Item $soul).Length)
}

if ($Only -in 'all', 'opencode') {
  $agent = Join-Path $OpenCodeAgents 'assistant.md'
  New-Item -ItemType Directory -Force -Path $OpenCodeAgents | Out-Null
  Backup $agent
  $front = @"
---
description: Jarvis — the everyday assistant for this machine. Spoken-friendly. Not the coding agent; hand software work to build.
mode: primary
permissions:
  - action: "*"
    resource: "*"
    effect: allow
  - action: edit
    resource: "*"
    effect: ask
  - action: shell
    resource: "*"
    effect: ask
---
"@
  if (Test-Path $agent) {
    $text = [IO.File]::ReadAllText($agent)
    if ($text -match '(?s)^---\s*\r?\n.*?\r?\n---\s*\r?\n') {
      $front = $Matches[0].TrimEnd()
      $front = [regex]::Replace($front, '(?m)^description:.*$',
        'description: Jarvis - the everyday assistant for this machine. Spoken-friendly. Not the coding agent; hand software work to build.')
    }
  }
  [IO.File]::WriteAllText($agent, "$front`n`n$persona`n", (New-Object System.Text.UTF8Encoding($false)))
  Write-Host ("  opencode: $agent ({0} chars)" -f (Get-Item $agent).Length)
}

Write-Host "done"
