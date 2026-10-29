param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Arguments
)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $env:UV_CACHE_DIR = Join-Path $PSScriptRoot '.work/uv-cache'
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $PSScriptRoot '.work/python'
    $env:TEMP = Join-Path $PSScriptRoot '.work/tmp'
    $env:TMP = $env:TEMP
    New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
    if (-not (Test-Path -LiteralPath 'upstream/o11y-bench/.git')) {
        git clone --config core.autocrlf=false --no-checkout https://github.com/grafana/o11y-bench.git upstream/o11y-bench
        if ($LASTEXITCODE) { throw 'Could not clone o11y-bench' }
    }
    git -C upstream/o11y-bench checkout --detach b66d8cfbbe309d2e03e9a301baea056d9718b71b
    if ($LASTEXITCODE) { throw 'Could not select the pinned benchmark commit' }
    uv sync --locked --python 3.14
    if ($LASTEXITCODE) { throw 'Could not install benchmark dependencies' }
    uv run --no-sync python -m opencluster_bench @Arguments
    if ($LASTEXITCODE) { throw 'Benchmark command failed; inspect its message and artifacts' }
}
finally {
    Pop-Location
}
