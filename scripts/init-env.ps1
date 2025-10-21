param(
  [string]$ExamplePath = ".env.example",
  [string]$DestPath = ".env"
)

if (Test-Path $DestPath) {
  Write-Host "$DestPath already exists. Aborting."
  exit 1
}

if (-not (Test-Path $ExamplePath)) {
  Write-Host "Example file $ExamplePath not found."
  exit 1
}

Copy-Item -Path $ExamplePath -Destination $DestPath
Write-Host "Created $DestPath from $ExamplePath. Edit it before running docker compose."
