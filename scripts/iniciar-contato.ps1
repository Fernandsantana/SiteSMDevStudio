param([switch]$Enviar, [int]$Porta = 5185, [string]$Python)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$pythonCommand = $Python
if (-not $pythonCommand -and (Test-Path -LiteralPath $bundledPython)) { $pythonCommand = $bundledPython }
if (-not $pythonCommand) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue |
        Where-Object Source -NotLike '*Microsoft\WindowsApps\*' | Select-Object -ExpandProperty Source -First 1
}
if (-not $pythonCommand -and (Get-Command Get-AppxPackage -ErrorAction SilentlyContinue)) {
    $pythonCommand = Get-AppxPackage -Name 'OpenAI.CodexPrimaryRuntime*' |
        Sort-Object Version -Descending | ForEach-Object {
            Join-Path $_.InstallLocation 'dependencies/python/python.exe'
        } | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $pythonCommand) { throw 'Python não encontrado. Informe -Python com o caminho do executável Python 3.11 ou superior.' }
$mode = if ($Enviar) { '--smtp' } else { '--preview' }
& $pythonCommand (Join-Path $projectRoot 'server/contact.py') $mode --port $Porta
